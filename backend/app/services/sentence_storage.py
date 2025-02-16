import json
import os
from datetime import datetime
from typing import Dict, List
from dataclasses import asdict
from .sentence_classifier import ClassifiedSentence

class SentenceStorage:
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        
        self.classified_dir = os.path.join(base_dir, 'classified')
        os.makedirs(self.classified_dir, exist_ok=True)
    
    def save_classified_sentences(self, keyword: str, classified_data: Dict[str, List[ClassifiedSentence]]) -> str:
        """분류된 문장들을 JSON 파일로 저장"""
        # 현재 시간을 파일명에 포함
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'classified_{timestamp}_{keyword}.json'
        filepath = os.path.join(self.classified_dir, filename)
        
        # ClassifiedSentence 객체를 dict로 변환
        output_data = {
            'keyword': keyword,
            'timestamp': timestamp,
            'categories': {}
        }
        
        for category, sentences in classified_data.items():
            output_data['categories'][category] = [asdict(sent) for sent in sentences]
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        return filepath
    
    def load_classified_sentences(self, filepath: str) -> Dict[str, List[ClassifiedSentence]]:
        """저장된 JSON 파일에서 분류된 문장들을 로드"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # dict를 ClassifiedSentence 객체로 변환
        classified_data = {}
        for category, sentences in data['categories'].items():
            classified_data[category] = [
                ClassifiedSentence(
                    text=sent['text'],
                    category=sent['category'],
                    confidence=sent['confidence'],
                    keywords=sent['keywords'],
                    sentiment=sent['sentiment'],
                    quality_score=sent['quality_score']
                ) for sent in sentences
            ]
        
        return classified_data
