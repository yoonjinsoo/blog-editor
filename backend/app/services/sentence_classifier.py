from typing import List, Dict, Any
from dataclasses import dataclass
from .lm_studio_client import LMStudioClient

@dataclass
class ClassifiedSentence:
    text: str
    category: str  # usage, benefits, features, costs, reviews
    confidence: float
    keywords: List[str]
    sentiment: float
    quality_score: float

class SentenceClassifier:
    def __init__(self):
        self.lm_client = LMStudioClient()
        
        # 카테고리별 프롬프트
        self.category_prompts = {
            'usage': "이 문장이 제품/서비스의 사용 방법이나 절차를 설명하고 있나요?",
            'benefits': "이 문장이 제품/서비스의 장점이나 이점을 설명하고 있나요?",
            'features': "이 문장이 제품/서비스의 특징이나 기능을 설명하고 있나요?",
            'costs': "이 문장이 제품/서비스의 가격이나 비용을 설명하고 있나요?",
            'reviews': "이 문장이 제품/서비스에 대한 사용자 후기나 평가를 포함하고 있나요?"
        }
    
    def classify_sentence(self, sentence: str) -> str:
        """문장을 카테고리로 분류"""
        prompt = f"""주어진 문장을 다음 카테고리 중 하나로 분류해주세요.

문장: "{sentence}"

가능한 카테고리:
usage - 제품/서비스의 사용 방법이나 절차를 설명
benefits - 제품/서비스의 장점이나 이점을 설명
features - 제품/서비스의 특징이나 기능을 설명
costs - 제품/서비스의 가격이나 비용을 설명
reviews - 제품/서비스에 대한 사용자 후기나 평가

답변 형식: 카테고리명만 정확히 입력 (예: usage)

답변:"""
        
        response = self.lm_client._generate_response(prompt)
        if not response:
            return None
            
        # 응답에서 카테고리 추출
        categories = ['usage', 'benefits', 'features', 'costs', 'reviews']
        response = response.lower().strip()
        for category in categories:
            if category in response:
                return category
        return None
    
    def analyze_sentence(self, sentence: str, category: str) -> ClassifiedSentence:
        """문장 상세 분석"""
        prompt = f"""다음 문장을 분석하여 JSON 형식으로 결과를 출력해주세요.

문장: "{sentence}"
카테고리: {category}

분석해야 할 항목:
1. confidence (신뢰도): 0.0~1.0 사이의 값
2. keywords (핵심 키워드): 문장에서 추출한 중요 단어들의 배열
3. sentiment (감성 점수): -1.0(매우 부정)~1.0(매우 긍정) 사이의 값
4. quality_score (품질 점수): 0.0~1.0 사이의 값

답변 형식:
{{
    "confidence": 0.0~1.0,
    "keywords": ["키워드1", "키워드2", ...],
    "sentiment": -1.0~1.0,
    "quality_score": 0.0~1.0
}}

답변:"""
        
        response = self.lm_client._generate_response(prompt)
        if not response:
            return None
            
        # JSON 형식이 아닐 경우를 대비한 기본값
        result = {
            "confidence": 0.8,  # 기본 신뢰도
            "keywords": [word.strip() for word in sentence.split() if len(word.strip()) > 1],  # 기본 키워드
            "sentiment": 0.0,  # 중립
            "quality_score": 0.7  # 기본 품질 점수
        }
        
        try:
            # JSON 응답 파싱 시도
            import json
            import re
            
            # JSON 부분만 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # 유효한 값만 업데이트
                if isinstance(parsed.get('confidence'), (int, float)):
                    result['confidence'] = float(parsed['confidence'])
                if isinstance(parsed.get('keywords'), list):
                    result['keywords'] = parsed['keywords']
                if isinstance(parsed.get('sentiment'), (int, float)):
                    result['sentiment'] = float(parsed['sentiment'])
                if isinstance(parsed.get('quality_score'), (int, float)):
                    result['quality_score'] = float(parsed['quality_score'])
        except:
            pass  # 파싱 실패 시 기본값 사용
            
        return ClassifiedSentence(
            text=sentence,
            category=category,
            confidence=result['confidence'],
            keywords=result['keywords'],
            sentiment=result['sentiment'],
            quality_score=result['quality_score']
        )
