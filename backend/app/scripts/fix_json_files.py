import json
import os
from pathlib import Path
import re

def clean_text(text: str) -> str:
    """텍스트에서 HTML 태그와 특수 문자를 제거합니다."""
    if not isinstance(text, str):
        return text
        
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수 문자 처리
    text = text.replace('​', '')  # 제로 너비 공백 제거
    text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)  # 제어 문자 제거
    
    return text

def clean_json_content(data):
    """JSON 데이터의 모든 문자열 값을 정제합니다."""
    if isinstance(data, dict):
        return {k: clean_json_content(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [clean_json_content(item) for item in data]
    elif isinstance(data, str):
        return clean_text(data)
    return data

def fix_json_file(file_path: str) -> None:
    """JSON 파일의 형식을 수정하고 인코딩 문제를 해결합니다."""
    try:
        # UTF-8로 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 데이터 정제
        cleaned_data = clean_json_content(data)
        
        # 정제된 데이터를 UTF-8로 저장
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully fixed {file_path}")
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")

def fix_all_json_files():
    """수집된 데이터 디렉토리의 모든 JSON 파일을 처리합니다."""
    data_dir = Path(__file__).parent.parent / 'data' / 'collected'
    
    for json_file in data_dir.glob('*.json'):
        fix_json_file(str(json_file))

if __name__ == '__main__':
    fix_all_json_files()
