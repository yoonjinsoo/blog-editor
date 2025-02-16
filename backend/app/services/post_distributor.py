from typing import Dict, List, Any
from dataclasses import dataclass
from .sentence_classifier import ClassifiedSentence

@dataclass
class PostStructure:
    title_keywords: List[str]
    usage_sentences: List[ClassifiedSentence]
    benefit_sentences: List[ClassifiedSentence]
    feature_sentences: List[ClassifiedSentence]
    cost_sentences: List[ClassifiedSentence]
    review_sentences: List[ClassifiedSentence]
    quality_score: float

class PostDistributor:
    def __init__(self):
        # 각 섹션별 필요한 최소/최대 문장 수
        self.section_requirements = {
            'usage': {'min': 2, 'max': 4},
            'benefits': {'min': 2, 'max': 4},
            'features': {'min': 2, 'max': 4},
            'costs': {'min': 1, 'max': 2},
            'reviews': {'min': 2, 'max': 3}
        }
        
        # 하나의 포스트에 필요한 최소 품질 점수
        self.min_post_quality = 0.7
    
    def distribute_sentences(self, classified_data: Dict[str, List[ClassifiedSentence]], 
                           max_posts: int = 3) -> List[PostStructure]:
        """분류된 문장들을 여러 개의 포스트 구조로 분배"""
        posts = []
        
        # 1. 각 카테고리별로 품질 점수 기준으로 정렬
        sorted_sentences = self._sort_sentences_by_quality(classified_data)
        
        # 2. 가능한 포스트 수 계산
        possible_posts = self._calculate_possible_posts(sorted_sentences)
        num_posts = min(possible_posts, max_posts)
        
        # 3. 문장 분배
        for i in range(num_posts):
            post = self._create_post_structure(sorted_sentences, i)
            if post and self._validate_post_structure(post):
                posts.append(post)
        
        return posts
    
    def _sort_sentences_by_quality(self, classified_data: Dict[str, List[ClassifiedSentence]]) -> Dict[str, List[ClassifiedSentence]]:
        """각 카테고리별 문장을 품질 점수로 정렬"""
        sorted_data = {}
        for category, sentences in classified_data.items():
            sorted_data[category] = sorted(sentences, 
                                        key=lambda x: (x.quality_score + x.confidence), 
                                        reverse=True)
        return sorted_data
    
    def _calculate_possible_posts(self, sorted_sentences: Dict[str, List[ClassifiedSentence]]) -> int:
        """생성 가능한 포스트 수 계산"""
        max_posts = float('inf')
        
        for category, requirements in self.section_requirements.items():
            if category in sorted_sentences:
                # 각 카테고리별로 최소 요구사항을 만족하는 문장 수로 가능한 포스트 수 계산
                available_sentences = len([s for s in sorted_sentences[category] 
                                        if (s.quality_score + s.confidence) / 2 >= 0.6])
                possible_posts = available_sentences // requirements['min']
                max_posts = min(max_posts, possible_posts)
        
        return max(0, int(max_posts))
    
    def _create_post_structure(self, sorted_sentences: Dict[str, List[ClassifiedSentence]], 
                             post_index: int) -> PostStructure:
        """하나의 포스트 구조 생성"""
        post_sentences = {
            'usage': [],
            'benefits': [],
            'features': [],
            'costs': [],
            'reviews': []
        }
        
        # 각 카테고리별로 문장 할당
        for category, requirements in self.section_requirements.items():
            if category in sorted_sentences:
                sentences = sorted_sentences[category]
                start_idx = post_index * requirements['min']
                end_idx = start_idx + requirements['max']
                
                # 품질 기준을 만족하는 문장만 선택
                qualified_sentences = [s for s in sentences[start_idx:end_idx]
                                    if (s.quality_score + s.confidence) / 2 >= 0.6]
                post_sentences[category] = qualified_sentences[:requirements['max']]
        
        # 전체 품질 점수 계산
        total_quality = self._calculate_total_quality(post_sentences)
        
        # 키워드 추출 (제목용)
        title_keywords = self._extract_title_keywords(post_sentences)
        
        return PostStructure(
            title_keywords=title_keywords,
            usage_sentences=post_sentences['usage'],
            benefit_sentences=post_sentences['benefits'],
            feature_sentences=post_sentences['features'],
            cost_sentences=post_sentences['costs'],
            review_sentences=post_sentences['reviews'],
            quality_score=total_quality
        )
    
    def _validate_post_structure(self, post: PostStructure) -> bool:
        """포스트 구조가 최소 요구사항을 만족하는지 검증"""
        if post.quality_score < self.min_post_quality:
            return False
            
        # 각 섹션별 최소 문장 수 확인
        sections = {
            'usage': post.usage_sentences,
            'benefits': post.benefit_sentences,
            'features': post.feature_sentences,
            'costs': post.cost_sentences,
            'reviews': post.review_sentences
        }
        
        for category, sentences in sections.items():
            if len(sentences) < self.section_requirements[category]['min']:
                return False
        
        return True
    
    def _calculate_total_quality(self, post_sentences: Dict[str, List[ClassifiedSentence]]) -> float:
        """포스트 전체의 품질 점수 계산"""
        total_score = 0
        total_sentences = 0
        
        for sentences in post_sentences.values():
            for sent in sentences:
                total_score += (sent.quality_score + sent.confidence) / 2
                total_sentences += 1
        
        return total_score / total_sentences if total_sentences > 0 else 0
    
    def _extract_title_keywords(self, post_sentences: Dict[str, List[ClassifiedSentence]]) -> List[str]:
        """포스트의 제목에 사용할 키워드 추출"""
        all_keywords = []
        
        # 특징과 장점 섹션에서 주로 키워드 추출
        priority_sections = ['features', 'benefits']
        for section in priority_sections:
            for sent in post_sentences[section]:
                all_keywords.extend(sent.keywords)
        
        # 빈도수 기준으로 상위 키워드 선택
        keyword_freq = {}
        for keyword in all_keywords:
            keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        sorted_keywords = sorted(keyword_freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, _ in sorted_keywords[:5]]  # 상위 5개 키워드 반환
