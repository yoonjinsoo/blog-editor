from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import random
from .section_assembler import (
    SectionAssemblerFactory,
    SectionContent,
    SectionAssembler
)
from .title_generator import TitleGenerator
from ..content_context.content_context import ContentContext
from ..sentence_analyzer.sentence_analyzer import AnalyzedSentence

@dataclass
class BlogPost:
    """블로그 포스트 구조체"""
    title: str
    meta: Dict[str, Any]   # description, keywords, tags
    content: Dict[str, Any]  # intro, main_sections, conclusion
    footer: Dict[str, str]  # company_info, contact
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'title': self.title,
            'meta': self.meta,
            'content': self.content,
            'footer': self.footer
        }
        
class ContentAssembler:
    """블로그 포스트 조립기"""
    
    def __init__(self, content_context: ContentContext):
        self.context = content_context
        self.section_factory = SectionAssemblerFactory()
        self.title_generator = TitleGenerator(content_context)
        
    def _group_sentences(self, sentences: List[AnalyzedSentence]) -> Dict[str, List[AnalyzedSentence]]:
        """문장 그룹화"""
        groups = {
            'intro': [],
            'main': [],
            'conclusion': []
        }
        
        for sentence in sentences:
            if sentence.sentence_type in ['hook', 'statistics']:
                groups['intro'].append(sentence)
            elif sentence.sentence_type in ['core', 'detail', 'example']:
                groups['main'].append(sentence)
            elif sentence.sentence_type in ['summary', 'action']:
                groups['conclusion'].append(sentence)
            else:
                groups['main'].append(sentence)
                
        return groups
        
    def _generate_meta(self, description: str, sentences: List[AnalyzedSentence]) -> Dict[str, Any]:
        """메타 정보 생성"""
        keywords = set()
        for sentence in sentences:
            keywords.update(sentence.keywords)
            
        return {
            'description': description,
            'keywords': list(keywords),
            'tags': [self.context.keyword]
        }
        
    def _generate_footer(self) -> Dict[str, str]:
        """푸터 정보 생성"""
        return {
            'company_info': self.context.company,
            'contact': self.context.contact_info
        }
        
    def assemble_post(self, analyzed_sentences: List[AnalyzedSentence]) -> Dict[str, Any]:
        """블로그 포스트 조립"""
        # 1. 섹션별 문장 분류
        sentence_groups = self._group_sentences(analyzed_sentences)
        
        # 2. 섹션 조립
        intro_assembler = self.section_factory.create_assembler('intro', self.context)
        main_assembler = self.section_factory.create_assembler('main', self.context)
        conclusion_assembler = self.section_factory.create_assembler('conclusion', self.context)
        
        intro_content = intro_assembler.assemble(sentence_groups['intro'])
        main_content = main_assembler.assemble(sentence_groups['main'])
        conclusion_content = conclusion_assembler.assemble(sentence_groups['conclusion'])
        
        # 3. 제목 생성
        titles = self.title_generator.generate_titles(intro_content, main_content)
        
        # 4. 메타 정보 생성
        meta = self._generate_meta(titles.meta_description, analyzed_sentences)
        
        # 5. 푸터 정보 생성
        footer = self._generate_footer()
        
        # 6. 최종 포스트 조립
        post = BlogPost(
            title=titles.main_title,
            meta=meta,
            content={
                'intro': intro_content.to_dict(),
                'main_sections': main_content.to_dict(),
                'conclusion': conclusion_content.to_dict()
            },
            footer=footer
        )
        
        return post.to_dict()
