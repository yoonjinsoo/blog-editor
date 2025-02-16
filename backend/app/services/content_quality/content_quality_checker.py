from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re

@dataclass
class QualityMetrics:
    """컨텐츠 품질 지표"""
    readability_score: float    # 가독성 점수 (0-1)
    grammar_score: float        # 문법 점수 (0-1)
    spelling_score: float       # 맞춤법 점수 (0-1)
    keyword_density: float      # 키워드 밀도 (0-1)
    avg_sentence_length: float  # 평균 문장 길이
    issues: List[Dict[str, Any]]  # 발견된 문제점들
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'readability_score': self.readability_score,
            'grammar_score': self.grammar_score,
            'spelling_score': self.spelling_score,
            'keyword_density': self.keyword_density,
            'avg_sentence_length': self.avg_sentence_length,
            'issues': self.issues
        }

@dataclass
class QualityCheckResult:
    """품질 검사 결과"""
    overall_score: float        # 전체 점수 (0-1)
    metrics: QualityMetrics     # 세부 지표
    suggestions: List[str]      # 개선 제안
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'overall_score': self.overall_score,
            'metrics': self.metrics.to_dict(),
            'suggestions': self.suggestions
        }

class ContentQualityChecker:
    """컨텐츠 품질 검사기"""
    
    def __init__(self):
        # 맞춤법 패턴 (예시)
        self.spelling_patterns = {
            r'되여': '되어',
            r'했슴니다': '했습니다',
            r'봄니다': '봅니다'
        }
        
        # 문법 패턴 (예시)
        self.grammar_patterns = {
            r'\s+을/를\s+': ' ',  # 불필요한 조사
            r'\s+이/가\s+': ' '   # 불필요한 조사
        }
        
        # 가독성 기준
        self.readability_criteria = {
            'max_sentence_length': 50,  # 최대 문장 길이
            'max_paragraph_length': 200,  # 최대 문단 길이
            'optimal_keyword_density': 0.02  # 최적 키워드 밀도 (2%)
        }
        
    def check_content(self, content: str, keywords: List[str]) -> QualityCheckResult:
        """컨텐츠 품질 검사"""
        # 1. 맞춤법 검사
        spelling_issues = self._check_spelling(content)
        spelling_score = self._calculate_spelling_score(content, spelling_issues)
        
        # 2. 문법 검사
        grammar_issues = self._check_grammar(content)
        grammar_score = self._calculate_grammar_score(content, grammar_issues)
        
        # 3. 가독성 검사
        readability_metrics = self._check_readability(content)
        readability_score = self._calculate_readability_score(readability_metrics)
        
        # 4. 키워드 밀도 검사
        keyword_density = self._calculate_keyword_density(content, keywords)
        
        # 5. 전체 메트릭스 생성
        metrics = QualityMetrics(
            readability_score=readability_score,
            grammar_score=grammar_score,
            spelling_score=spelling_score,
            keyword_density=keyword_density,
            avg_sentence_length=readability_metrics['avg_sentence_length'],
            issues=spelling_issues + grammar_issues
        )
        
        # 6. 개선 제안 생성
        suggestions = self._generate_suggestions(metrics)
        
        # 7. 전체 점수 계산
        overall_score = self._calculate_overall_score(metrics)
        
        return QualityCheckResult(
            overall_score=overall_score,
            metrics=metrics,
            suggestions=suggestions
        )
        
    def _check_spelling(self, content: str) -> List[Dict[str, Any]]:
        """맞춤법 검사"""
        issues = []
        
        for pattern, correction in self.spelling_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append({
                    'type': 'spelling',
                    'position': match.start(),
                    'text': match.group(),
                    'suggestion': correction
                })
                
        return issues
        
    def _check_grammar(self, content: str) -> List[Dict[str, Any]]:
        """문법 검사"""
        issues = []
        
        for pattern, correction in self.grammar_patterns.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                issues.append({
                    'type': 'grammar',
                    'position': match.start(),
                    'text': match.group(),
                    'suggestion': correction
                })
                
        return issues
        
    def _check_readability(self, content: str) -> Dict[str, float]:
        """가독성 검사"""
        # 문장 분리
        sentences = re.split(r'[.!?]\s+', content)
        
        # 문단 분리
        paragraphs = content.split('\n\n')
        
        # 메트릭스 계산
        metrics = {
            'avg_sentence_length': sum(len(s) for s in sentences) / len(sentences),
            'avg_paragraph_length': sum(len(p) for p in paragraphs) / len(paragraphs),
            'long_sentences': sum(1 for s in sentences if len(s) > self.readability_criteria['max_sentence_length']),
            'long_paragraphs': sum(1 for p in paragraphs if len(p) > self.readability_criteria['max_paragraph_length'])
        }
        
        return metrics
        
    def _calculate_keyword_density(self, content: str, keywords: List[str]) -> float:
        """키워드 밀도 계산"""
        total_words = len(content.split())
        keyword_count = 0
        
        for keyword in keywords:
            keyword_count += len(re.findall(rf'\b{keyword}\b', content, re.I))
            
        return keyword_count / total_words if total_words > 0 else 0
        
    def _calculate_spelling_score(self, content: str, issues: List[Dict[str, Any]]) -> float:
        """맞춤법 점수 계산"""
        total_words = len(content.split())
        error_count = len(issues)
        
        return 1 - (error_count / total_words) if total_words > 0 else 0
        
    def _calculate_grammar_score(self, content: str, issues: List[Dict[str, Any]]) -> float:
        """문법 점수 계산"""
        total_sentences = len(re.split(r'[.!?]\s+', content))
        error_count = len(issues)
        
        return 1 - (error_count / total_sentences) if total_sentences > 0 else 0
        
    def _calculate_readability_score(self, metrics: Dict[str, float]) -> float:
        """가독성 점수 계산"""
        scores = []
        
        # 1. 문장 길이 점수
        if metrics['avg_sentence_length'] <= self.readability_criteria['max_sentence_length']:
            scores.append(1.0)
        else:
            scores.append(0.5)
            
        # 2. 문단 길이 점수
        if metrics['avg_paragraph_length'] <= self.readability_criteria['max_paragraph_length']:
            scores.append(1.0)
        else:
            scores.append(0.5)
            
        # 3. 긴 문장 비율 점수
        long_sentence_ratio = metrics['long_sentences'] / (metrics['avg_sentence_length'] or 1)
        scores.append(1 - long_sentence_ratio)
        
        return sum(scores) / len(scores)
        
    def _calculate_overall_score(self, metrics: QualityMetrics) -> float:
        """전체 점수 계산"""
        weights = {
            'readability': 0.3,
            'grammar': 0.3,
            'spelling': 0.3,
            'keyword_density': 0.1
        }
        
        score = (
            metrics.readability_score * weights['readability'] +
            metrics.grammar_score * weights['grammar'] +
            metrics.spelling_score * weights['spelling'] +
            (1 - abs(metrics.keyword_density - self.readability_criteria['optimal_keyword_density']) * 10) * weights['keyword_density']
        )
        
        return min(max(score, 0), 1)  # 0-1 범위로 제한
        
    def _generate_suggestions(self, metrics: QualityMetrics) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 1. 맞춤법 관련 제안
        if metrics.spelling_score < 0.9:
            suggestions.append("맞춤법 오류를 수정해주세요.")
            
        # 2. 문법 관련 제안
        if metrics.grammar_score < 0.9:
            suggestions.append("문법 오류를 수정해주세요.")
            
        # 3. 가독성 관련 제안
        if metrics.readability_score < 0.8:
            if metrics.avg_sentence_length > self.readability_criteria['max_sentence_length']:
                suggestions.append(f"문장의 길이가 너무 깁니다. {self.readability_criteria['max_sentence_length']}자 이내로 줄여보세요.")
                
        # 4. 키워드 밀도 관련 제안
        optimal_density = self.readability_criteria['optimal_keyword_density']
        if metrics.keyword_density < optimal_density * 0.5:
            suggestions.append("키워드 사용 빈도가 너무 낮습니다.")
        elif metrics.keyword_density > optimal_density * 2:
            suggestions.append("키워드가 너무 자주 사용되었습니다.")
            
        return suggestions
