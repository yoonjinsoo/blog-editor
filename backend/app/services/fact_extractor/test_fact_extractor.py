import unittest
import json
from pathlib import Path
from .fact_extractor import FactExtractor

class TestFactExtractor(unittest.TestCase):
    def setUp(self):
        self.fact_extractor = FactExtractor()
        self.test_data_path = Path(__file__).parent.parent.parent / 'data' / 'collected'
    
    def test_extract_facts_from_sample(self):
        # 테스트용 샘플 텍스트
        sample_text = """
        쿠팡 퀵플렉스 앱을 다운로드 후 가입했습니다. 안전교육은 2시간 동영상을 시청해야 합니다.
        계약은 9월 25일에 진행되었고, 시급은 15,000원입니다.
        """
        
        facts = self.fact_extractor.extract_facts_with_llm(sample_text)
        
        # 결과 검증
        self.assertIsInstance(facts, list)
        self.assertTrue(len(facts) > 0)
        
        # 각 추출된 사실이 문자열인지 확인
        for fact in facts:
            self.assertIsInstance(fact, str)
            self.assertTrue(len(fact.strip()) > 0)
    
    def test_process_real_search_results(self):
        # 실제 수집된 데이터 파일 찾기
        json_files = list(self.test_data_path.glob('*.json'))
        if not json_files:
            self.skipTest("No JSON test data found")
        
        # 첫 번째 JSON 파일 사용
        with open(json_files[0], 'r', encoding='utf-8') as f:
            search_results = json.load(f)
        
        # 결과 처리
        result = self.fact_extractor.process_search_results(search_results)
        
        # 결과 검증
        self.assertIn('keyword', result)
        self.assertIn('timestamp', result)
        self.assertIn('facts', result)
        self.assertIsInstance(result['facts'], list)
        
        # 각 추출된 사실 검증
        for fact in result['facts']:
            self.assertIsInstance(fact, str)
            self.assertTrue(len(fact.strip()) > 0)

if __name__ == '__main__':
    unittest.main()
