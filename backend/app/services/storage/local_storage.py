import os
import json
from datetime import datetime
from typing import List, Dict

class LocalStorage:
    def __init__(self, base_dir: str = None):
        """Initialize local storage with base directory"""
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'collected')
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_search_results(self, keyword: str, blog_results: List[Dict], news_results: List[Dict]) -> str:
        """Save search results to a JSON file"""
        # 파일명 생성 (YYYYMMDD_HHMMSS_keyword.json)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{keyword}.json"
        filepath = os.path.join(self.base_dir, filename)

        # 저장할 데이터 구성
        data = {
            'keyword': keyword,
            'timestamp': timestamp,
            'blog_results': blog_results,
            'news_results': news_results
        }

        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return filename

    def get_search_result(self, filename: str) -> Dict:
        """Get search result from a JSON file"""
        filepath = os.path.join(self.base_dir, filename)
        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_search_results(self) -> List[Dict]:
        """List all search results"""
        results = []
        for filename in os.listdir(self.base_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.base_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    results.append({
                        'filename': filename,
                        'keyword': data['keyword'],
                        'timestamp': data['timestamp']
                    })
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
