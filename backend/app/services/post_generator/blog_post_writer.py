from typing import Dict, List, Any
from datetime import datetime

class BlogPostWriter:
    def __init__(self):
        self.current_year = datetime.now().year

    def create_post(self, materials: Dict[str, Any], meta: Dict[str, Any]) -> Dict[str, Any]:
        """새로운 템플릿 구조에 맞춰 블로그 포스트 생성"""
        try:
            post = {
                'meta': self._generate_meta(meta),
                'content': {
                    'title': self._generate_title(meta['main_keyword'], meta.get('benefit', '')),
                    'intro': self._generate_introduction(meta, materials),
                    'main_sections': self._generate_main_sections(materials),
                    'conclusion': self._generate_conclusion(meta, materials)
                },
                'seo': self._generate_seo(meta, materials)
            }
            return post
            
        except Exception as e:
            print(f"Error in create_post: {str(e)}")
            return self._generate_error_post(meta['main_keyword'])

    def _generate_meta(self, meta: Dict[str, Any]) -> Dict[str, Any]:
        """메타 정보 생성"""
        return {
            'category': meta['category'],
            'main_keyword': meta['main_keyword'],
            'sub_keywords': meta.get('sub_keywords', [])[:5],
            'target_audience': meta['target_audience']
        }

    def _generate_title(self, keyword: str, benefit: str) -> str:
        """타이틀 생성 - 템플릿 패턴 활용"""
        patterns = [
            f"{self.current_year} {keyword}로 {benefit} 얻는 방법",
            f"5가지 {keyword} {benefit} 비법",
            f"{keyword} 완벽 가이드: {benefit} 노하우"
        ]
        # TODO: AI 모델을 통해 가장 적절한 패턴 선택
        return patterns[0]

    def _generate_introduction(self, meta: Dict[str, Any], materials: Dict[str, Any]) -> Dict[str, Any]:
        """도입부 생성"""
        return {
            'hook': self._generate_hook(meta['main_keyword']),
            'problem': self._generate_problem(materials),
            'solution_hint': self._generate_solution_hint(meta),
            'overview': self._generate_overview(materials)
        }

    def _generate_main_sections(self, materials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """메인 섹션 생성"""
        sections = []
        main_points = materials.get('main_points', [])[:4]
        
        for point in main_points:
            section = {
                'subtitle': point['title'],
                'content': point['content'],
                'example': point.get('example', ''),
                'image': {
                    'url': '',  # TODO: 이미지 수집기와 연동
                    'alt': f"{point['title']} 관련 이미지",
                    'caption': point['title']
                }
            }
            sections.append(section)
        
        return sections

    def _generate_conclusion(self, meta: Dict[str, Any], materials: Dict[str, Any]) -> Dict[str, Any]:
        """결론 생성"""
        return {
            'summary': self._generate_summary(materials),
            'action_items': self._generate_action_items(materials),
            'engagement': self._generate_engagement_prompt(meta['main_keyword'])
        }

    def _generate_seo(self, meta: Dict[str, Any], materials: Dict[str, Any]) -> Dict[str, Any]:
        """SEO 요소 생성"""
        return {
            'meta_description': self._generate_meta_description(meta, materials),
            'tags': self._generate_tags(meta),
            'internal_links': [],  # TODO: 내부 링크 수집기와 연동
            'external_links': materials.get('references', [])[:3]
        }

    def _generate_error_post(self, keyword: str) -> Dict[str, Any]:
        """에러 발생시 기본 포스트 생성"""
        return {
            'meta': {
                'category': '일반',
                'main_keyword': keyword,
                'sub_keywords': [],
                'target_audience': '일반 사용자'
            },
            'content': {
                'title': f"{keyword} 관련 정보",
                'intro': {
                    'hook': '준비 중입니다.',
                    'problem': '',
                    'solution_hint': '',
                    'overview': ''
                },
                'main_sections': [],
                'conclusion': {
                    'summary': '',
                    'action_items': [],
                    'engagement': ''
                }
            },
            'seo': {
                'meta_description': '',
                'tags': [keyword],
                'internal_links': [],
                'external_links': []
            }
        }

    # Helper methods (실제 구현 필요)
    def _generate_hook(self, keyword: str) -> str:
        # TODO: AI 모델을 통한 훅 생성
        return f"{keyword}에 대해 알아보세요."

    def _generate_problem(self, materials: Dict[str, Any]) -> str:
        # TODO: AI 모델을 통한 문제 제시
        return materials.get('problem', '')

    def _generate_solution_hint(self, meta: Dict[str, Any]) -> str:
        # TODO: AI 모델을 통한 해결책 힌트 생성
        return f"{meta['main_keyword']}를 통한 해결책을 제시합니다."

    def _generate_overview(self, materials: Dict[str, Any]) -> str:
        # TODO: AI 모델을 통한 개요 생성
        return materials.get('overview', '')

    def _generate_summary(self, materials: Dict[str, Any]) -> str:
        # TODO: AI 모델을 통한 요약 생성
        return materials.get('summary', '')

    def _generate_action_items(self, materials: Dict[str, Any]) -> List[str]:
        # TODO: AI 모델을 통한 실천 항목 생성
        return materials.get('action_items', [])

    def _generate_engagement_prompt(self, keyword: str) -> str:
        # TODO: AI 모델을 통한 참여 유도 문구 생성
        return f"{keyword}에 대한 여러분의 경험을 댓글로 공유해주세요!"

    def _generate_meta_description(self, meta: Dict[str, Any], materials: Dict[str, Any]) -> str:
        # TODO: AI 모델을 통한 메타 설명 생성
        return f"{meta['main_keyword']}에 대한 완벽 가이드. {materials.get('overview', '')}"

    def _generate_tags(self, meta: Dict[str, Any]) -> List[str]:
        # TODO: 키워드 확장기를 통한 태그 생성
        tags = [meta['main_keyword']] + meta.get('sub_keywords', [])
        return list(set(tags))[:10]