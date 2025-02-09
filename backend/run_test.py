import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

from app.services.crawlers.keyword_crawler import KeywordCrawler
from app.services.post_generator import PostGenerator
import json

def test_post_generation():
	# 테스트용 뉴스 데이터
	test_data = {
		'news_results': [{
			'title': '中 딥시크에 美 AI 기업 대응 총공세...',
			'content': """[디지털데일리 오병훈기자] 중국이 저비용 AI 모델 '딥시크-알원(DeepSeek-R1, 이하 R1)'을 필두로 미국과 AI 자존심 대결을 펼치기 시작한 가운데, 미국 주요 AI 기업도 각양각색 전략을 앞세워 패권 경쟁 열기를 더하고 있다. R1이 '비용효율'을 강조하며 마케팅에 나선 만큼 미국 진영 기업에서도 신규 모델을 선보이면서 '가격 대비 성능' 키워드를 강조하고 나선 모습이다.

샘 올트먼 오픈AI CEO는 "AI 개발에서 안정성과 효율성이 가장 중요하다"라고 말했다. 앤스로픽 연구팀은 "자동화된 탈옥 방지 평가에서도 헌법적 분류기는 강력한 방어력을 보였다"고 전했다.

오픈AI와 구글은 비슷한 딥시크 R1 파장이 본격화된 이후 연속적으로 신규 모델 출시 소식을 전했다. 먼저 오픈AI에서는 고급추론 모델 'o1(오원)'의 후속 모델인 'o3-mini(오쓰리-미니)'를 출시했다.

시스코 연구진은 "딥시크 R1은 100% 공격 성공률을 보였다"고 전했다. 같은 기준으로 실험했을 때 메타의 '라마-3.1-405B'는 96%, 오픈AI 'GPT-4o'는 86%, 구글 '제미나이-1.5-프로'는 64%, 앤스로픽 '클로드-3.5-소넷'은 36% 성공률을 보였다는 것이 시스코 설명이다.""",
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