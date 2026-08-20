"""
西班牙語新聞每日整理器 - 重新建構版
"""

import os
import sys
import schedule
import time
import logging
from dotenv import load_dotenv

from news_fetcher import NewsFetcher
from email_sender import EmailSender

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpanishNewsDailyService:
    def __init__(self):
        self.sender_email = os.getenv('GMAIL_ADDRESS')
        self.sender_password = os.getenv('GMAIL_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')
        
        if not all([self.sender_email, self.sender_password, self.recipient_email]):
            raise ValueError("Missing required environment variables in .env file.")
        
        self.news_fetcher = NewsFetcher()
        self.email_sender = EmailSender(self.sender_email, self.sender_password)
    
    def send_daily_news(self):
        logger.info("Starting daily news task...")
        try:
            articles, vocabulary_list = self.news_fetcher.get_news(num_articles=1)
            if not articles:
                logger.warning("No articles found!")
                return False
            
            success = self.email_sender.send_email(self.recipient_email, articles, vocabulary_list)
            return success
        except Exception as e:
            logger.error(f"Error in send_daily_news: {str(e)}")
            return False
    
    def start_scheduler(self):
        logger.info("Service started, scheduled daily at 08:00")
        schedule.every().day.at("08:00").do(self.send_daily_news)
        while True:
            schedule.run_pending()
            time.sleep(60)
    
    def run_once(self):
        logger.info("Running test execution...")
        self.send_daily_news()

def main():
    try:
        service = SpanishNewsDailyService()
        if len(sys.argv) > 1 and sys.argv[1] == 'test':
            service.run_once()
        else:
            service.start_scheduler()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
