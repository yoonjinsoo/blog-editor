from typing import Dict, List, Any

class BlogPostWriter:
    def create_post(self, materials: Dict[str, Any], keyword: str) -> Dict[str, Any]:
        """분석된 자료를 바탕으로 블로그 포스트 생성"""
        try:
            post = {
                'title': self._generate_title(keyword, materials.get('topics', [])),
                'introduction': self._generate_introduction(keyword, materials),
                'main_content': self._generate_main_content(materials),
                'conclusion': self._generate_conclusion(keyword, materials),
                'references': materials.get('references', [])
            }
            return post
            
        except Exception as e:
            print(f"Error in create_post: {str(e)}")
            return {
                'title': f"{keyword} 관련 정보",
                'introduction': "소개글을 생성하지 못했습니다.",
                'main_content': [],
                'conclusion': "결론을 생성하지 못했습니다.",
                'references': []
            }
    
    def _generate_title(self, keyword: str, topics: List[Dict]) -> str:
        """제목 생성"""
        if not topics:
            return f"{keyword} 완벽 가이드"
            
        return f"{keyword} - {topics[0].get('title', '관련 정보')}"
    
    def _generate_introduction(self, keyword: str, materials: Dict) -> str:
        """소개글 생성"""
        topics = materials.get('topics', [])
        if not topics:
            return f"{keyword}에 대해 알아보겠습니다."
            
        return f"{keyword}에 대한 상세한 정보를 알아보겠습니다. " + \
               topics[0].get('summary', '')
    
    def _generate_main_content(self, materials: Dict) -> List[Dict]:
        """본문 내용 생성"""
        content = []
        
        # 주요 토픽 섹션
        topics = materials.get('topics', [])
        if topics:
            content.append({
                'type': 'section',
                'title': '주요 내용',
                'content': '\n'.join([
                    f"- {topic.get('title', '')}: {topic.get('summary', '')}"
                    for topic in topics[:3]
                ])
            })
        
        # 핵심 포인트 섹션
        key_points = materials.get('key_points', [])
        if key_points:
            content.append({
                'type': 'section',
                'title': '핵심 포인트',
                'content': '\n'.join([
                    f"- {point.get('title', '')}: {point.get('content', '')}"
                    for point in key_points[:3]
                ])
            })
        
        return content
    
    def _generate_conclusion(self, keyword: str, materials: Dict) -> str:
        """결론 생성"""
        topics = materials.get('topics', [])
        if not topics:
            return f"{keyword}에 대해 알아보았습니다."
            
        return f"{keyword}에 대해 자세히 알아보았습니다. " + \
               "더 자세한 정보는 참고 자료를 확인해주세요."