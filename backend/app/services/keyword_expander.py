from typing import List, Dict, Any
from dataclasses import dataclass
from .sentence_classifier import ClassifiedSentence

@dataclass
class ExpandedKeyword:
    keyword: str
    related_sentences: Dict[str, List[ClassifiedSentence]]
    relevance_score: float
    independence_score: float
    quality_score: float

class KeywordExpander:
    def __init__(self):
        self.section_requirements = {
            'intro': {'min': 2, 'max': 3},
            'main': {'min': 3, 'max': 4},
            'stats': {'min': 1, 'max': 2},
            'examples': {'min': 1, 'max': 2},
            'conclusion': {'min': 1, 'max': 2}
        }
        
        self.total_min_sentences = sum(req['min'] for req in self.section_requirements.values())
    
    def expand_keywords(self, main_keyword: str, classified_sentences: Dict[str, List[ClassifiedSentence]]) -> List[ExpandedKeyword]:
        # 1. 전체 문장 수에 따른 확장 키워드 수 결정
        total_sentences = sum(len(sentences) for sentences in classified_sentences.values())
        max_keywords = self._determine_max_keywords(total_sentences)
        
        # 2. 후보 키워드 그룹 생성
        candidate_groups = self._create_candidate_groups(classified_sentences)
        
        # 3. 키워드 그룹 평가
        evaluated_groups = []
        for group in candidate_groups:
            if self._meets_minimum_requirements(group):
                relevance = self._calculate_relevance(main_keyword, group)
                independence = self._calculate_independence(group, candidate_groups)
                quality = self._calculate_quality(group)
                
                evaluated_groups.append({
                    'group': group,
                    'relevance': relevance,
                    'independence': independence,
                    'quality': quality
                })
        
        # 4. 우선순위에 따른 정렬
        evaluated_groups.sort(key=lambda x: (
            self._meets_minimum_requirements(x['group']),  # 1순위
            x['relevance'],                               # 2순위
            x['independence'],                            # 3순위
            x['quality']                                  # 4순위
        ), reverse=True)
        
        # 5. 최종 확장 키워드 선택
        selected_groups = evaluated_groups[:max_keywords]
        
        return [
            ExpandedKeyword(
                keyword=self._extract_main_keyword(group['group']),
                related_sentences=group['group'],
                relevance_score=group['relevance'],
                independence_score=group['independence'],
                quality_score=group['quality']
            )
            for group in selected_groups
        ]
    
    def _determine_max_keywords(self, total_sentences: int) -> int:
        """문장 수에 따른 최대 확장 키워드 수 결정"""
        if total_sentences < 100:
            return 3
        elif total_sentences < 200:
            return 5
        elif total_sentences < 300:
            return 7
        else:
            return 8  # 최대 제한
    
    def _meets_minimum_requirements(self, sentence_group: Dict[str, List[ClassifiedSentence]]) -> bool:
        """최소 문장 수 요구사항 충족 여부 확인"""
        section_counts = {
            'intro': len([s for s in sentence_group.get('usage', [])
                         if s.quality_score >= 0.7]),
            'main': len([s for s in sentence_group.get('features', []) + sentence_group.get('benefits', [])
                        if s.quality_score >= 0.7]),
            'stats': len([s for s in sentence_group.get('costs', [])
                         if s.quality_score >= 0.7]),
            'examples': len([s for s in sentence_group.get('reviews', [])
                           if s.quality_score >= 0.7]),
            'conclusion': len([s for s in sentence_group.get('reviews', []) + sentence_group.get('benefits', [])
                             if s.quality_score >= 0.7])
        }
        
        return all(
            section_counts[section] >= self.section_requirements[section]['min']
            for section in self.section_requirements
        )
    
    def _calculate_relevance(self, main_keyword: str, sentence_group: Dict[str, List[ClassifiedSentence]]) -> float:
        """메인 키워드와의 연관성 점수 계산"""
        relevance_scores = []
        for sentences in sentence_group.values():
            for sentence in sentences:
                if main_keyword in sentence.text:
                    relevance_scores.append(sentence.confidence)
        
        return sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0.0
    
    def _calculate_independence(self, group: Dict[str, List[ClassifiedSentence]], 
                              all_groups: List[Dict[str, List[ClassifiedSentence]]]) -> float:
        """다른 그룹과의 독립성 점수 계산"""
        group_keywords = set()
        for sentences in group.values():
            for sentence in sentences:
                group_keywords.update(sentence.keywords)
        
        overlap_scores = []
        for other_group in all_groups:
            if other_group == group:
                continue
            
            other_keywords = set()
            for sentences in other_group.values():
                for sentence in sentences:
                    other_keywords.update(sentence.keywords)
            
            if other_keywords:
                overlap = len(group_keywords & other_keywords) / len(group_keywords | other_keywords)
                overlap_scores.append(1 - overlap)
        
        return sum(overlap_scores) / len(overlap_scores) if overlap_scores else 1.0
    
    def _calculate_quality(self, group: Dict[str, List[ClassifiedSentence]]) -> float:
        """문장 그룹의 전체 품질 점수 계산"""
        quality_scores = []
        for sentences in group.values():
            for sentence in sentences:
                quality_scores.append(sentence.quality_score)
        
        return sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
    
    def _extract_main_keyword(self, group: Dict[str, List[ClassifiedSentence]]) -> str:
        """문장 그룹의 대표 키워드 추출"""
        keyword_freq = {}
        for sentences in group.values():
            for sentence in sentences:
                for keyword in sentence.keywords:
                    keyword_freq[keyword] = keyword_freq.get(keyword, 0) + 1
        
        return max(keyword_freq.items(), key=lambda x: x[1])[0]
    
    def _create_candidate_groups(self, classified_sentences: Dict[str, List[ClassifiedSentence]]) -> List[Dict[str, List[ClassifiedSentence]]]:
        """후보 키워드 그룹 생성"""
        # 임시로 간단한 그룹핑 구현
        # 실제로는 더 복잡한 클러스터링 알고리즘 사용 필요
        groups = []
        used_sentences = set()
        
        for category, sentences in classified_sentences.items():
            for sentence in sentences:
                if sentence in used_sentences:
                    continue
                
                group = {cat: [] for cat in classified_sentences.keys()}
                group[category].append(sentence)
                used_sentences.add(sentence)
                
                # 관련 문장 찾기
                for other_cat, other_sentences in classified_sentences.items():
                    for other_sentence in other_sentences:
                        if other_sentence in used_sentences:
                            continue
                        
                        # 키워드 유사도로 관련 문장 판단
                        common_keywords = set(sentence.keywords) & set(other_sentence.keywords)
                        if len(common_keywords) >= 2:  # 최소 2개 이상의 공통 키워드
                            group[other_cat].append(other_sentence)
                            used_sentences.add(other_sentence)
                
                if self._meets_minimum_requirements(group):
                    groups.append(group)
        
        return groups
