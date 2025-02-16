from typing import Dict, List, Any
from collections import Counter
import re
from dataclasses import dataclass

@dataclass
class AnalyzedSentence:
    """분석된 문장 정보를 담는 클래스"""
    text: str
    quality_score: float
    has_statistics: bool
    has_example: bool
    keywords: List[str]
    sentiment: str  # 'objective', 'subjective'
    length: int
    structure_score: float  # 문장 구조 완성도
    sentence_type: str = 'core'  # 'hook', 'core', 'detail', 'example', 'conclusion'

class SentenceAnalyzer:
    """추출된 사실 문장을 분석하고 품질을 평가하는 클래스"""
    
    def __init__(self):
        self.min_sentence_length = 5  # 최소 길이 완화
        self.max_sentence_length = 200  # 최대 길이 증가
        self.structure_patterns = [
            r'^[가-힣]+.*[다요]$',  # 기본 문장 구조 완화
            r'.*[을를].*[다요]$',  # 목적어가 있는 구조
            r'.*[에서].*[다요]$',  # 장소/시간 표현이 있는 구조
        ]
        
    def analyze_sentences(self, sentences: List[str]) -> List[AnalyzedSentence]:
        """문장들을 분석하여 품질 평가"""
        analyzed_sentences = []
        
        for sentence in sentences:
            if self._is_valid_sentence(sentence):
                analyzed = self._analyze_single_sentence(sentence)
                analyzed_sentences.append(analyzed)
                
        return analyzed_sentences
    
    def filter_quality_sentences(self, analyzed_sentences: List[AnalyzedSentence], 
                               min_quality_score: float = 0.6) -> List[AnalyzedSentence]:
        """품질 기준을 충족하는 문장만 필터링"""
        return [
            sent for sent in analyzed_sentences 
            if sent.quality_score >= min_quality_score
        ]
    
    def _analyze_single_sentence(self, sentence: str) -> AnalyzedSentence:
        """개별 문장 분석"""
        # 1. 기본 정보 추출
        length = len(sentence)
        keywords = self._extract_keywords(sentence)
        
        # 2. 통계 포함 여부 확인
        has_statistics = bool(re.search(r'\d+(?:[.,%]\d+)?', sentence))
        
        # 3. 예시 포함 여부 확인
        has_example = any(marker in sentence for marker in ['예를 들어', '예시', '사례'])
        
        # 4. 문장 구조 점수 계산
        structure_score = self._calculate_structure_score(sentence)
        
        # 5. 감성 분석 (객관/주관)
        sentiment = self._analyze_sentiment(sentence)
        
        # 6. 종합 품질 점수 계산
        quality_score = self._calculate_quality_score(
            length=length,
            has_stats=has_statistics,
            has_example=has_example,
            structure_score=structure_score,
            keyword_count=len(keywords)
        )
        
        return AnalyzedSentence(
            text=sentence,
            quality_score=quality_score,
            has_statistics=has_statistics,
            has_example=has_example,
            keywords=keywords,
            sentiment=sentiment,
            length=length,
            structure_score=structure_score,
            sentence_type='fact'
        )
    
    def _is_valid_sentence(self, sentence: str) -> bool:
        """문장의 기본 유효성 검사"""
        if not sentence:
            return False
            
        # 길이 검사
        if not (self.min_sentence_length <= len(sentence) <= self.max_sentence_length):
            return False
            
        # 문장 종결 검사
        if not sentence[-1] in ['다', '요', '죠', '까']:
            return False
            
        return True
    
    def _extract_keywords(self, sentence: str) -> List[str]:
        """문장에서 키워드 추출"""
        # 조사 제거
        text = re.sub(r'[은는이가을를에서의로]([ ]|$)', ' ', sentence)
        
        # 단어 추출
        words = text.split()
        
        # 2글자 이상의 명사만 선택
        keywords = [w for w in words if len(w) >= 2]
        
        return keywords
    
    def _calculate_structure_score(self, sentence: str) -> float:
        """문장 구조 완성도 점수 계산"""
        score = 0.0
        
        # 기본 문장 구조 패턴 매칭
        for pattern in self.structure_patterns:
            if re.match(pattern, sentence):
                score += 0.3
                break
        
        # 주어 포함 여부
        if re.search(r'[가-힣]+[은는이가]', sentence):
            score += 0.3
            
        # 서술어 포함 여부
        if re.search(r'[가-힣]+[다요]$', sentence):
            score += 0.4
            
        return min(1.0, score)
    
    def _analyze_sentiment(self, sentence: str) -> str:
        """문장의 객관성/주관성 분석"""
        subjective_markers = ['것 같', '보이', '생각하', '느끼']
        
        for marker in subjective_markers:
            if marker in sentence:
                return 'subjective'
        
        return 'objective'
    
    def _calculate_quality_score(self, length: int, has_stats: bool, 
                               has_example: bool, structure_score: float,
                               keyword_count: int) -> float:
        """종합 품질 점수 계산"""
        score = 0.0
        
        # 1. 길이 점수 (0.2)
        length_score = 0.2 * (1.0 - abs(50 - length) / 50)  # 50자 기준
        score += length_score
        
        # 2. 통계 포함 점수 (0.2)
        if has_stats:
            score += 0.2
            
        # 3. 예시 포함 점수 (0.1)
        if has_example:
            score += 0.1
            
        # 4. 구조 점수 (0.3)
        score += 0.3 * structure_score
        
        # 5. 키워드 점수 (0.2)
        keyword_score = 0.2 * min(1.0, keyword_count / 3)  # 3개 키워드 기준
        score += keyword_score
        
        return min(1.0, score)
