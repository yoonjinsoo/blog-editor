from typing import Dict, Any, Optional
from openai import OpenAI

class LMStudioClient:
    def __init__(self, base_url="http://localhost:1234/v1"):  # /v1 추가
        self.base_url = base_url
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        
    def generate_title(self, facts: Dict[str, Any]) -> str:
        prompt = """
        다음 정보를 바탕으로 SEO 최적화된 블로그 제목을 생성해주세요:
        - 이모지 1-2개 사용
        - 핵심 키워드를 앞부분에 배치
        - 구체적인 수치나 혜택 포함
        - 전체 길이 30-45자 유지
        
        정보:
        {facts}
        
        제목 형식:
        [핵심 키워드] [구체적 수치/혜택] - [추가 정보]
        """
        
        response = self._generate_response(prompt.format(facts=facts))
        return response.strip()

    def write_blog_section(self, facts: Dict[str, Any], section_type: str) -> Optional[str]:
        section_prompts = {
            "intro": """
            다음 정보를 바탕으로 블로그 도입부를 작성해주세요:
            - 첫 3줄이 검색결과에 노출됨을 고려
            - 핵심 메시지를 먼저 전달
            - 신뢰성 있는 데이터나 통계 포함
            - 독자의 관심을 유도하는 문구
            - 자연스러운 키워드 포함 (2-3회)
            
            정보:
            {facts}
            """,
            
            "main": """
            다음 정보를 바탕으로 블로그 본문을 작성해주세요:
            - 섹션별로 이모지로 구분
            - 각 섹션은 4줄 이내로 작성
            - 내부/외부 링크 자연스럽게 포함
            - 리스트나 표 형식 활용
            - 구체적인 데이터와 예시 포함
            
            정보:
            {facts}
            """,
            
            "qa": """
            다음 정보를 바탕으로 자주 묻는 질문 섹션을 작성해주세요:
            - 실제 사용자들이 자주 묻는 질문 5-7개
            - 각 답변은 100-200자 내외
            - 질문에 핵심 키워드 포함
            - 답변은 구체적이고 실용적으로
            
            정보:
            {facts}
            """,
            
            "conclusion": """
            다음 정보를 바탕으로 블로그 결론을 작성해주세요:
            - 핵심 내용 요약
            - 구체적인 행동 유도 문구
            - 연락처나 신청 방법 안내
            - 자연스러운 키워드 마무리
            
            정보:
            {facts}
            """
        }
        
        if section_type not in section_prompts:
            return None
            
        prompt = section_prompts[section_type]
        response = self._generate_response(prompt.format(facts=facts))
        return response.strip()

    def _generate_response(self, prompt: str) -> str:
        try:
            completion = self.client.completions.create(
                model="local-model",
                prompt=prompt,
                temperature=0.7,
                max_tokens=2000,
                stream=False
            )
            
            # 응답 디버깅
            print("Raw response:", completion)
            
            if completion is None:
                print("Warning: Received None response from LM Studio")
                return ""
                
            if not hasattr(completion, 'choices'):
                print("Warning: Response has no 'choices' attribute")
                return ""
                
            if not completion.choices:
                print("Warning: Response has empty choices")
                return ""
                
            text = completion.choices[0].text
            if not text:
                print("Warning: Choice has no text")
                return ""
                
            return text.strip()
                
        except Exception as e:
            print(f"Error generating response: {e}")
            import traceback
            print("Traceback:", traceback.format_exc())
            return ""
            
# 테스트 코드
if __name__ == "__main__":
    client = LMStudioClient()
    
    # 간단한 테스트
    test_prompt = "인공지능에 대해 100자 내외로 설명해주세요."
    result = client._generate_response(test_prompt)
    
    if result:
        print("테스트 성공!")
        print("결과:", result)
    else:
        print("테스트 실패!")
