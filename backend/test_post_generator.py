from app.services.crawlers.keyword_crawler import KeywordCrawler
from app.services.post_generator import PostGenerator
import json

def test_post_generation():
	# 테스트용 뉴스 데이터
	test_data = {
		'news_results': [{
			'title': '中 딥시크에 美 AI 기업 대응 총공세...',
			'content': """[디지털데일리 오병훈기자] 중국이 저비용 AI 모델 '딥시크-알원(DeepSeek-R1, 이하 R1)'을 필두로 미국과 AI 자존심 대결을 펼치기 시작한 가운데, 미국 주요 AI 기업도 각양각색 전략을 앞세워 패권 경쟁 열기를 더하고 있다...""",
			'datetime': '2025.02.08. 오전 10:44',
			'url': 'https://n.news.naver.com/mnews/article/138/0002190511?sid=105'
		}],
		'blog_results': [],
		'main_keyword': 'AI 기업 경쟁'
	}

	# KeywordCrawler Mock
	class MockCrawler:
		def search_with_long_tail(self, keyword):
			return test_data

	# 포스트 생성 테스트
	crawler = MockCrawler()
	generator = PostGenerator(crawler)
	post = generator.generate_post('AI 기업 경쟁')

	# 결과 출력
	print('Generated post structure:')
	print(json.dumps(post, ensure_ascii=False, indent=2))

if __name__ == '__main__':
	test_post_generation()