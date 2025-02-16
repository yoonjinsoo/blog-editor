import json
import time
from pathlib import Path
from typing import Dict, Any

from ..services.post_generator.blog_post_generator import BlogPostGenerator
from ..services.content_context.content_context import ContentContext, ServiceInfo

def load_data(file_path: str) -> Dict[str, Any]:
    """데이터 파일 로드"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    """메인 함수"""
    try:
        # 1. 데이터 로드
        data_path = Path(__file__).parent.parent / 'data' / 'collected' / '20250209_174644_퀵플렉스.json'
        data = load_data(str(data_path))
        
        # 2. 서비스 정보 설정
        service_info = ServiceInfo(
            name="쿠팡 퀵플렉스",
            features=["당일 배송", "실시간 배송 추적", "안전한 포장"],
            benefits=["빠른 배송", "편리한 관리", "비용 절감"],
            connection_points=["배송", "관리", "비용"]
        )
        
        # 3. 컨텍스트 설정
        context = ContentContext(
            keyword="쿠팡 퀵플렉스",
            service=service_info,
            target_audience="일반",
            tone="정보성",
            company="쿠팡",
            contact_info="1577-7011"
        )
        
        # 4. 블로그 포스트 생성기 초기화
        generator = BlogPostGenerator(context)
        
        # 5. 시작 시간 기록
        start_time = time.time()
        
        # 6. 포스트 생성
        post = generator.generate_post(data)
        
        # 7. 소요 시간 계산
        elapsed_time = time.time() - start_time
        
        # 8. 결과 출력
        print("\n" + "=" * 50)
        print("포스트 생성 결과")
        print("=" * 50)
        print(f"상태: success")
        print(f"소요 시간: {elapsed_time:.2f}초\n")
        
        # 9. 생성된 포스트 저장
        output_path = Path(__file__).parent.parent / 'data' / 'generated' / 'test_post.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(post, f, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print("\n" + "=" * 50)
        print("포스트 생성 결과")
        print("=" * 50)
        print(f"상태: error")
        print(f"소요 시간: {time.time() - start_time:.2f}초\n")
        print(f"오류: 포스트 생성 중 오류 발생: {str(e)}")

if __name__ == '__main__':
    main()
