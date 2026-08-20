"""
新聞獲取模組 - 西班牙在地媒體來源版本
"""

import feedparser
import logging
import requests
import random
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NewsFetcher:
    def __init__(self):
        # 使用根基於西班牙當地的真實媒體 RSS 來源（如 RTVE 西班牙國家廣播電視台）
        self.rss_feeds = [
            'https://www.rtve.es/rss/noticias_portada.xml',
            'https://www.bbc.com/mundo/index.xml',
        ]
    
    def fetch_full_article_text(self, url):
        """透過爬蟲直接抓取網頁的正文內容，確保不是只有摘要"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                paragraphs = soup.find_all('p')
                full_text_list = []
                for p in paragraphs:
                    text = p.get_text().strip()
                    if len(text) > 40 and not any(kw in text.lower() for kw in ['cookie', 'suscríbete', 'derechos reservados', 'publicidad', 'privacidad', 'aviso legal']):
                        full_text_list.append(text)
                
                if full_text_list:
                    return "\n\n".join(full_text_list[:10])
        except Exception as e:
            logger.error(f"Error scraping full article from {url}: {str(e)}")
        return None

    def get_news(self, num_articles=1):
        all_candidates = []
        
        # 遍歷每一個 RSS 來源，確保每個來源都有公平的機會貢獻候選文章
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url)
                source_candidates = []
                
                for entry in feed.entries[:5]: # 每個來源取前 5 篇
                    summary = entry.get('summary', '')
                    if len(summary) < 30:
                        continue
                    
                    link = entry.get('link', '')
                    title = entry.get('title', '')
                    
                    full_content = self.fetch_full_article_text(link)
                    if not full_content or len(full_content) < len(summary):
                        full_content = summary
                        
                    source_candidates.append({
                        'title': title,
                        'summary': summary,
                        'full_content': full_content,
                        'link': link,
                        'source': feed.feed.get('title', 'News')
                    })
                
                all_candidates.extend(source_candidates)
            except Exception as e:
                logger.error(f"Error fetching RSS {feed_url}: {str(e)}")
                continue
        
        # 如果總候選池有文章，從中完全隨機抽出一篇
        if all_candidates:
            selected = random.sample(all_candidates, min(num_articles, len(all_candidates)))
            return selected
            
        return []
