from typing import Dict, List, Any
import random
from ..sentence_analyzer.sentence_analyzer import AnalyzedSentence
from ..content_context.content_context import ContentContext

class SentenceConnector:
    """문장과 서비스를 자연스럽게 연결하는 클래스"""
    
    def __init__(self, content_context: ContentContext):
        self.context = content_context
        
    def connect_sentences(self, sentences: List[AnalyzedSentence]) -> List[Dict[str, Any]]:
        """문장들과 서비스 연결"""
        connected_sentences = []
        
        for i, sentence in enumerate(sentences):
            # 1. 연결 포인트 찾기
            connection = self.context.get_connection_point(sentence.text)
            
            # 2. 연결 문장 생성
            if connection['type'] and connection['template']:
                connected = {
                    'original': sentence.text,
                    'connection_type': connection['type'],
                    'service_connection': self._generate_connection_sentence(
                        connection['template'],
                        connection['params']
                    )
                }
                connected_sentences.append(connected)
            else:
                # 직접적인 연결점이 없는 경우
                connected_sentences.append({
                    'original': sentence.text,
                    'connection_type': None,
                    'service_connection': None
                })
                
        return connected_sentences
    
    def _generate_connection_sentence(self, templates: List[str], params: Dict[str, Any]) -> str:
        """서비스 연결 문장 생성"""
        # 템플릿 랜덤 선택
        template = random.choice(templates)
        
        # 파라미터 채우기
        try:
            return template.format(**params)
        except KeyError:
            # 파라미터 매칭 실패시 기본 템플릿 사용
            return f"이러한 상황에서 {self.context.service.name}이(가) 도움이 될 수 있습니다."
            
    def enhance_section(self, section_sentences: List[Dict[str, Any]], 
                       section_type: str) -> List[str]:
        """섹션 전체의 문장들을 향상"""
        enhanced = []
        service_mentioned = False
        
        for i, sentence in enumerate(section_sentences):
            enhanced.append(sentence['original'])
            
            # 서비스 연결 문장 추가
            if sentence['service_connection']:
                if not service_mentioned or random.random() < 0.3:  # 30% 확률로 추가 연결
                    enhanced.append(sentence['service_connection'])
                    service_mentioned = True
                    
            # 섹션별 마무리 문장 추가
            if i == len(section_sentences) - 1:
                if section_type == 'conclusion':
                    templates = self.context.service.get_connection_templates()['conclusion']
                    enhanced.append(random.choice(templates))
                    
        return enhanced
