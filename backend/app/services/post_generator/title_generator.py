from typing import Dict, List, Optional
from dataclasses import dataclass
import datetime
from ..content_context.content_context import ContentContext
from .section_assembler import SectionContent

@dataclass
class TitleSet:
    """블로그 제목 세트"""
    main_title: str        # 메인 제목
    sub_title: str        # 부제목
    seo_title: str        # SEO 최적화 제목
    meta_description: str  # 메타 설명

class TitleGenerator:
    """블로그 제목 생성기"""
    
    def __init__(self, content_context: ContentContext):
        self.context = content_context
        self.current_year = datetime.datetime.now().year
        
        # 제목 패턴 정의
        self.title_patterns = {
            'benefit': [
                "{year}년 {keyword} {benefit}! {service}로 시작하세요",
                "{keyword}로 {benefit} 가능한 {service} 알아보기",
                "놓치면 후회할 {keyword} {benefit} 기회"
            ],
            'feature': [
                "{service}의 특별한 {feature}로 {keyword} 시작하기",
                "{keyword} {feature} 노하우 - {service} 가이드",
                "{feature} 핵심만 쏙쏙 - {service} {keyword} 완벽 가이드"
            ],
            'question': [
                "{keyword} 고민이라면? {service}에서 해결!",
                "{keyword} 어떻게 시작할까? {service} 완벽 가이드",
                "{keyword} 궁금증 해결! {service} 현직자 조언"
            ]
        }
        
        # 부제목 패턴
        self.subtitle_patterns = [
            "현직자가 알려주는 {keyword} 성공 노하우",
            "{benefit} 기회를 놓치지 마세요",
            "{service}에서만 제공하는 특별한 혜택"
        ]
        
    def generate_titles(self, 
                       intro_content: SectionContent,
                       main_content: SectionContent) -> TitleSet:
        """제목 세트 생성"""
        # 서비스 정보 추출
        service_name = self.context.service.name
        
        # 혜택 정보 추출
        benefits = self.context.service.benefits
        benefit = benefits[0] if benefits else "혜택"
        
        # 기능 정보 추출
        features = self.context.service.features
        feature = features[0] if features else "기능"
        
        # 제목 생성
        title_vars = {
            'year': self.current_year,
            'keyword': self.context.keyword,
            'service': service_name,
            'benefit': benefit,
            'feature': feature
        }
        
        # 패턴 선택 및 적용
        main_title = self.title_patterns['benefit'][0].format(**title_vars)
        sub_title = self.subtitle_patterns[0].format(**title_vars)
        seo_title = f"{self.context.keyword} - {service_name} | {benefit}"
        
        # 메타 설명 생성
        meta_description = (
            f"{self.context.keyword}로 {benefit}을 경험해보세요. "
            f"{service_name}에서 제공하는 {feature} 기능으로 "
            f"더 나은 서비스를 만나보실 수 있습니다."
        )
        
        return TitleSet(
            main_title=main_title,
            sub_title=sub_title,
            seo_title=seo_title,
            meta_description=meta_description
        )
        
    def _extract_benefits(self, 
                         intro_content: SectionContent,
                         main_content: SectionContent) -> List[str]:
        """혜택 관련 키워드 추출"""
        benefits = []
        
        # 서비스 혜택 추가
        benefits.extend(self.context.service.benefits)
        
        # 문장에서 혜택 관련 키워드 추출
        benefit_keywords = ['수입', '급여', '혜택', '기회', '지원']
        for paragraph in intro_content.paragraphs + main_content.paragraphs:
            for keyword in benefit_keywords:
                if keyword in paragraph:
                    benefits.append(paragraph.split(keyword)[0] + keyword)
                    
        return list(set(benefits))[:3]  # 중복 제거 후 상위 3개
        
    def _extract_features(self, main_content: SectionContent) -> List[str]:
        """특징 관련 키워드 추출"""
        features = []
        
        # 서비스 특징 추가
        features.extend(self.context.service.features)
        
        # 문장에서 특징 관련 키워드 추출
        feature_keywords = ['특징', '장점', '특별', '차별']
        for paragraph in main_content.paragraphs:
            for keyword in feature_keywords:
                if keyword in paragraph:
                    features.append(paragraph.split(keyword)[0] + keyword)
                    
        return list(set(features))[:3]  # 중복 제거 후 상위 3개
        
    def _generate_main_title(self, 
                           benefits: List[str],
                           features: List[str]) -> str:
        """메인 제목 생성"""
        import random
        
        # 패턴 선택
        pattern_type = random.choice(['benefit', 'feature', 'question'])
        pattern = random.choice(self.title_patterns[pattern_type])
        
        # 변수 설정
        variables = {
            'year': self.current_year,
            'keyword': self.context.keyword,
            'service': self.context.service.name,
            'benefit': random.choice(benefits) if benefits else '놓칠 수 없는 혜택',
            'feature': random.choice(features) if features else '특별한 기회'
        }
        
        # 제목 생성
        title = pattern.format(**variables)
        
        # 길이 제한 (45자)
        if len(title) > 45:
            title = title[:42] + "..."
            
        return title
        
    def _generate_sub_title(self, benefits: List[str]) -> str:
        """부제목 생성"""
        import random
        
        pattern = random.choice(self.subtitle_patterns)
        
        variables = {
            'keyword': self.context.keyword,
            'service': self.context.service.name,
            'benefit': random.choice(benefits) if benefits else '특별한 혜택'
        }
        
        return pattern.format(**variables)
        
    def _generate_seo_title(self, main_title: str) -> str:
        """SEO 제목 생성"""
        # 기본 형식: [키워드] 메인제목 | 회사명
        return f"[{self.context.keyword}] {main_title} | {self.context.service.name}"
        
    def _generate_meta_description(self,
                                 intro_content: SectionContent,
                                 main_content: SectionContent) -> str:
        """메타 설명 생성"""
        # 첫 번째 단락과 주요 혜택 조합
        description = []
        
        if intro_content.paragraphs:
            description.append(intro_content.paragraphs[0])
            
        if main_content.service_connection:
            description.append(main_content.service_connection)
            
        full_description = " ".join(description)
        
        # 길이 제한 (160자)
        if len(full_description) > 160:
            full_description = full_description[:157] + "..."
            
        return full_description
