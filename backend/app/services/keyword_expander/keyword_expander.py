from typing import Dict, List, Any
from collections import defaultdict
from dataclasses import dataclass
from ..sentence_analyzer.sentence_analyzer import AnalyzedSentence
from ..content_context.content_context import ContentContext
from ..sentence_connector.sentence_connector import SentenceConnector

@dataclass
class KeywordCluster:
    """키워드 클러스터 정보"""
    main_keyword: str
    related_keywords: List[str]
    sentences: List[AnalyzedSentence]
    relevance_score: float
    sentence_count: Dict[str, int]  # 문장 유형별 개수
    connected_sentences: List[Dict[str, Any]]  # 서비스 연결된 문장들

@dataclass
class ExpandedKeyword:
    """확장 키워드 정보"""
    keyword: str
    cluster: KeywordCluster
    quality_score: float
    is_valid: bool

class KeywordExpander:
    """분석된 문장들을 기반으로 확장 키워드를 생성하는 클래스"""
    
    def __init__(self, content_context: ContentContext):
        self.min_cluster_size = 8  # 최소 필요 문장 수
        self.min_relevance_score = 0.7  # 메인 키워드와의 최소 연관성 점수
        self.content_context = content_context
        self.sentence_connector = SentenceConnector(content_context)
        
        # 문장 유형별 최소 필요 개수
        self.required_sentence_counts = {
            'intro': 2,
            'main': 3,
            'statistics': 1,
            'example': 1,
            'conclusion': 1
        }
        
    def expand_keywords(self, analyzed_sentences: List[AnalyzedSentence]) -> List[ExpandedKeyword]:
        """확장 키워드 생성"""
        # 1. 문장 클러스터링
        clusters = self._cluster_sentences(analyzed_sentences)
        
        # 2. 클러스터 품질 평가
        evaluated_clusters = self._evaluate_clusters(self.content_context.keyword, clusters)
        
        # 3. 상위 클러스터 선택
        top_clusters = self._select_top_clusters(evaluated_clusters)
        
        # 4. 서비스 연결
        connected_clusters = self._connect_service_to_clusters(top_clusters)
        
        # 5. 확장 키워드 생성
        expanded_keywords = self._create_expanded_keywords(connected_clusters)
        
        return expanded_keywords
        
    def _cluster_sentences(self, 
                         analyzed_sentences: List[AnalyzedSentence]) -> List[KeywordCluster]:
        """문장들을 키워드 기반으로 클러스터링"""
        # 키워드별 문장 그룹화
        keyword_groups = defaultdict(list)
        for sentence in analyzed_sentences:
            for keyword in sentence.keywords:
                keyword_groups[keyword].append(sentence)
        
        # 클러스터 생성
        clusters = []
        processed_keywords = set()
        
        for keyword, sentences in keyword_groups.items():
            if keyword in processed_keywords:
                continue
                
            # 연관 키워드 찾기
            related_keywords = self._find_related_keywords(keyword, keyword_groups)
            processed_keywords.update(related_keywords)
            
            # 문장 유형별 개수 계산
            sentence_count = self._count_sentence_types(sentences)
            
            # 클러스터 생성
            cluster = KeywordCluster(
                main_keyword=keyword,
                related_keywords=list(related_keywords),
                sentences=sentences,
                relevance_score=0.0,  # 초기값, 나중에 계산
                sentence_count=sentence_count,
                connected_sentences=[]
            )
            
            clusters.append(cluster)
        
        return clusters
    
    def _find_related_keywords(self, keyword: str, 
                             keyword_groups: Dict[str, List[AnalyzedSentence]]) -> set:
        """주어진 키워드와 연관된 키워드 찾기"""
        related = {keyword}
        base_sentences = set(s.text for s in keyword_groups[keyword])
        
        for other_keyword, other_sentences in keyword_groups.items():
            if other_keyword == keyword:
                continue
                
            other_texts = set(s.text for s in other_sentences)
            # 문장 중복도가 높은 키워드를 연관 키워드로 판단
            if len(base_sentences & other_texts) / len(base_sentences) > 0.3:
                related.add(other_keyword)
                
        return related
    
    def _count_sentence_types(self, sentences: List[AnalyzedSentence]) -> Dict[str, int]:
        """문장 유형별 개수 계산"""
        counts = {
            'intro': 0,
            'main': 0,
            'statistics': 0,
            'example': 0,
            'conclusion': 0
        }
        
        for sent in sentences:
            # 통계 문장
            if sent.has_statistics:
                counts['statistics'] += 1
                continue
                
            # 예시 문장
            if sent.has_example:
                counts['example'] += 1
                continue
                
            # 도입부 문장 (객관적이고 짧은 문장)
            if sent.sentiment == 'objective' and sent.length < 50:
                counts['intro'] += 1
                continue
                
            # 결론 문장 (주관적이거나 긴 문장)
            if sent.sentiment == 'subjective' or sent.length > 80:
                counts['conclusion'] += 1
                continue
                
            # 나머지는 본문 문장
            counts['main'] += 1
            
        return counts
    
    def _evaluate_clusters(self, main_keyword: str, 
                         clusters: List[KeywordCluster]) -> List[KeywordCluster]:
        """클러스터 품질 평가"""
        for cluster in clusters:
            # 1. 메인 키워드와의 연관성 점수 계산
            relevance_score = self._calculate_relevance_score(
                main_keyword, 
                cluster.main_keyword,
                cluster.related_keywords
            )
            cluster.relevance_score = relevance_score
            
        return clusters
    
    def _calculate_relevance_score(self, main_keyword: str, 
                                 cluster_keyword: str,
                                 related_keywords: List[str]) -> float:
        """키워드 연관성 점수 계산"""
        score = 0.0
        
        # 1. 직접적인 포함 관계
        if main_keyword in cluster_keyword or cluster_keyword in main_keyword:
            score += 0.5
            
        # 2. 관련 키워드와의 관계
        for related in related_keywords:
            if main_keyword in related or related in main_keyword:
                score += 0.3
                break
                
        # 3. 키워드 길이 고려
        length_score = min(1.0, len(cluster_keyword) / len(main_keyword))
        score += 0.2 * length_score
        
        return min(1.0, score)
    
    def _select_top_clusters(self, clusters: List[KeywordCluster]) -> List[KeywordCluster]:
        """품질 기준을 충족하는 상위 클러스터 선택"""
        valid_clusters = []
        
        for cluster in clusters:
            # 1. 최소 문장 수 확인
            if sum(cluster.sentence_count.values()) < self.min_cluster_size:
                continue
                
            # 2. 문장 유형별 최소 개수 확인
            if not self._check_minimum_sentence_counts(cluster.sentence_count):
                continue
                
            # 3. 연관성 점수 확인
            if cluster.relevance_score < self.min_relevance_score:
                continue
                
            valid_clusters.append(cluster)
            
        # 연관성 점수 기준으로 정렬
        valid_clusters.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return valid_clusters
    
    def _check_minimum_sentence_counts(self, counts: Dict[str, int]) -> bool:
        """문장 유형별 최소 개수 충족 여부 확인"""
        for type_name, required_count in self.required_sentence_counts.items():
            if counts.get(type_name, 0) < required_count:
                return False
        return True
    
    def _connect_service_to_clusters(self, clusters: List[KeywordCluster]) -> List[KeywordCluster]:
        """각 클러스터의 문장들에 서비스 연결"""
        connected_clusters = []
        
        for cluster in clusters:
            # 문장들과 서비스 연결
            connected_sentences = self.sentence_connector.connect_sentences(cluster.sentences)
            
            # 연결된 문장 정보 추가
            cluster.connected_sentences = connected_sentences
            connected_clusters.append(cluster)
            
        return connected_clusters
    
    def _create_expanded_keywords(self, clusters: List[KeywordCluster]) -> List[ExpandedKeyword]:
        """확장 키워드 생성"""
        expanded_keywords = []
        
        for cluster in clusters:
            # 품질 점수 계산
            quality_score = self._calculate_cluster_quality_score(cluster)
            
            # 확장 키워드 생성
            expanded = ExpandedKeyword(
                keyword=cluster.main_keyword,
                cluster=cluster,
                quality_score=quality_score,
                is_valid=True
            )
            
            expanded_keywords.append(expanded)
            
        return expanded_keywords
    
    def _calculate_cluster_quality_score(self, cluster: KeywordCluster) -> float:
        """클러스터 품질 점수 계산"""
        score = 0.0
        
        # 1. 연관성 점수 반영 (0.4)
        score += 0.4 * cluster.relevance_score
        
        # 2. 문장 수 점수 (0.3)
        sentence_count = sum(cluster.sentence_count.values())
        count_score = min(1.0, sentence_count / self.min_cluster_size)
        score += 0.3 * count_score
        
        # 3. 문장 유형 다양성 점수 (0.3)
        type_score = sum(1 for count in cluster.sentence_count.values() if count > 0) / len(cluster.sentence_count)
        score += 0.3 * type_score
        
        return score
