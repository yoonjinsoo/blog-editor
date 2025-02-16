from typing import Dict, List, Any
from collections import Counter
import re

class FactAnalyzer:
    """추출된 팩트를 분석하고 활용 가능한 형태로 가공하는 클래스"""
    
    def __init__(self):
        self.pattern_cache = {}
        
    def analyze_facts(self, facts: Dict[str, Any]) -> Dict[str, Any]:
        """팩트 분석 및 구조화"""
        analyzed_data = {
            'patterns': self._extract_sentence_patterns(facts),
            'entities': self._analyze_entities(facts),
            'keywords': self._extract_keywords(facts),
            'statistics': self._extract_statistics(facts),
            'templates': self._find_content_templates(facts)
        }
        return analyzed_data
    
    def _extract_sentence_patterns(self, facts: Dict[str, Any]) -> Dict[str, List[str]]:
        """문장 패턴 추출"""
        patterns = {
            'intro': [],
            'main': [],
            'conclusion': []
        }
        
        for sentence in facts.get('sentences', []):
            # 문장 시작 패턴으로 섹션 분류
            if any(starter in sentence for starter in ['안녕하세요', '오늘은', '먼저']):
                patterns['intro'].append(sentence)
            elif any(starter in sentence for starter in ['정리하면', '마지막으로', '결론적으로']):
                patterns['conclusion'].append(sentence)
            else:
                patterns['main'].append(sentence)
                
        return patterns
    
    def _analyze_entities(self, facts: Dict[str, Any]) -> Dict[str, List[str]]:
        """개체명 분석 및 분류"""
        entities = {}
        for entity in facts.get('entities', []):
            entity_type = entity.get('type')
            if entity_type not in entities:
                entities[entity_type] = []
            entities[entity_type].append(entity.get('text'))
        return entities
    
    def _extract_keywords(self, facts: Dict[str, Any]) -> Dict[str, float]:
        """키워드 중요도 분석"""
        keywords = Counter()
        
        # 문장에서 키워드 추출
        for sentence in facts.get('sentences', []):
            words = sentence.split()
            keywords.update(words)
            
        # 정규화된 점수 계산
        total = sum(keywords.values())
        return {word: count/total for word, count in keywords.most_common(20)}
    
    def _extract_statistics(self, facts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """통계 정보 추출"""
        statistics = []
        
        for sentence in facts.get('sentences', []):
            # 숫자가 포함된 문장에서 통계 추출
            if re.search(r'\d+', sentence):
                statistics.append({
                    'text': sentence,
                    'numbers': re.findall(r'\d+(?:[\.,]\d+)?', sentence),
                    'context': self._get_statistical_context(sentence)
                })
                
        return statistics
    
    def _find_content_templates(self, facts: Dict[str, Any]) -> List[Dict[str, str]]:
        """컨텐츠 템플릿 추출"""
        templates = []
        
        # 반복되는 문장 구조 찾기
        sentences = facts.get('sentences', [])
        for i in range(len(sentences)-1):
            if self._is_similar_structure(sentences[i], sentences[i+1]):
                templates.append({
                    'pattern': self._extract_template_pattern(sentences[i]),
                    'example': sentences[i]
                })
                
        return templates
    
    def _get_statistical_context(self, sentence: str) -> str:
        """통계 관련 문맥 추출"""
        contexts = {
            '증가': '상승/증가',
            '감소': '하락/감소',
            '평균': '평균값',
            '비율': '비율/퍼센트'
        }
        
        for key, category in contexts.items():
            if key in sentence:
                return category
        return '기타'
    
    def _is_similar_structure(self, sent1: str, sent2: str) -> bool:
        """문장 구조 유사성 확인"""
        pattern1 = self._get_sentence_pattern(sent1)
        pattern2 = self._get_sentence_pattern(sent2)
        return pattern1 == pattern2
    
    def _get_sentence_pattern(self, sentence: str) -> str:
        """문장의 패턴 추출"""
        if sentence in self.pattern_cache:
            return self.pattern_cache[sentence]
            
        # 문장 패턴 추출 로직
        pattern = re.sub(r'\d+', 'NUM', sentence)
        pattern = re.sub(r'[가-힣]+', 'KOR', pattern)
        pattern = re.sub(r'[a-zA-Z]+', 'ENG', pattern)
        
        self.pattern_cache[sentence] = pattern
        return pattern
    
    def _extract_template_pattern(self, sentence: str) -> str:
        """템플릿 패턴 추출"""
        # 핵심 구조만 남기고 변수 부분을 플레이스홀더로 대체
        pattern = sentence
        pattern = re.sub(r'\d+[가-힣]*', '{NUM}', pattern)
        pattern = re.sub(r'[가-힣]+(?:은|는|이|가|을|를|에|의)', '{TOPIC}', pattern)
        return pattern
