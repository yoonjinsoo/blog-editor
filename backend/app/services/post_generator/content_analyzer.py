from typing import Dict, List, Any
import re

class ContentAnalyzer:
    def analyze_materials(self, materials: Dict[str, Any]) -> Dict[str, Any]:
        """검색 결과 분석"""
        try:
            analyzed = {
                'keyword': materials.get('keyword', ''),
                'topics': [],
                'key_points': [],
                'references': []
            }
            
            # 블로그 결과 분석
            for result in materials.get('blog_results', []):
                if result.get('title') and result.get('description'):
                    analyzed['topics'].append({
                        'title': result['title'],
                        'summary': result['description'][:100],
                        'source': 'blog',
                        'url': result.get('link', '')
                    })
            
            # 뉴스 결과 분석
            for result in materials.get('news_results', []):
                if result.get('title') and result.get('description'):
                    analyzed['key_points'].append({
                        'title': result['title'],
                        'content': result['description'][:100],
                        'source': 'news',
                        'url': result.get('link', '')
                    })
            
            # 참조 정보 수집
            analyzed['references'] = [
                {
                    'title': result.get('title', ''),
                    'url': result.get('link', ''),
                    'source': result.get('source', 'unknown')
                }
                for result in materials.get('blog_results', []) + materials.get('news_results', [])
                if result.get('title') and result.get('link')
            ][:5]  # 상위 5개만 유지
            
            return analyzed
            
        except Exception as e:
            print(f"Error in analyze_materials: {str(e)}")
            return {
                'keyword': materials.get('keyword', ''),
                'topics': [],
                'key_points': [],
                'references': []
            }

    def _extract_key_facts(self, content: str) -> List[str]:
        facts = []
        patterns = [
            r'중국이[^.]*\.',
            r'미국[^.]*대응[^.]*\.',
            r'\d+억[^.]*\.',
            r'(?:발표|출시|개발)[^.]*\.'
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            facts.extend(match.group(0).strip() for match in matches)
        return list(set(facts))[:5]

    def _extract_statistics(self, content: str) -> List[Dict]:
        stats = []
        pattern = r'(\d+(?:,\d+)*(?:\.\d+)?)\s*([%만원억천달러]|\w+)(?:[^.]*?(?:성공률|비용|금액|시장|규모))?[^.]*\.'
        matches = re.finditer(pattern, content)
        for match in matches:
            context = content[max(0, match.start()-30):min(len(content), match.end()+30)]
            if any(keyword in context for keyword in ['성공률', '비용', '금액', '시장', '규모']):
                stats.append({
                    'number': match.group(1),
                    'unit': match.group(2),
                    'context': context.strip()
                })
        return stats[:5]

    def _extract_expert_quotes(self, content: str) -> List[Dict]:
        quotes = []
        patterns = [
            r'([^"]*(?:CEO|대표|전문가|연구[팀원])[^"]*)\s*[은는이가]\s*"([^"]+)"(?:라고|이라고)\s*(?:말했|밝혔|전했)',
            r'"([^"]+)"\s*라고\s*([^은는이가]+(?:CEO|대표|전문가|연구[팀원])[^은는이가]*)'
        ]
        for pattern in patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                quotes.append({
                    'speaker': match.group(1).strip(),
                    'quote': match.group(2).strip(),
                    'context': content[max(0, match.start()-30):min(len(content), match.end()+30)]
                })
        return quotes[:3]

    def _extract_trends(self, content: str) -> List[str]:
        trends = []
        indicators = ['전략', '대응', '총공세', '패권', '경쟁', '트렌드', '동향']
        for indicator in indicators:
            pattern = f'[^.]*{indicator}[^.]*\.'
            matches = re.finditer(pattern, content)
            trends.extend(match.group(0).strip() for match in matches)
        return list(set(trends))[:3]

    def _extract_case_studies(self, content: str) -> List[Dict]:
        cases = []
        companies = ['오픈AI', '구글', '메타', '앤스로픽', '딥시크']
        for company in companies:
            pattern = f'{company}[^.]*(?:전략|대응|계획|출시)[^.]*\.'
            matches = re.finditer(pattern, content)
            for match in matches:
                cases.append({
                    'entity': company,
                    'description': match.group(0).strip()
                })
        return cases[:3]
