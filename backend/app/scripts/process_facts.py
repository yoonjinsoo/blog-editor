import os
import json
import logging
from pathlib import Path
import spacy
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_sentences(text):
    """텍스트에서 문장을 추출합니다."""
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    # 연속된 공백 제거
    text = re.sub(r'\s+', ' ', text.strip())
    
    # spaCy로 문장 분리
    nlp = spacy.load("ko_core_news_lg")
    doc = nlp(text)
    
    sentences = []
    for sent in doc.sents:
        sent_text = sent.text.strip()
        if sent_text:
            sentences.append({
                'text': sent_text,
                'entities': [{'text': ent.text, 'label': ent.label_} for ent in sent.ents]
            })
    
    return sentences

def process_collected_files():
    """수집된 파일들에서 문장을 추출하고 저장합니다."""
    try:
        # 기본 디렉토리 설정
        base_dir = Path(__file__).parent.parent
        collected_dir = base_dir / 'data' / 'collected'
        facts_dir = base_dir / 'data' / 'facts'
        facts_dir.mkdir(exist_ok=True)
        
        # collected 디렉토리의 모든 JSON 파일 처리
        for json_file in collected_dir.glob('*.json'):
            try:
                logger.info(f"Processing file: {json_file}")
                
                # JSON 파일 읽기
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 블로그/뉴스 결과 추출
                contents = []
                if isinstance(data, dict):
                    if 'blog_results' in data:
                        for item in data['blog_results']:
                            content = item.get('full_content', '') or item.get('content', '')
                            if content:
                                contents.append(content)
                    if 'news_results' in data:
                        for item in data['news_results']:
                            content = item.get('full_content', '') or item.get('content', '')
                            if content:
                                contents.append(content)
                
                # 각 컨텐츠에서 문장 추출
                all_sentences = []
                for content in contents:
                    if content:
                        sentences = extract_sentences(content)
                        all_sentences.extend(sentences)
                
                # 결과를 텍스트 파일로 저장
                output_file = facts_dir / f"facts_{json_file.name}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    for sent in all_sentences:
                        f.write(f"문장: {sent['text']}\n")
                        if sent['entities']:
                            f.write("개체명:\n")
                            for ent in sent['entities']:
                                f.write(f"  - {ent['text']} ({ent['label']})\n")
                        f.write("\n")
                
                logger.info(f"Successfully processed {json_file}. Results saved to: {output_file}")
                
            except Exception as e:
                logger.error(f"Error processing file {json_file}: {str(e)}")
                continue
                
    except Exception as e:
        logger.error(f"Error in process_collected_files: {str(e)}")
        raise

if __name__ == "__main__":
    process_collected_files()
