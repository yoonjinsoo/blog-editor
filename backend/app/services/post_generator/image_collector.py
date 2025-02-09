from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
import logging
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageCollector:
	def __init__(self, client_id: str = None, client_secret: str = None):
		self.headers = {
			'X-Naver-Client-Id': client_id,
			'X-Naver-Client-Secret': client_secret
		} if client_id and client_secret else None
		
		# 이미지 저장 경로
		self.image_dir = Path(__file__).parent.parent.parent.parent / 'static' / 'images'
		self.image_dir.mkdir(parents=True, exist_ok=True)
	
	def collect_images(self, keyword: str, section_type: str, count: int = 3) -> List[Dict]:
		"""키워드와 섹션 타입에 맞는 이미지 수집"""
		search_keyword = self._generate_search_keyword(keyword, section_type)
		
		try:
			# 네이버 이미지 검색 API 호출
			url = "https://openapi.naver.com/v1/search/image"
			params = {
				'query': search_keyword,
				'display': count * 2,  # 여유있게 검색
				'filter': 'large',  # 큰 이미지만
				'sort': 'sim'  # 정확도순
			}
			
			response = requests.get(url, headers=self.headers, params=params)
			response.raise_for_status()
			
			images = []
			for item in response.json().get('items', [])[:count]:
				image_info = self._download_and_process_image(item['link'], keyword, section_type)
				if image_info:
					images.append(image_info)
			
			return images
			
		except Exception as e:
			logger.error(f"이미지 수집 중 오류 발생: {str(e)}")
			return []
	
	def _generate_search_keyword(self, keyword: str, section_type: str) -> str:
		"""섹션 타입에 맞는 검색 키워드 생성"""
		if section_type == 'intro':
			return f"{keyword} 대표 이미지"
		elif section_type == 'background':
			return f"{keyword} 통계 차트"
		elif section_type == 'methods':
			return f"{keyword} 방법 설명"
		elif section_type == 'features':
			return f"{keyword} 특징"
		else:
			return keyword
	
	def _download_and_process_image(self, image_url: str, keyword: str, section_type: str) -> Optional[Dict]:
		"""이미지 다운로드 및 처리"""
		try:
			response = requests.get(image_url)
			response.raise_for_status()
			
			# 파일명 생성
			file_name = f"{keyword}_{section_type}_{len(os.listdir(self.image_dir))}.jpg"
			file_path = self.image_dir / file_name
			
			# 이미지 저장
			with open(file_path, 'wb') as f:
				f.write(response.content)
			
			# 이미지 정보 반환
			return {
				'file_name': file_name,
				'file_path': str(file_path),
				'url': image_url,
				'alt_text': self._generate_alt_text(keyword, section_type),
				'section_type': section_type
			}
			
		except Exception as e:
			logger.error(f"이미지 다운로드 중 오류 발생: {str(e)}")
			return None
	
	def _generate_alt_text(self, keyword: str, section_type: str) -> str:
		"""SEO 최적화된 이미지 대체 텍스트 생성"""
		if section_type == 'intro':
			return f"{keyword} 소개 이미지"
		elif section_type == 'background':
			return f"{keyword} 관련 통계 및 현황"
		elif section_type == 'methods':
			return f"{keyword} 방법 설명 이미지"
		elif section_type == 'features':
			return f"{keyword} 주요 특징 이미지"
		else:
			return f"{keyword} 관련 이미지"