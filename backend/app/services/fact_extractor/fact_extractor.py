import re
from typing import List, Dict

class FactExtractor:
    def __init__(self):
        # 사실성 정보를 나타내는 패턴
        self.fact_patterns = [
            r'\d+[%％]', # 백분율
            r'\d+년', # 연도
            r'\d+월', # 월
            r'\d+일', # 일
            r'약 \d+', # 대략적인 수치
            r'\d+억원', # 금액
            r'\d+만원',
            r'\d+위', # 순위
        ]
        
    def extract_facts(self, text: str) -> List[str]:
        """텍스트에서 사실성 정보를 추출합니다."""
        facts = []
        
        # 문장 단위로 분리
        sentences = text.split('.')
        
        for sentence in sentences:
            # 패턴 매칭으로 사실성 정보 확인
            for pattern in self.fact_patterns:
                matches = re.finditer(pattern, sentence)
                for match in matches:
                    # 매칭된 문장 전체를 컨텍스트로 저장
                    fact_sentence = sentence.strip()
                    if fact_sentence and fact_sentence not in facts:
                        facts.append(fact_sentence)
                        
        return facts

    def process_search_results(self, search_results: Dict) -> Dict:
        """검색 결과에서 사실성 정보를 추출하여 반환합니다."""
        facts = []
        
        # 블로그 검색 결과 처리
        if 'blog_results' in search_results:
            for post in search_results['blog_results']:
                description = post.get('description', '')
                extracted_facts = self.extract_facts(description)
                facts.extend(extracted_facts)
        
        # 뉴스 검색 결과 처리
        if 'news_results' in search_results:
            for news in search_results['news_results']:
                description = news.get('description', '')
                extracted_facts = self.extract_facts(description)
                facts.extend(extracted_facts)
                
        # 중복 제거
        facts = list(set(facts))
        
        # 원본 검색 결과에 사실성 정보 추가
        search_results['extracted_facts'] = facts
        
        return search_results
