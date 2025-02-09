from typing import Dict, List, Tuple

class QualityChecker:
    def validate_post(self, post: Dict) -> Tuple[bool, List[str]]:
        """포스트 품질 검사"""
        issues = []
        
        # 제목 검사
        if not post.get('title'):
            issues.append("제목이 없습니다.")
        elif len(post['title']) < 10:
            issues.append("제목이 너무 짧습니다.")
        elif len(post['title']) > 100:
            issues.append("제목이 너무 깁니다.")
        
        # 소개글 검사
        if not post.get('introduction'):
            issues.append("소개글이 없습니다.")
        elif len(post['introduction']) < 50:
            issues.append("소개글이 너무 짧습니다.")
        
        # 본문 검사
        main_content = post.get('main_content', [])
        if not main_content:
            issues.append("본문 내용이 없습니다.")
        else:
            total_content_length = sum(
                len(section.get('content', '')) 
                for section in main_content
            )
            if total_content_length < 200:
                issues.append("본문 내용이 너무 짧습니다.")
        
        # 결론 검사
        if not post.get('conclusion'):
            issues.append("결론이 없습니다.")
        elif len(post['conclusion']) < 30:
            issues.append("결론이 너무 짧습니다.")
        
        # 참조 검사
        if not post.get('references'):
            issues.append("참조 자료가 없습니다.")
        
        return len(issues) == 0, issues
    
    def _check_structure(self, post: Dict) -> List[str]:
        issues = []
        
        if not post.get('title'):
            issues.append("제목이 없습니다")
        
        if not post.get('intro', {}).get('text'):
            issues.append("도입부가 없습니다")
            
        main_content = post.get('main_content', [])
        if len(main_content) < 3:
            issues.append("본문 섹션이 최소 3개 이상 필요합니다")
            
        if not post.get('conclusion', {}).get('text'):
            issues.append("결론이 없습니다")
            
        return issues
    
    def _check_content_quality(self, post: Dict) -> List[str]:
        issues = []
        
        # 전체 단어 수 확인
        total_words = self._count_total_words(post)
        if total_words < 800:
            issues.append(f"전체 글자 수가 부족합니다 (현재: {total_words}, 최소: 800)")
        elif total_words > 2000:
            issues.append(f"전체 글자 수가 너무 많습니다 (현재: {total_words}, 최대: 2000)")
            
        # 전문성 검증
        if not self._has_expert_content(post):
            issues.append("전문가 인용구나 통계 자료가 부족합니다")
            
        # 가독성 검증
        readability_issues = self._check_readability(post)
        issues.extend(readability_issues)
        
        return issues
    
    def _check_seo_optimization(self, post: Dict) -> List[str]:
        issues = []
        
        # 메타 정보 검증
        meta = post.get('meta', {})
        if not meta.get('description'):
            issues.append("메타 설명이 없습니다")
        elif len(meta['description']) < 50:
            issues.append("메타 설명이 너무 짧습니다")
            
        if not meta.get('tags') or len(meta['tags']) < 3:
            issues.append("태그가 3개 이상 필요합니다")
            
        # 키워드 밀도 검증
        keyword = meta.get('keyword', '')
        if keyword:
            density = self._calculate_keyword_density(post, keyword)
            if density < 0.5:
                issues.append("주요 키워드 사용 빈도가 낮습니다")
            elif density > 3.0:
                issues.append("주요 키워드가 과도하게 사용되었습니다")
                
        return issues
    
    def _count_total_words(self, post: Dict) -> int:
        text_parts = [
            post.get('title', ''),
            post.get('intro', {}).get('text', ''),
            *[section.get('content', '') for section in post.get('main_content', [])],
            post.get('conclusion', {}).get('text', '')
        ]
        return sum(len(re.findall(r'\S+', text)) for text in text_parts)
    
    def _has_expert_content(self, post: Dict) -> bool:
        for section in post.get('main_content', []):
            content = section.get('content', '')
            if '전문가' in content or '통계' in content:
                return True
        return False
    
    def _check_readability(self, post: Dict) -> List[str]:
        issues = []
        
        for section in post.get('main_content', []):
            content = section.get('content', '')
            
            # 문장 길이 검사
            long_sentences = [s for s in re.split(r'[.!?]', content) if len(s.strip()) > 100]
            if long_sentences:
                issues.append("일부 문장이 너무 깁니다")
                
            # 단락 구분 검사
            paragraphs = content.split('\n\n')
            if any(len(p.strip()) > 300 for p in paragraphs):
                issues.append("일부 단락이 너무 깁니다")
                
        return issues
    
    def _calculate_keyword_density(self, post: Dict, keyword: str) -> float:
        total_words = self._count_total_words(post)
        if not total_words:
            return 0.0
            
        keyword_count = sum(
            text.lower().count(keyword.lower())
            for text in [
                post.get('title', ''),
                post.get('intro', {}).get('text', ''),
                *[section.get('content', '') for section in post.get('main_content', [])],
                post.get('conclusion', {}).get('text', '')
            ]
        )
        
        return (keyword_count / total_words) * 100