"""
新聞獲取模組 - 簡化穩定版本
"""

import feedparser
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        self.rss_feeds = [
            'https://feeds.elpais.com/elpais/portada',
            'https://www.bbc.com/mundo/index.xml',
        ]
    
    def fetch_from_rss(self, num_articles=1):
        articles = []
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:3]:
                    summary = entry.get('summary', '')
                    if len(summary) < 100:
                        continue
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': summary[:300] + '...',
                        'link': entry.get('link', ''),
                        'source': feed.feed.get('title', 'News')
                    })
                    if len(articles) >= num_articles:
                        return articles
            except Exception as e:
                logger.error(f"Error fetching RSS: {str(e)}")
                continue
        return articles
    
    def get_news(self, num_articles=1):
        articles = self.fetch_from_rss(num_articles)
        # 固定提供幾個基礎單字預習，確保穩定
        vocabulary_list = [
            ('gobierno', '政府', 'El gobierno anunció nuevas medidas.'),
            ('desarrollo', '發展', 'Buscan el desarrollo sostenible del país.'),
            ('problema', '問題', 'Es un problema complejo de resolver.')
        ]
        return articles, vocabulary_list
