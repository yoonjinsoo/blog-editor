import requests
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentCollector:
    def __init__(self, naver_client_id: str, naver_client_secret: str):
        self.naver_client_id = naver_client_id
        self.naver_client_secret = naver_client_secret
        self.headers = {
            'X-Naver-Client-Id': naver_client_id,
            'X-Naver-Client-Secret': naver_client_secret
        }

    def collect_blog_posts(self, query: str, display: int = 100) -> List[Dict[str, Any]]:
        """네이버 블로그 API를 통해 블로그 포스트를 수집합니다."""
        try:
            url = f"https://openapi.naver.com/v1/search/blog"
            params = {
                'query': query,
                'display': display,
                'sort': 'date'  # 최신순으로 정렬
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            posts = data.get('items', [])
            
            # HTML 태그 제거 및 데이터 정제
            for post in posts:
                post['description'] = BeautifulSoup(post['description'], 'html.parser').get_text()
                post['collected_at'] = datetime.now().isoformat()
            
            return posts
            
        except Exception as e:
            logger.error(f"Error collecting blog posts: {str(e)}")
            return []

    def collect_news_articles(self, query: str, display: int = 100) -> List[Dict[str, Any]]:
        """네이버 뉴스 API를 통해 뉴스 기사를 수집합니다."""
        try:
            url = f"https://openapi.naver.com/v1/search/news"
            params = {
                'query': query,
                'display': display,
                'sort': 'date'  # 최신순으로 정렬
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('items', [])
            
            # HTML 태그 제거 및 데이터 정제
            for article in articles:
                article['description'] = BeautifulSoup(article['description'], 'html.parser').get_text()
                article['collected_at'] = datetime.now().isoformat()
            
            return articles
            
        except Exception as e:
            logger.error(f"Error collecting news articles: {str(e)}")
            return []

    def get_full_content(self, url: str) -> str:
        """URL에서 전체 콘텐츠를 추출합니다."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 메타 태그와 스크립트 제거
            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.decompose()
            
            # 본문 내용 추출
            content = soup.get_text(separator=' ', strip=True)
            return content
            
        except Exception as e:
            logger.error(f"Error extracting full content from {url}: {str(e)}")
            return ""
