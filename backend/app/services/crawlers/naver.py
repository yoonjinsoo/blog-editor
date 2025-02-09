from .base import BaseCrawler
from typing import Dict, List, Optional
from datetime import datetime
import re

class NaverNewsCrawler(BaseCrawler):
	def get_news_list(self, keyword: str, page: int = 1) -> List[Dict]:
		"""Fetch news articles from Naver News search."""
		start = (page - 1) * 10 + 1
		url = f"https://search.naver.com/search.naver?where=news&query={keyword}&start={start}"
		soup = self._get_soup(url)
		if not soup:
			return []
		
		news_list = []
		for article in soup.select("div.news_wrap.api_ani_send"):
			try:
				title = article.select_one("a.news_tit").text
				url = article.select_one("a.news_tit")["href"]
				news_list.append({
					'title': title,
					'url': url
				})
			except Exception:
				continue
		return news_list

	def get_blog_list(self, keyword: str, page: int = 1) -> List[Dict]:
		"""Fetch blog posts from Naver Blog search."""
		start = (page - 1) * 10 + 1
		url = f"https://search.naver.com/search.naver?where=blog&query={keyword}&start={start}"
		soup = self._get_soup(url)
		if not soup:
			return []
		
		blog_list = []
		for post in soup.select("div.total_wrap.api_ani_send"):
			try:
				title_elem = post.select_one("a.api_txt_lines.total_tit")
				if title_elem:
					title = title_elem.text.strip()
					url = title_elem["href"]
					blog_list.append({
						'title': title,
						'url': url
					})
			except Exception as e:
				continue
		return blog_list

	def get_news_content(self, url: str) -> Optional[Dict]:
		"""Fetch and parse the content of a Naver news article."""
		soup = self._get_soup(url)
		if not soup:
			return None
		
		try:
			# Handle both Naver News and redirected news sites
			if "news.naver.com" in url:
				title = soup.select_one("#title_area")
				content = soup.select_one("#dic_area")
				date_str = soup.select_one(".media_end_head_info_datestamp_time")
				
				if not all([title, content, date_str]):
					return None
				
				title = title.text.strip()
				content = content.text.strip()
				date_str = date_str.get("data-date-time") or date_str.text.strip()
				
				return {
					'title': title,
					'content': content,
					'datetime': date_str,
					'url': url
				}
			return None
		except Exception:
			return None

	def get_blog_content(self, url: str) -> Optional[Dict]:
		"""Fetch and parse the content of a Naver blog post."""
		if "blog.naver.com" not in url:
			return None
			
		soup = self._get_soup(url)
		if not soup:
			return None
		
		try:
			iframe = soup.select_one("#mainFrame")
			if iframe:
				blog_url = f"https://blog.naver.com{iframe['src']}"
				soup = self._get_soup(blog_url)
				if not soup:
					return None
			
			title = soup.select_one(".se-title-text")
			content = soup.select_one(".se-main-container")
			date = soup.select_one(".se-date")
			
			if not all([title, content, date]):
				return None
				
			return {
				'title': title.text.strip(),
				'content': content.text.strip(),
				'datetime': date.text.strip(),
				'url': url
			}
		except Exception:
			return None