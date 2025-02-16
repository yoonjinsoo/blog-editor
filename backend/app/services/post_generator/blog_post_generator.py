from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import json
import os
from pathlib import Path

from ..content_context.content_context import ContentContext
from ..sentence_analyzer.sentence_analyzer import SentenceAnalyzer, AnalyzedSentence
from ..fact_extractor.fact_extractor import FactExtractor
from .content_assembler import ContentAssembler
from .title_generator import TitleGenerator
from .section_assembler import SectionAssemblerFactory
from ..content_quality.content_quality_checker import ContentQualityChecker, QualityCheckResult
from ..content_quality.content_styler import ContentStyler, StyleConfig, StyleResult
from ..content_quality.content_optimizer import ContentOptimizer, OptimizationResult

@dataclass
class TitleSet:
    """제목 세트"""
    main_title: str
    sub_title: str
    meta_description: str

@dataclass
class BlogPost:
    """블로그 포스트"""
    title: str
    meta: Dict[str, Any]
    content: Dict[str, Any]
    footer: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SectionContent:
    """섹션 콘텐츠"""
    title: str
    paragraphs: List[str]

@dataclass
class GenerationResult:
    """생성 결과"""
    post: BlogPost
    style_result: Optional[StyleResult] = None
    seo_result: Optional[OptimizationResult] = None

class LLM:
    """LLM 클래스"""
    def generate(self, prompt: str) -> str:
        """프롬프트를 기반으로 텍스트 생성"""
        # 실제 LLM 호출 대신 임시로 샘플 텍스트 반환
        return """# 소개
안녕하세요! 오늘은 2025년 최신 트렌드로 떠오르는 퀵플렉스(QuickFlex) 서비스에 대해 자세히 알아보겠습니다. 특히 직장인들의 부업으로 주목받고 있는 이유와 실제 성공 사례를 중심으로 살펴보겠습니다.

# 퀵플렉스란?
퀵플렉스는 기존의 배달 서비스와는 차별화된 새로운 개념의 물류 플랫폼입니다. 특히 다음과 같은 특징들로 주목받고 있습니다:

- 자유로운 시간 관리
- 안정적인 수입
- 낮은 진입 장벽
- 체계적인 교육 지원

# 수익성 분석
실제 퀵플렉스 기사님들의 데이터를 분석해보면, 평균적으로 월 300만원 이상의 수익을 올리고 있습니다. 특히 성과가 좋은 상위 20% 기사님들은 월 500만원 이상을 달성하고 있죠.

# 시작하는 방법
1. 화물운송종사자격증 취득
2. 기본 교육 이수
3. 실전 연습
4. 정식 계약

# 결론
퀵플렉스는 2025년 현재, 직장인들의 안정적인 부업 수단으로 자리잡았습니다. 특히 자유로운 시간 활용과 안정적인 수익이 보장되어 많은 분들이 관심을 가지고 있습니다. 체계적인 교육과 지원 시스템을 통해 초보자도 쉽게 시작할 수 있다는 것이 큰 장점입니다."""

