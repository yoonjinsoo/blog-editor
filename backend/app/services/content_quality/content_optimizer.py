from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from collections import Counter

@dataclass
class SEOMetrics:
    """SEO 지표"""
    keyword_density: float          # 키워드 밀도
    heading_score: float           # 제목 최적화 점수
    meta_score: float             # 메타 정보 점수
    readability_score: float      # 가독성 점수
    internal_link_score: float    # 내부 링크 점수
    
    def to_dict(self) -> Dict[str, float]:
        """딕셔너리로 변환"""
        return {
            'keyword_density': self.keyword_density,
            'heading_score': self.heading_score,
            'meta_score': self.meta_score,
            'readability_score': self.readability_score,
            'internal_link_score': self.internal_link_score
        }

@dataclass
class OptimizationResult:
    """최적화 결과"""
    optimized_content: str        # 최적화된 컨텐츠
    optimized_meta: Dict[str, Any]  # 최적화된 메타 정보
    metrics: SEOMetrics           # SEO 지표
    suggestions: List[str]        # 개선 제안
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'optimized_content': self.optimized_content,
            'optimized_meta': self.optimized_meta,
            'metrics': self.metrics.to_dict(),
            'suggestions': self.suggestions
        }

class ContentOptimizer:
    """컨텐츠 SEO 최적화기"""
    
    def __init__(self):
        self.optimal_metrics = {
            'keyword_density': 0.02,  # 2%
            'min_headings': 3,        # 최소 제목 수
            'max_meta_length': 160,   # 메타 설명 최대 길이
            'optimal_paragraph_length': 300  # 최적 문단 길이
        }
        
        self.heading_patterns = {
            'h1': r'<h1>(.*?)</h1>',
            'h2': r'<h2>(.*?)</h2>',
            'h3': r'<h3>(.*?)</h3>'
        }
        
    def optimize_content(self,
                        content: str,
                        meta: Dict[str, Any],
                        keywords: List[str]) -> OptimizationResult:
        """컨텐츠 SEO 최적화"""
        # 1. 키워드 밀도 최적화
        optimized_content, keyword_metrics = self._optimize_keyword_density(
            content,
            keywords
        )
        
        # 2. 제목 구조 최적화
        optimized_content, heading_metrics = self._optimize_headings(
            optimized_content,
            keywords
        )
        
        # 3. 메타 정보 최적화
        optimized_meta, meta_metrics = self._optimize_meta(
            meta,
            keywords
        )
        
        # 4. 가독성 최적화
        optimized_content, readability_metrics = self._optimize_readability(
            optimized_content
        )
        
        # 5. 내부 링크 최적화
        optimized_content, link_metrics = self._optimize_internal_links(
            optimized_content,
            keywords
        )
        
        # 6. SEO 지표 계산
        metrics = SEOMetrics(
            keyword_density=keyword_metrics['density'],
            heading_score=heading_metrics['score'],
            meta_score=meta_metrics['score'],
            readability_score=readability_metrics['score'],
            internal_link_score=link_metrics['score']
        )
        
        # 7. 개선 제안 생성
        suggestions = self._generate_suggestions(metrics)
        
        return OptimizationResult(
            optimized_content=optimized_content,
            optimized_meta=optimized_meta,
            metrics=metrics,
            suggestions=suggestions
        )
        
    def _optimize_keyword_density(self,
                                content: str,
                                keywords: List[str]) -> tuple[str, Dict[str, float]]:
        """키워드 밀도 최적화"""
        words = content.split()
        total_words = len(words)
        keyword_count = 0
        
        # 키워드 출현 횟수 계산
        for keyword in keywords:
            keyword_count += len(re.findall(rf'\b{keyword}\b', content, re.I))
            
        current_density = keyword_count / total_words if total_words > 0 else 0
        
        # 밀도 조정
        if current_density < self.optimal_metrics['keyword_density'] * 0.8:
            # 키워드 추가
            for keyword in keywords:
                if len(re.findall(rf'\b{keyword}\b', content, re.I)) < 2:
                    # 적절한 위치에 키워드 삽입
                    paragraphs = content.split('\n\n')
                    if len(paragraphs) > 2:
                        paragraphs[1] = f"{keyword}와 관련하여, {paragraphs[1]}"
                        content = '\n\n'.join(paragraphs)
                        
        elif current_density > self.optimal_metrics['keyword_density'] * 1.2:
            # 키워드 일부 제거 (동의어로 대체)
            for keyword in keywords:
                content = re.sub(rf'\b{keyword}\b', '이것', content, count=1)
                
        return content, {'density': current_density}
        
    def _optimize_headings(self,
                          content: str,
                          keywords: List[str]) -> tuple[str, Dict[str, float]]:
        """제목 구조 최적화"""
        heading_counts = {
            'h1': 0,
            'h2': 0,
            'h3': 0
        }
        
        # 제목 태그 분석
        for tag, pattern in self.heading_patterns.items():
            matches = re.findall(pattern, content)
            heading_counts[tag] = len(matches)
            
            # 키워드가 제목에 없으면 추가
            if matches and not any(k in ' '.join(matches) for k in keywords):
                first_match = re.search(pattern, content)
                if first_match:
                    heading_text = first_match.group(1)
                    new_heading = f"{heading_text} - {keywords[0]}"
                    content = content.replace(
                        first_match.group(0),
                        f"<{tag}>{new_heading}</{tag}>"
                    )
                    
        # 제목 점수 계산
        score = min(1.0, (
            (heading_counts['h1'] == 1) * 0.4 +  # H1은 정확히 1개
            (heading_counts['h2'] >= 2) * 0.3 +  # H2는 2개 이상
            (heading_counts['h3'] >= 2) * 0.3    # H3는 2개 이상
        ))
        
        return content, {'score': score}
        
    def _optimize_meta(self,
                      meta: Dict[str, Any],
                      keywords: List[str]) -> tuple[Dict[str, Any], Dict[str, float]]:
        """메타 정보 최적화"""
        optimized_meta = meta.copy()
        score = 0.0
        
        # 1. 메타 설명 최적화
        if 'description' in optimized_meta:
            description = optimized_meta['description']
            
            # 길이 제한
            if len(description) > self.optimal_metrics['max_meta_length']:
                description = description[:157] + '...'
                
            # 키워드 포함 확인
            if not any(k in description for k in keywords):
                description = f"{keywords[0]} - {description}"
                
            optimized_meta['description'] = description
            score += 0.4
            
        # 2. 메타 키워드 최적화
        if 'keywords' in optimized_meta:
            # 중요 키워드가 앞쪽에 오도록
            keyword_set = set(optimized_meta['keywords'])
            keyword_set.update(keywords)
            optimized_meta['keywords'] = (
                keywords +
                list(keyword_set - set(keywords))
            )
            score += 0.3
            
        # 3. 메타 태그 최적화
        if 'tags' in optimized_meta:
            tags = set(optimized_meta['tags'])
            tags.update(keywords[:3])  # 주요 키워드를 태그에 추가
            optimized_meta['tags'] = list(tags)
            score += 0.3
            
        return optimized_meta, {'score': score}
        
    def _optimize_readability(self,
                            content: str) -> tuple[str, Dict[str, float]]:
        """가독성 최적화"""
        paragraphs = content.split('\n\n')
        optimized_paragraphs = []
        score = 0.0
        
        for paragraph in paragraphs:
            # 1. 문단 길이 최적화
            if len(paragraph) > self.optimal_metrics['optimal_paragraph_length']:
                # 긴 문단 분할
                sentences = re.split(r'[.!?]\s+', paragraph)
                mid = len(sentences) // 2
                optimized_paragraphs.extend([
                    '. '.join(sentences[:mid]) + '.',
                    '. '.join(sentences[mid:]) + '.'
                ])
                score += 0.5
            else:
                optimized_paragraphs.append(paragraph)
                score += 1.0
                
        # 2. 문단 간격 최적화
        optimized_content = '\n\n'.join(optimized_paragraphs)
        
        return optimized_content, {'score': score / len(paragraphs)}
        
    def _optimize_internal_links(self,
                               content: str,
                               keywords: List[str]) -> tuple[str, Dict[str, float]]:
        """내부 링크 최적화"""
        # 현재는 간단한 점수만 계산
        link_count = len(re.findall(r'<a\s+href=[^>]+>', content))
        score = min(1.0, link_count / 5)  # 5개 링크를 목표로
        
        return content, {'score': score}
        
    def _generate_suggestions(self, metrics: SEOMetrics) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 1. 키워드 밀도 관련
        if metrics.keyword_density < self.optimal_metrics['keyword_density'] * 0.8:
            suggestions.append("키워드 사용 빈도를 높여주세요.")
        elif metrics.keyword_density > self.optimal_metrics['keyword_density'] * 1.2:
            suggestions.append("키워드가 너무 자주 사용되었습니다.")
            
        # 2. 제목 구조 관련
        if metrics.heading_score < 0.8:
            suggestions.append("제목 구조를 개선해주세요. H1은 1개, H2와 H3는 각각 2개 이상 사용하세요.")
            
        # 3. 메타 정보 관련
        if metrics.meta_score < 0.8:
            suggestions.append("메타 설명과 키워드를 최적화해주세요.")
            
        # 4. 가독성 관련
        if metrics.readability_score < 0.8:
            suggestions.append("문단 길이를 조정하여 가독성을 개선해주세요.")
            
        # 5. 내부 링크 관련
        if metrics.internal_link_score < 0.6:
            suggestions.append("관련 내부 링크를 더 추가해주세요.")
            
        return suggestions
