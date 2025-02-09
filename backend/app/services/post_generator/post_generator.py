from typing import Dict, List
import logging
from ..crawlers.keyword_crawler import KeywordCrawler
from .content_analyzer import ContentAnalyzer
from .blog_post_writer import BlogPostWriter
from .quality_checker import QualityChecker
import traceback

logger = logging.getLogger(__name__)

class PostGenerator:
	def __init__(self, crawler: KeywordCrawler):
		self.crawler = crawler
		self.content_analyzer = ContentAnalyzer()
		self.blog_writer = BlogPostWriter()
		self.quality_checker = QualityChecker()

	
	def generate_post(self, keyword: str, search_results: Dict = None) -> Dict:
		"""검색 결과를 바탕으로 고품질 포스트 생성"""
		try:
			# 1. 검색 결과 사용 또는 수집
			if search_results is None:
				search_results = self.crawler.search_with_long_tail(keyword)
			
			# 검색 결과 구조 변환
			materials = {
				'keyword': keyword,
				'blog_results': [],
				'news_results': []
			}
			
			# 결과를 블로그와 뉴스로 분리
			for result in search_results.get('results', []):
				if result.get('source') == 'blog':
					materials['blog_results'].append(result)
				elif result.get('source') == 'news':
					materials['news_results'].append(result)
			
			# 2. 소재 분석
			analyzed_materials = self.content_analyzer.analyze_materials(materials)
			
			# 3. 블로그 포스트 작성
			post = self.blog_writer.create_post(analyzed_materials, keyword)
			
			# 4. 품질 검사
			is_valid, issues = self.quality_checker.validate_post(post)
			
			# 5. 품질 이슈가 있다면 개선
			if not is_valid:
				post = self._improve_post_quality(post, issues, analyzed_materials)
				
			# 6. 최종 검증
			final_valid, final_issues = self.quality_checker.validate_post(post)
			post['validation'] = {
				'is_valid': final_valid,
				'issues': final_issues
			}
			
			return post
			
		except Exception as e:
			logger.error(f"Error in generate_post: {str(e)}")
			logger.error(traceback.format_exc())
			raise
	
	def _improve_post_quality(self, post: Dict, issues: List[str], materials: Dict) -> Dict:
		"""품질 이슈 개선"""
		improved_post = post.copy()
		
		for issue in issues:
			if "글자 수가 부족합니다" in issue:
				# 콘텐츠 보강
				self._expand_content(improved_post, materials)
			elif "전문가 인용구나 통계 자료가 부족합니다" in issue:
				# 전문성 보강
				self._add_expert_content(improved_post, materials)
			elif "키워드 사용 빈도가 낮습니다" in issue:
				# 키워드 밀도 조정
				self._adjust_keyword_density(improved_post, materials)
		
		return improved_post
	
	def _expand_content(self, post: Dict, materials: Dict) -> None:
		"""콘텐츠 양 보강"""
		# 추가 사례 연구 추가
		if materials.get('case_studies'):
			post['main_content'].append({
				'title': '추가 사례 연구',
				'content': self.blog_writer._format_case_studies(materials['case_studies'])
			})
		
		# 트렌드 분석 확장
		if materials.get('trends'):
			post['main_content'].append({
				'title': '시장 트렌드 심층 분석',
				'content': self.blog_writer._format_trends(materials['trends'])
			})
	
	def _add_expert_content(self, post: Dict, materials: Dict) -> None:
		"""전문성 보강"""
		if materials.get('expert_quotes'):
			post['main_content'].append({
				'title': '전문가 인사이트',
				'content': self.blog_writer._format_expert_quotes(materials['expert_quotes'])
			})
	
	def _adjust_keyword_density(self, post: Dict) -> None:
		"""키워드 밀도 조정"""
		keyword = post['meta']['keyword']
		
		# 제목에 키워드 추가
		if keyword not in post['title']:
			post['title'] = f"{keyword} - {post['title']}"
		
		# 각 섹션 첫 문장에 키워드 자연스럽게 추가
		for section in post['main_content']:
			if section['content'] and keyword not in section['content'][:100]:
				section['content'] = f"{keyword}와 관련하여, {section['content']}"