class BlogPostGenerator:
    """블로그 포스트 생성기"""
    
    def __init__(self, content_context: ContentContext):
        """초기화"""
        self.context = content_context
        self.title_generator = TitleGenerator(content_context)
        self.llm = LLM()  # LLM 인스턴스 추가
        
        # 컴포넌트 초기화
        self.fact_extractor = FactExtractor()
        self.sentence_analyzer = SentenceAnalyzer()
        self.content_assembler = ContentAssembler(content_context)
        
    def generate_post(self, raw_data: Dict[str, Any]) -> BlogPost:
        """블로그 포스트 생성"""
        # 1. 사실 정보 추출
        facts = self.extract_facts(raw_data)
        
        # 2. LLM으로 블로그 포스트 생성
        prompt = f"""다음 정보를 바탕으로 블로그 포스트를 작성해주세요.
        주제: {self.context.keyword}
        서비스: {self.context.service.name}
        참고 정보:
        {facts}
        
        다음 형식으로 작성해주세요:
        1. 소개 (흥미로운 도입부)
        2. 서비스 설명 (주요 특징과 장점)
        3. 수익성 분석 (구체적인 데이터)
        4. 시작하는 방법 (단계별 설명)
        5. 결론 (요약 및 추천)
        """
        
        generated_content = self.llm.generate(prompt)
        
        # 3. 제목 생성
        titles = self.title_generator.generate_titles(
            SectionContent(title="intro", paragraphs=[generated_content[:200]]),  # 처음 200자를 기반으로 제목 생성
            SectionContent(title="main", paragraphs=[generated_content])
        )
        
        # 4. 블로그 포스트 구조화
        post = BlogPost(
            title=titles.main_title,
            meta={
                "description": titles.meta_description,
                "keywords": [self.context.keyword] + self.context.service.features,
                "author": "AI 에디터",
                "date": "2025-02-17"
            },
            content={
                "title": titles.main_title,
                "subtitle": titles.sub_title,
                "body": generated_content
            },
            footer={
                "tags": ", ".join([self.context.keyword] + self.context.service.features),
                "category": "부업/투잡"
            }
        )
        
        return post

    def extract_facts(self, raw_data: Dict[str, Any]) -> str:
        """원본 데이터에서 사실 정보 추출"""
        facts = []
        
        # 블로그 결과에서 정보 추출
        blog_results = raw_data.get('blog_results', [])
        for result in blog_results:
            content = result.get('content', '')
            if not content:
                continue
                
            # 문장 단위로 분리
            sentences = content.split('. ')
            for sentence in sentences:
                # 키워드나 서비스 관련 문장만 선택
                if (self.context.keyword in sentence or 
                    self.context.service.name in sentence or
                    any(feature in sentence for feature in self.context.service.features) or
                    any(benefit in sentence for benefit in self.context.service.benefits)):
                    
                    # 불필요한 문구 제거
                    cleaned = sentence.replace('★', '').replace('*', '').strip()
                    if cleaned and len(cleaned) > 10:  # 너무 짧은 문장 제외
                        facts.append(cleaned)
        
        # 중복 제거
        facts = list(set(facts))
        
        # 문장 품질 기준으로 정렬
        facts.sort(key=lambda x: (
            self.context.keyword in x,  # 키워드 포함 여부
            len(x) >= 20 and len(x) <= 100,  # 적절한 길이
            not any(bad_word in x for bad_word in ['사기', '불법', '문제'])  # 부정적 단어 제외
        ), reverse=True)
        
        # 상위 10개 문장만 선택
        selected_facts = facts[:10]
        
        # 문자열로 변환
        return "\n".join(f"- {fact}" for fact in selected_facts)

    def _split_content_into_sections(self, content: str) -> List[Dict[str, Any]]:
        """생성된 콘텐츠를 섹션별로 분리"""
        # 여기서 콘텐츠를 분석하여 섹션으로 나눔
        # 실제 구현에서는 더 정교한 분리 로직 필요
        sections = []
        
        # 임시 구현
        paragraphs = content.split('\n\n')
        current_section = {
            'type': 'intro',
            'title': '소개',
            'content': []
        }
        
        for p in paragraphs:
            if not p.strip():
                continue
                
            # 새로운 섹션의 시작인지 확인
            if p.startswith('# '):
                if current_section['content']:
                    sections.append(current_section)
                
                title = p.replace('# ', '').strip()
                if '결론' in title.lower():
                    current_section = {
                        'type': 'conclusion',
                        'title': title,
                        'content': []
                    }
                else:
                    current_section = {
                        'type': 'main',
                        'title': title,
                        'content': []
                    }
            else:
                current_section['content'].append(p.strip())
        
        if current_section['content']:
            sections.append(current_section)
            
        return sections
        
    def _check_quality(self, post: BlogPost) -> QualityCheckResult:
        """품질 검사"""
        # 컨텐츠 추출
        content = self._extract_content_from_post(post)
        
        # 키워드 추출
        keywords = [
            *post.meta['keywords'][:5],  # 상위 5개 키워드
            post.title.split()[0]  # 제목의 첫 단어
        ]
        
        return self.quality_checker.check_content(content, keywords)
        
    def _apply_style(self, post: BlogPost) -> StyleResult:
        """스타일 적용"""
        # 컨텐츠 추출
        content = self._extract_content_from_post(post)
        
        return self.content_styler.apply_style(content, self.style_config)
        
    def _optimize_content(self, 
                         post: BlogPost,
                         main_keyword: str) -> OptimizationResult:
        """SEO 최적화"""
        # 컨텐츠 추출
        content = self._extract_content_from_post(post)
        
        # 키워드 준비
        keywords = [
            main_keyword,
            *post.meta['keywords'][:3]  # 상위 3개 키워드
        ]
        
        return self.content_optimizer.optimize_content(
            content,
            post.meta,
            keywords
        )
        
    def _update_post_with_optimizations(self,
                                      post: BlogPost,
                                      style_result: StyleResult,
                                      seo_result: OptimizationResult) -> BlogPost:
        """최적화 결과를 포스트에 적용"""
        # 1. 스타일이 적용된 컨텐츠를 섹션별로 분할
        styled_content = style_result.styled_content
        sections = self._split_content_into_sections(styled_content)
        
        # 2. SEO 최적화된 메타 정보 적용
        post.meta.update(seo_result.optimized_meta)
        
        # 3. 섹션별 컨텐츠 업데이트
        for section_name, content in sections.items():
            if section_name in post.content:
                post.content[section_name]['paragraphs'] = content.split('\n\n')
                
        return post
        
    def _extract_content_from_post(self, post: BlogPost) -> str:
        """포스트에서 컨텐츠 추출"""
        sections = []
        
        # 1. 제목 추가
        sections.append(f"<h1>{post.title}</h1>")
        
        # 2. 섹션별 컨텐츠 추가
        for section_name, section in post.content.items():
            if 'title' in section:
                sections.append(f"<h2>{section['title']}</h2>")
            if 'paragraphs' in section:
                sections.extend(section['paragraphs'])
                
        # 3. 푸터 추가
        sections.append(post.footer['company_info'])
        sections.append(post.footer['contact'])
        
        return '\n\n'.join(sections)
        
    def _analyze_sentences(self,
                          facts: Dict[str, Any],
                          context: ContentContext) -> List[AnalyzedSentence]:
        """문장 분석"""
        sentences = []
        
        # 팩트 유형별 문장 분석
        for fact_type, items in facts.items():
            if not isinstance(items, list):
                continue
                
            for item in items:
                if isinstance(item, dict):
                    text = item.get('text', '')
                else:
                    text = str(item)
                    
                if text:
                    analyzed = self.sentence_analyzer._analyze_single_sentence(text)
                    if analyzed.quality_score >= self.quality_threshold:
                        sentences.append(analyzed)
                        
        return sentences
        
    def _validate_post_quality(self, post: BlogPost) -> bool:
        """포스트 품질 검증"""
        # 1. 제목 검증
        if not self._validate_title(post.title):
            return False
            
        # 2. 컨텐츠 검증
        if not self._validate_content(post.content):
            return False
            
        # 3. 메타 정보 검증
        if not self._validate_meta(post.meta):
            return False
            
        return True
        
    def _validate_title(self, title: str) -> bool:
        """제목 검증"""
        # 길이 제한 확인
        if len(title) > 45:
            return False
            
        return True
        
    def _validate_content(self, content: Dict[str, Any]) -> bool:
        """컨텐츠 검증"""
        # 필수 섹션 확인
        required_sections = ['intro', 'main_sections', 'conclusion']
        if not all(section in content for section in required_sections):
            return False
            
        # 각 섹션 문단 수 확인
        if len(content['intro']['paragraphs']) < 2:
            return False
            
        if len(content['main_sections']['paragraphs']) < 3:
            return False
            
        if len(content['conclusion']['paragraphs']) < 1:
            return False
            
        return True
        
    def _validate_meta(self, meta: Dict[str, Any]) -> bool:
        """메타 정보 검증"""
        # 필수 필드 확인
        required_fields = ['description', 'keywords', 'tags']
        if not all(field in meta for field in required_fields):
            return False
            
        # 키워드 수 확인
        if len(meta['keywords']) < 5:
            return False
            
        # 메타 설명 길이 확인
        if len(meta['description']) > 160:
            return False
            
        return True
        
    def _save_post(self, 
                   post: BlogPost,
                   keyword: str) -> Dict[str, Any]:
        """포스트 저장"""
        # 파일명 생성
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{keyword}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        # 저장할 데이터 준비
        data = {
            'post': {
                'title': post.title,
                'meta': post.meta,
                'content': post.content,
                'footer': post.footer
            },
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'keyword': keyword,
                'version': '2.0'
            }
        }
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        return {
            'filepath': str(filepath),
            'filename': filename,
            'timestamp': timestamp
        }

class TitleGenerator:
    """제목 생성기"""
    def __init__(self, content_context):
        self.context = content_context
    
    def generate_titles(self, intro: SectionContent, main: SectionContent) -> TitleSet:
        """제목 세트 생성"""
        # 임시로 고정된 제목 반환
        return TitleSet(
            main_title=f"2025년 직장인 부업 트렌드, {self.context.service.name}로 월 300만원 벌기",
            sub_title=f"{self.context.service.name}의 특징과 장점, 그리고 시작하는 방법",
            meta_description=f"2025년 최신 트렌드 {self.context.service.name}를 활용한 직장인 부업 완벽 가이드. 월 300만원 수익 달성 노하우와 시작 방법을 상세히 알아봅니다."
        )
