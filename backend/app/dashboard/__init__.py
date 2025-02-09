from flask import Flask, render_template, request, jsonify
from ..services.crawlers.keyword_crawler import KeywordCrawler
from ..services.post_generator.post_generator import PostGenerator
from ..services.fact_extractor import FactExtractor
import os
import logging
import traceback

# Configure root logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static'),
                static_url_path='/static')
    app.config['SECRET_KEY'] = 'dev'
    
    client_id = "O61cc1jqWc2kZVIhqoM2"
    client_secret = "0XXLaAa4FY"
    
    # 크롤러와 포스트 생성기 초기화
    crawler = KeywordCrawler(
        client_id=client_id,
        client_secret=client_secret
    )
    post_generator = PostGenerator(crawler=crawler)
    
    # 사실성 정보 추출기 초기화
    fact_extractor = FactExtractor()

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/search', methods=['POST'])
    def search():
        try:
            keyword = request.form.get('keyword')
            logger.debug(f"Received search request with keyword: {keyword}")
            
            if not keyword:
                logger.warning("No keyword provided in search request")
                return jsonify({'error': '키워드를 입력해주세요'})
            
            # 검색 결과 가져오기
            logger.debug("Calling crawler.search_with_long_tail...")
            search_results = crawler.search_with_long_tail(keyword)
            logger.debug(f"Search results received: {search_results}")
            
            if not search_results or not search_results.get('results'):
                logger.warning(f"No results found for keyword: {keyword}")
                return jsonify({'error': '검색 결과를 찾을 수 없습니다'})
            
            # 검색 결과 반환
            return jsonify({
                'blog_results': search_results['results'],  # 블로그와 뉴스 결과 모두 포함
                'intent': search_results['intent'],
                'main_keyword': search_results['main_keyword'],
                'search_keywords': search_results['search_keywords']
            })
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error during search: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': f'검색 중 오류가 발생했습니다: {error_msg}'}), 500

    @app.route('/generate_post', methods=['POST'])
    def generate_post():
        try:
            data = request.get_json()
            keyword = data.get('keyword')
            if not keyword:
                return jsonify({'error': '키워드를 입력해주세요'})
            
            # 포스트 생성
            post_data = post_generator.generate_post(keyword)
            return jsonify(post_data)
        except Exception as e:
            logger.error(f"Error in generate_post endpoint: {str(e)}", exc_info=True)
            return jsonify({'error': f'포스트 생성 중 오류가 발생했습니다: {str(e)}'}), 500

    return app
