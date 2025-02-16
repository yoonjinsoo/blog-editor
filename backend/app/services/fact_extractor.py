import spacy
from typing import List, Dict, Any
import re
import logging
import json
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class FactExtractor:
    def __init__(self):
        """한국어 언어 모델로 FactExtractor를 초기화합니다."""
        try:
            self.nlp = spacy.load("ko_core_news_lg")
        except OSError:
            spacy.cli.download("ko_core_news_lg")
            self.nlp = spacy.load("ko_core_news_lg")

    def extract_facts_from_json(self, json_file_path: str) -> str:
        """JSON 파일에서 사실 정보를 추출하고 새로운 JSON 파일로 저장합니다.
        
        Args:
            json_file_path (str): 처리할 JSON 파일 경로
            
        Returns:
            str: 저장된 facts JSON 파일 경로
        """
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 블로그/뉴스 결과 추출
            blog_results = []
            if isinstance(data, dict):
                if 'blog_results' in data:
                    blog_results.extend(data['blog_results'])
                if 'news_results' in data:
                    blog_results.extend(data['news_results'])
            
            # 각 결과에서 문장 추출
            facts = []
            for result in blog_results:
                if 'content' in result:
                    text = result['content']
                    # HTML 태그 제거
                    text = re.sub(r'<[^>]+>', '', text)
                    # 문장 추출
                    sentences = self.extract_facts(text)
                    facts.extend(sentences)
            
            # 결과를 JSON으로 저장
            output_filename = os.path.basename(json_file_path)
            output_dir = os.path.join(os.path.dirname(os.path.dirname(json_file_path)), 'facts')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f'facts_{output_filename}')
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'source_file': json_file_path,
                    'timestamp': datetime.now().isoformat(),
                    'facts': facts
                }, f, ensure_ascii=False, indent=2)
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error processing {json_file_path}: {str(e)}")
            raise

    def extract_facts(self, text: str) -> List[Dict[str, Any]]:
        """텍스트에서 문장을 추출합니다.
        
        Args:
            text (str): 처리할 텍스트
            
        Returns:
            List[Dict[str, Any]]: 추출된 문장 리스트
        """
        # 텍스트 전처리
        text = re.sub(r'\s+', ' ', text.strip())
        
        # spaCy로 문장 분리
        doc = self.nlp(text)
        
        facts = []
        for sent in doc.sents:
            sent_text = sent.text.strip()
            if sent_text:
                facts.append({
                    'sentence': sent_text,
                    'length': len(sent_text),
                    'entities': [
                        {
                            'text': ent.text,
                            'label': ent.label_
                        }
                        for ent in sent.ents
                    ]
                })
        
        return facts
