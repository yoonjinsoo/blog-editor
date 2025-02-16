from typing import Dict, List, Any
import re
import os
import json
from datetime import datetime

class FactExtractor:
    def extract_structured_facts(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """원본 데이터에서 구조화된 팩트 추출"""
        facts = {
            'core_facts': [],
            'statistics': [],
            'expert_quotes': [],
            'examples': [],
            'references': []
        }
        
        for item in raw_data:
            content = item.get('full_content', '')
            if not content:
                continue
                
            # 핵심 사실 추출
            facts['core_facts'].append({
                'text': content,
                'source': item.get('blog_name', ''),
                'date': item.get('post_date', '')
            })
            
            # 참조 추가
            if item.get('link'):
                facts['references'].append({
                    'url': item['link'],
                    'title': item.get('title', ''),
                    'blog_name': item.get('blog_name', '')
                })
        
        return facts
    
    def _extract_core_facts(self, text: str) -> List[str]:
        """핵심 사실 추출"""
        facts = []
        
        # 문장 단위로 분리
        sentences = re.split(r'[.!?][ \t]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            # 핵심 사실로 보이는 문장 선택
            if len(sentence) > 20 and len(sentence) < 100:
                if any(keyword in sentence for keyword in ['은', '는', '이란', '란', '특징', '장점']):
                    facts.append(sentence)
        
        return facts[:5]  # 상위 5개만 선택
    
    def _extract_statistics(self, text: str) -> List[str]:
        """통계 데이터 추출"""
        stats = []
        
        # 숫자가 포함된 문장 찾기
        number_pattern = r'\d+(?:[,.]\d+)?(?:\s*[%만천억원]|\s*개월|\s*시간|\s*분|\s*초)?'
        sentences = re.split(r'[.!?]\s+', text)
        
        for sentence in sentences:
            if re.search(number_pattern, sentence):
                sentence = sentence.strip()
                if len(sentence) > 10 and len(sentence) < 150:
                    stats.append(sentence)
        
        return stats[:5]  # 상위 5개만 선택
    
    def _extract_expert_quotes(self, text: str) -> List[str]:
        """전문가 인용구 추출"""
        quotes = []
        
        # 인용구로 보이는 패턴 찾기
        quote_patterns = [
            r'"([^"]+)"',
            r'\'([^\']+)\'',
            r'[""]([^""]+)[""]'
        ]
        
        for pattern in quote_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 20 and len(match) < 200:
                    quotes.append(match.strip())
        
        return quotes[:3]  # 상위 3개만 선택
    
    def _extract_examples(self, text: str) -> List[str]:
        """예시 추출"""
        examples = []
        
        # 예시 문구 패턴
        example_patterns = [
            r'예를\s+들[면어]([^.!?]+)[.!?]',
            r'예시로([^.!?]+)[.!?]',
            r'사례로([^.!?]+)[.!?]',
            r'경우에는([^.!?]+)[.!?]'
        ]
        
        for pattern in example_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) > 20 and len(match) < 200:
                    examples.append(match.strip())
        
        return examples[:3]  # 상위 3개만 선택

    def save_facts(self, facts: Dict[str, Any], output_dir: str, keyword: str) -> str:
        """추출된 팩트를 파일로 저장"""
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{keyword}_facts.json"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(facts, f, ensure_ascii=False, indent=2)
        
        return filepath
