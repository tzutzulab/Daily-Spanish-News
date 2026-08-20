"""
新聞獲取模組 - 完整文章內容獲取版本
"""

import feedparser
import logging
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.rss_feeds = [
            'https://feeds.elpais.com/elpais/portada',
            'https://www.bbc.com/mundo/index.xml',
        ]
    
    def fetch_full_article_text(self, url):
        """透過爬蟲直接抓取網頁的正文內容，確保不是只有摘要"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 針對常見新聞網站（El País, BBC Mundo 等）提取段落
                paragraphs = soup.find_all('p')
                full_text_list = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    # 過濾掉太短或無關的段落
                    if len(text) > 40 and not any(kw in text.lower() for kw in ['cookie', 'suscríbete', 'derechos reservados', 'publicidad']):
                        full_text_list.append(text)
                
                if full_text_list:
                    return "\n\n".join(full_text_list[:10]) # 取前 10 個核心段落
        except Exception as e:
            logger.error(f"Error scraping full article from {url}: {str(e)}")
        return None

    def get_news(self, num_articles=1):
        articles = []
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    summary = entry.get('summary', '')
                    if len(summary) < 50:
                        continue
                    
                    link = entry.get('link', '')
                    title = entry.get('title', '')
                    
                    # 嘗試抓取完整內文
                    full_content = self.fetch_full_article_text(link)
                    if not full_content or len(full_content) < len(summary):
                        full_content = summary # 抓不到才退回 RSS 摘要
                        
                    articles.append({
                        'title': title,
                        'summary': summary,
                        'full_content': full_content,
                        'link': link,
                        'source': feed.feed.get('title', 'News')
                    })
                    if len(articles) >= num_articles:
                        return articles
            except Exception as e:
                logger.error(f"Error fetching RSS: {str(e)}")
                continue
        return articles
