import spacy
from typing import List, Dict, Any
import re

class FactExtractor:
    def __init__(self):
        """사실 정보 추출기를 초기화합니다."""
        try:
            self.nlp = spacy.load("ko_core_news_lg")
        except OSError:
            # 모델이 설치되어 있지 않으면 다운로드
            spacy.cli.download("ko_core_news_lg")
            self.nlp = spacy.load("ko_core_news_lg")

    def extract_facts(self, text: str) -> List[Dict[str, Any]]:
        """텍스트에서 사실 정보를 추출합니다."""
        facts = []
        doc = self.nlp(text)
        
        # 문장별로 처리
        for sent in doc.sents:
            # 주관적인 표현이나 감정을 나타내는 단어 필터링
            if self._is_objective(sent.text):
                fact = {
                    'text': sent.text,
                    'confidence_score': self._calculate_confidence(sent),
                    'entities': self._extract_entities(sent),
                    'dates': self._extract_dates(sent.text),
                    'numbers': self._extract_numbers(sent)
                }
                facts.append(fact)
        
        return facts

    def _is_objective(self, text: str) -> bool:
        """문장이 객관적인지 판단합니다."""
        # 주관적 표현을 나타내는 패턴
        subjective_patterns = [
            r'같아요', r'것 같다', r'인 것 같', 
            r'생각', r'느낌', r'아마도',
            r'아닐까', r'지 않을까',
            r'예쁘', r'좋', r'나쁘', r'싫'
        ]
        
        return not any(re.search(pattern, text) for pattern in subjective_patterns)

    def _calculate_confidence(self, sent) -> float:
        """문장의 신뢰도 점수를 계산합니다."""
        # 기본 점수 0.5
        score = 0.5
        
        # 숫자가 포함되어 있으면 점수 상승
        if any(token.like_num for token in sent):
            score += 0.2
            
        # 고유명사가 포함되어 있으면 점수 상승
        if any(token.pos_ == "PROPN" for token in sent):
            score += 0.2
            
        # 날짜/시간 표현이 있으면 점수 상승
        date_patterns = [r'\d{4}년', r'\d{1,2}월', r'\d{1,2}일', r'오늘', r'어제', r'내일']
        if any(re.search(pattern, sent.text) for pattern in date_patterns):
            score += 0.1
            
        return min(score, 1.0)  # 최대 1.0

    def _extract_entities(self, sent) -> List[Dict[str, str]]:
        """문장에서 개체명을 추출합니다."""
        entities = []
        for ent in sent.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
        return entities

    def _extract_dates(self, text: str) -> List[str]:
        """문장에서 날짜 정보를 추출합니다."""
        date_pattern = r'\d{4}년\s*\d{1,2}월\s*\d{1,2}일|\d{4}[\./\-]\d{1,2}[\./\-]\d{1,2}|\d{1,2}월\s*\d{1,2}일'
        return re.findall(date_pattern, text)

    def _extract_numbers(self, sent) -> List[Dict[str, Any]]:
        """문장에서 수치 정보를 추출합니다."""
        numbers = []
        for token in sent:
            if token.like_num:
                # 단위가 있는 경우 함께 추출
                next_token = token.nbor() if token.i + 1 < len(token.doc) else None
                unit = next_token.text if next_token and next_token.pos_ == "NOUN" else None
                
                numbers.append({
                    'value': token.text,
                    'unit': unit
                })
        return numbers

    def process_search_results(self, search_results: Dict[str, Any]) -> Dict[str, Any]:
        """검색 결과에서 사실 정보를 추출합니다."""
        extracted_facts = []
        
        # 블로그 결과 처리
        for item in search_results.get('blog_results', []):
            facts = self.extract_facts(item['description'])
            for fact in facts:
                if fact['confidence_score'] >= 0.7:  # 신뢰도가 높은 정보만 선택
                    extracted_facts.append({
                        'content': fact['text'],
                        'source_type': '블로그',
                        'source_title': item['title'],
                        'confidence': fact['confidence_score'],
                        'categories': self._categorize_fact(fact),
                        'entities': fact['entities'],
                        'dates': fact['dates'],
                        'numbers': fact['numbers']
                    })
        
        # 뉴스 결과 처리
        for item in search_results.get('news_results', []):
            facts = self.extract_facts(item['description'])
            for fact in facts:
                if fact['confidence_score'] >= 0.6:  # 뉴스는 신뢰도 기준을 좀 더 낮게 설정
                    extracted_facts.append({
                        'content': fact['text'],
                        'source_type': '뉴스',
                        'source_title': item['title'],
                        'confidence': fact['confidence_score'],
                        'categories': self._categorize_fact(fact),
                        'entities': fact['entities'],
                        'dates': fact['dates'],
                        'numbers': fact['numbers']
                    })
        
        # 신뢰도 순으로 정렬
        extracted_facts.sort(key=lambda x: x['confidence'], reverse=True)
        
        return {
            'facts': extracted_facts[:10]  # 상위 10개만 반환
        }

    def _categorize_fact(self, fact: Dict[str, Any]) -> List[str]:
        """사실 정보의 카테고리를 결정합니다."""
        categories = []
        text = fact['text'].lower()
        
        # 날짜 정보가 있으면 '시간/날짜' 카테고리 추가
        if fact['dates']:
            categories.append('시간/날짜')
        
        # 수치 정보가 있으면 '수치/통계' 카테고리 추가
        if fact['numbers']:
            categories.append('수치/통계')
        
        # 엔티티 기반 카테고리
        entity_categories = {
            'PERSON': '인물',
            'ORG': '조직',
            'LOC': '장소',
            'PRODUCT': '제품',
            'EVENT': '이벤트'
        }
        
        for entity in fact['entities']:
            if entity['label'] in entity_categories:
                categories.append(entity_categories[entity['label']])
        
        # 내용 기반 카테고리
        content_categories = [
            (r'(개발|출시|발표)', '제품/서비스'),
            (r'(매출|실적|성장|하락|증가|감소)', '경제/비즈니스'),
            (r'(기술|특허|혁신)', '기술'),
            (r'(정책|규제|법|제도)', '정책/제도'),
            (r'(연구|조사|분석)', '연구/분석'),
            (r'(환경|기후|에너지)', '환경'),
            (r'(건강|의료|질병)', '건강/의료'),
            (r'(교육|학습|학교)', '교육'),
            (r'(문화|예술|공연)', '문화/예술')
        ]
        
        for pattern, category in content_categories:
            if re.search(pattern, text):
                categories.append(category)
        
        # 중복 제거
        return list(set(categories))
