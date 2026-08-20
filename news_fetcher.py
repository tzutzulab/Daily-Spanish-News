"""
新聞獲取模組 - 僅保留 BBC Mundo 穩定來源版本
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
        # 僅保留穩定且可正常抓取的 BBC Mundo RSS 來源
        self.rss_feeds = [
            'https://www.bbc.com/mundo/index.xml',
        ]
    
    def fetch_full_article_text(self, url):
        """透過爬蟲直接抓取網頁的正文內容，確保不是只有摘要"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            response = requests.get(url, headers=headers, timeout=12)
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
        
        for feed_url in self.rss_feeds:
            try:
                logger.info(f"Fetching from {feed_url}")
                feed = feedparser.parse(feed_url, agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
                source_candidates = []
                
                for entry in feed.entries[:5]: # 抓取前 5 篇作為候選池
                    summary = entry.get('summary', '')
                    if len(summary) < 20:
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
        
        # 從候選池中隨機抽出一篇
        if all_candidates:
            selected = random.sample(all_candidates, min(num_articles, len(all_candidates)))
            return selected
            
        return []
