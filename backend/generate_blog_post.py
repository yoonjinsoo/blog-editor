from app.services.post_generator.blog_post_generator import BlogPostGenerator
from app.services.content_context.content_context import ContentContext, ServiceInfo
import json
from pathlib import Path
import datetime

def main():
    # 1. 수집된 데이터 로드
    data_path = Path("app/data/collected/20250209_174644_퀵플렉스.json")
    with open(data_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 2. 컨텍스트 설정
    service_info = ServiceInfo(
        name="퀵플렉스",
        features=["자동화", "효율성", "사용자 친화적"],
        benefits=["시간 절약", "비용 절감", "생산성 향상"],
        connection_points=["업무 자동화", "프로세스 최적화", "시스템 통합"]
    )
    
    content_context = ContentContext(
        keyword="퀵플렉스",
        service=service_info,
        target_audience="기업 관리자",
        tone="professional",
        company="퀵플렉스",
        contact_info="contact@quickflex.com"
    )
    
    # 3. 블로그 포스트 생성기 초기화
    generator = BlogPostGenerator(content_context)
    
    # 4. 포스트 생성
    post = generator.generate_post(raw_data)
    
    # 5. 결과 저장
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = Path(f"generated_posts/{timestamp}_퀵플렉스_post.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(post.to_dict(), f, ensure_ascii=False, indent=2)
    
    print(f"블로그 포스트가 생성되었습니다: {output_path}")
    
    # HTML 파일도 생성
    html_path = output_path.with_suffix('.html')
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{post.title}</title>
    <meta name="description" content="{post.meta['description']}">
    <meta name="keywords" content="{', '.join(post.meta['keywords'])}">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }}
        h1, h2, h3 {{
            color: #2c3e50;
        }}
        .meta {{
            color: #7f8c8d;
            font-size: 0.9em;
            margin-bottom: 20px;
        }}
        .content {{
            margin-top: 30px;
        }}
        .footer {{
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 0.9em;
            color: #7f8c8d;
        }}
    </style>
</head>
<body>
    <h1>{post.title}</h1>
    <div class="meta">
        <p>작성자: {post.meta['author']} | 작성일: {post.meta['date']}</p>
    </div>
    <div class="content">
        <h2>{post.content['subtitle']}</h2>
        {post.content['body']}
    </div>
    <div class="footer">
        <p>카테고리: {post.footer['category']}</p>
        <p>태그: {post.footer['tags']}</p>
    </div>
</body>
</html>
""")
    
    print(f"HTML 파일이 생성되었습니다: {html_path}")
    
    # HTML 파일 열기
    import os
    os.startfile(str(html_path))

if __name__ == "__main__":
    main()
