"""
新聞獲取模組 - 移除單字庫版本
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
                    if len(summary) < 50:
                        continue
                    
                    full_content = entry.get('content', [{'value': summary}])[0].get('value', summary)
                    if len(full_content) < len(summary):
                        full_content = summary
                        
                    articles.append({
                        'title': entry.get('title', ''),
                        'summary': summary,
                        'full_content': full_content,
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
        return articles
