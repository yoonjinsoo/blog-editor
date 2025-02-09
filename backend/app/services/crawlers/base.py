from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
	def __init__(self):
		self.headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
			'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
			'Accept-Language': 'ko-KR,ko;q=0.8,en-US;q=0.5,en;q=0.3',
			'Connection': 'keep-alive',
		}
		self.session = requests.Session()
	
	def _get_soup(self, url: str) -> Optional[BeautifulSoup]:
		try:
			response = self.session.get(url, headers=self.headers)
			response.raise_for_status()
			return BeautifulSoup(response.text, 'html.parser')
		except Exception as e:
			logger.error(f"Failed to fetch URL {url}: {str(e)}")
			return None
	
	@abstractmethod
	def get_news_list(self, keyword: str, page: int = 1) -> List[Dict]:
		"""키워드로 뉴스를 검색하는 추상 메서드"""
		pass
	
	@abstractmethod
	def get_blog_list(self, keyword: str, page: int = 1) -> List[Dict]:
		"""키워드로 블로그를 검색하는 추상 메서드"""
		pass
	
	@abstractmethod
	def get_news_content(self, url: str) -> Optional[Dict]:
		"""뉴스 내용을 가져오는 추상 메서드"""
		pass
	
	@abstractmethod
	def get_blog_content(self, url: str) -> Optional[Dict]:
		"""블로그 내용을 가져오는 추상 메서드"""
		pass