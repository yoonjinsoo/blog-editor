from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..content_context.content_context import ContentContext

@dataclass
class SectionContent:
    """섹션 컨텐츠 정보"""
    title: str
    paragraphs: List[str]
    service_connection: Optional[str] = None
    meta_info: Optional[Dict[str, str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'title': self.title,
            'paragraphs': self.paragraphs,
            'service_connection': self.service_connection,
            'meta_info': self.meta_info
        }
    
    @staticmethod
    def from_string(text: str) -> 'SectionContent':
        """문자열로부터 섹션 컨텐츠 생성"""
        return SectionContent(
            title="",
            paragraphs=[text],
            service_connection=None,
            meta_info=None
        )

class SectionAssembler:
    """섹션 어셈블러 기본 클래스"""
    
    def __init__(self, content_context: ContentContext):
        self.context = content_context
        
    def create_intro_section(self, sentences: List[Any]) -> SectionContent:
        """소개 섹션 생성"""
        paragraphs = []
        for sentence in sentences:
            paragraphs.append(sentence.text)
            
        return SectionContent(
            title="소개",
            paragraphs=paragraphs,
            service_connection=None,
            meta_info=None
        )
        
    def create_main_sections(self, sentences: List[Any]) -> SectionContent:
        """메인 섹션 생성"""
        paragraphs = []
        for sentence in sentences:
            paragraphs.append(sentence.text)
            
        return SectionContent(
            title="본문",
            paragraphs=paragraphs,
            service_connection=f"{self.context.service.name}의 {self.context.service.features[0]} 기능으로 {self.context.service.benefits[0]}을(를) 경험해보세요.",
            meta_info=None
        )
        
    def create_conclusion_section(self, sentences: List[Any]) -> SectionContent:
        """결론 섹션 생성"""
        paragraphs = []
        for sentence in sentences:
            paragraphs.append(sentence.text)
            
        return SectionContent(
            title="결론",
            paragraphs=paragraphs,
            service_connection=None,
            meta_info=None
        )

class BlogSectionAssembler(SectionAssembler):
    """블로그용 섹션 어셈블러"""
    pass

class SectionAssemblerFactory:
    """섹션 어셈블러 팩토리"""
    
    @staticmethod
    def create_assembler(assembler_type: str, context: ContentContext) -> SectionAssembler:
        """어셈블러 생성"""
        if assembler_type == "blog":
            return BlogSectionAssembler(context)
        else:
            return SectionAssembler(context)
