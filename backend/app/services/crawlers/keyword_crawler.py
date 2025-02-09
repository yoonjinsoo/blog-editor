from .base import BaseCrawler
from typing import Dict, List, Optional, Set
import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
import re
import traceback
import os
import json

logger = logging.getLogger(__name__)

class KeywordCrawler(BaseCrawler):
    # 검색 의도 패턴 정의
    intent_patterns = {
        'income': {  # 수입/재테크 관련
            'patterns': [
                r'월\s*\d+(?:만원|만|원)?',  # 월500, 월 500만원
                r'\d+\s*(?:만원|만|원)',     # 500만원, 100만
                r'연봉\s*\d+',              # 연봉 5000
                r'수입|매출|돈벌기|재테크|투자|부업|알바|투잡'
            ],
            'related_keywords': ['방법', '후기', '성공', '실패', '팁', '노하우']
        },
        'travel': {  # 여행/관광 관련
            'patterns': [
                r'(?:서울|부산|제주|강원|경기|인천|대구|울산|광주|대전|충북|충남|경북|경남|전북|전남|세종).*(?:여행|관광|숙소|맛집|카페)',
                r'여행\s*\d+(?:만원|만|원)',  # 여행 100만원
                r'(?:국내|해외|섬|산|바다|계곡).*(?:여행|관광|둘러보기)',
                r'(?:액티비티|체험|관광|투어|트레킹)'
            ],
            'related_keywords': ['코스', '일정', '후기', '추천', '명소', '숙소', '맛집', '카페']
        },
        'food': {  # 맛집/음식 관련
            'patterns': [
                r'(?:서울|부산|제주|강원|경기|인천|대구|울산|광주|대전|충북|충남|경북|경남|전북|전남|세종).*(?:맛집|음식|식당|카페)',
                r'(?:한식|중식|일식|양식|분식|카페|디저트)',
                r'(?:맛집|맛있는|유명한|인기|추천).*(?:음식|식당|카페|디저트)',
                r'(?:아침|점심|저녁|브런치|디너).*(?:메뉴|식사)'
            ],
            'related_keywords': ['맛집', '후기', '추천', '인기', '메뉴', '가격', '위치']
        },
        'shopping': {  # 쇼핑/구매 관련
            'patterns': [
                r'\d+(?:만원|만|원).*(?:제품|상품|물건)',  # 100만원 노트북
                r'(?:가성비|최저가|할인|세일)',
                r'(?:제품|상품|물건).*(?:추천|비교|구매|후기)',
                r'(?:쇼핑|구매|구입|장만)'
            ],
            'related_keywords': ['추천', '후기', '비교', '가격', '장단점', '사용법']
        },
        'living': {  # 생활/주거 관련
            'patterns': [
                r'(?:서울|부산|제주|강원|경기|인천|대구|울산|광주|대전|충북|충남|경북|경남|전북|전남|세종).*(?:아파트|빌라|원룸)',
                r'(?:전세|월세|매매).*\d+(?:만원|억)',
                r'(?:이사|입주|청소|인테리어|수리|공과금)',
                r'(?:동네|지역|근처|인근).*(?:생활|편의|시설)'
            ],
            'related_keywords': ['후기', '비교', '장단점', '시세', '정보', '팁']
        },
        'info': {  # 정보/지식 관련
            'patterns': [
                r'(?:방법|하는법|어떻게|뭘까|의미|차이|비교|설명)',
                r'(?:장점|단점|특징|종류|차이점)',
                r'(?:시작|입문|기초|기본|핵심|꿀팁)',
                r'(?:정보|지식|상식|팁|노하우)'
            ],
            'related_keywords': ['정리', '총정리', '한눈에', '쉽게', '초보']
        }
    }

    def __init__(self, client_id: str = None, client_secret: str = None):
        BaseCrawler.__init__(self)  # 부모 클래스 초기화
        logger.info(f"Initializing KeywordCrawler with client_id: {client_id}, client_secret: {client_secret}")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_headers = {
            'X-Naver-Client-Id': client_id,
            'X-Naver-Client-Secret': client_secret
        } if client_id and client_secret else None

        # Test API credentials immediately
        if self.api_headers:
            test_result = self._test_api_credentials()
            if not test_result:
                logger.error("Naver API credentials are invalid")
            # API 테스트 실패해도 헤더는 유지
        else:
            logger.warning("No Naver API credentials provided")

    def _search_api(self, keyword: str, service: str, start: int = 1, display: int = 10) -> Dict:
        """네이버 검색 API 호출"""
        if not self.api_headers:
            logger.error("네이버 API 키가 설정되지 않았습니다.")
            return {}

        # 서비스별 URL 설정
        if service == 'blog':
            url = "https://openapi.naver.com/v1/search/blog"
        elif service == 'news':
            url = "https://openapi.naver.com/v1/search/news.json"
        else:
            logger.error(f"지원하지 않는 서비스입니다: {service}")
            return {}

        params = {
            'query': keyword,
            'display': display,
            'start': start,
            'sort': 'sim'  # 정확도순으로 변경
        }

        try:
            logger.info(f"Calling Naver API - URL: {url}, Service: {service}, Keyword: {keyword}")
            logger.debug(f"Headers: {self.api_headers}")
            logger.debug(f"Params: {params}")
            
            # 부모 클래스의 session이나 headers를 사용하지 않고 직접 API 호출
            response = requests.get(url, headers=self.api_headers, params=params, timeout=10)
            logger.info(f"Response Status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"API Error - Status: {response.status_code}")
                logger.error(f"Error Response: {response.text}")
                return {}
                
            response.raise_for_status()
            result = response.json()
            
            items_count = len(result.get('items', []))
            total_count = result.get('total', 0)
            logger.info(f"API Response - Retrieved {items_count} items out of {total_count} total results")
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API Request Error: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
        except ValueError as e:
            logger.error(f"JSON Parsing Error: {str(e)}")
            logger.error(traceback.format_exc())
            return {}
        except Exception as e:
            logger.error(f"Unexpected Error in API call: {str(e)}")
            logger.error(traceback.format_exc())
            return {}

    def get_news_content(self, url: str) -> Optional[Dict]:
        """뉴스 기사 내용 크롤링"""
        try:
            # 일반 웹 크롤링은 부모 클래스의 session과 headers 사용
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            if "news.naver.com" in url:
                title = soup.select_one("#title_area")
                content = soup.select_one("#dic_area")
                date_str = soup.select_one(".media_end_head_info_datestamp_time")
                
                if not all([title, content, date_str]):
                    logger.warning(f"Missing required elements in news content: {url}")
                    return None
                
                return {
                    'title': title.text.strip(),
                    'content': content.text.strip(),
                    'datetime': date_str.get("data-date-time") or date_str.text.strip(),
                    'url': url
                }
            return None
        except Exception as e:
            logger.error(f"뉴스 내용 파싱 중 오류: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def get_blog_content(self, url: str) -> Optional[Dict]:
        """블로그 포스트 내용 크롤링"""
        try:
            soup = self._get_soup(url)
            if not soup:
                return None
            
            # 네이버 블로그 파싱
            if "blog.naver.com" in url:
                # iframe 내부의 실제 컨텐츠 URL 찾기
                frame = soup.select_one("iframe#mainFrame")
                if not frame:
                    return None
                
                real_url = f"https://blog.naver.com{frame['src']}"
                soup = self._get_soup(real_url)
                if not soup:
                    return None
            
            # SE3 에디터
            title = soup.select_one(".se-title-text")
            content = soup.select_one(".se-main-container")
            date = soup.select_one(".se-date")
            
            if not all([title, content, date]):
                logger.warning(f"Missing required elements in blog content: {url}")
                return None
                
            return {
                'title': title.text.strip(),
                'content': content.text.strip(),
                'datetime': date.text.strip(),
                'url': url
            }
        except Exception as e:
            logger.error(f"블로그 내용 파싱 중 오류: {str(e)}")
            logger.error(traceback.format_exc())
            return None

    def _analyze_search_intent(self, keyword: str) -> Dict:
        """검색 의도 분석"""
        keyword = keyword.lower()
        intents = []
        
        # 각 의도 패턴 검사
        for intent, data in self.intent_patterns.items():
            for pattern in data['patterns']:
                if re.search(pattern, keyword):
                    intents.append(intent)
                    break
        
        # 기본 의도가 없으면 'info' 추가
        if not intents:
            intents.append('info')
        
        return {
            'intents': intents,
            'original_keyword': keyword
        }

    def _expand_search_keywords(self, keyword: str, intent_info: Dict) -> List[str]:
        """검색 의도에 따른 키워드 확장"""
        keywords = [keyword]  # 원본 키워드
        
        for intent in intent_info['intents']:
            if intent in self.intent_patterns:
                # 의도별 관련 키워드 추가
                for related_kw in self.intent_patterns[intent]['related_keywords']:
                    keywords.append(f"{keyword} {related_kw}")
        
        return list(set(keywords))

    def _test_api_credentials(self) -> bool:
        """Test if the Naver API credentials are valid"""
        try:
            logger.info("Testing Naver API credentials...")
            
            # 블로그 API 테스트
            blog_url = "https://openapi.naver.com/v1/search/blog"
            blog_params = {
                'query': '테스트',
                'display': 1
            }
            logger.info(f"Testing Blog API - URL: {blog_url}")
            blog_response = requests.get(blog_url, headers=self.api_headers, params=blog_params)
            
            # 뉴스 API 테스트
            news_url = "https://openapi.naver.com/v1/search/news.json"
            news_params = {
                'query': '테스트',
                'display': 1
            }
            logger.info(f"Testing News API - URL: {news_url}")
            news_response = requests.get(news_url, headers=self.api_headers, params=news_params)
            
            # 두 API 모두 성공해야 True 반환
            if blog_response.status_code == 200 and news_response.status_code == 200:
                logger.info("Both Blog and News APIs are accessible")
                return True
            else:
                logger.error(f"API test failed - Blog Status: {blog_response.status_code}, News Status: {news_response.status_code}")
                if blog_response.status_code != 200:
                    logger.error(f"Blog API Error: {blog_response.text}")
                if news_response.status_code != 200:
                    logger.error(f"News API Error: {news_response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Naver API credentials: {str(e)}")
            logger.error(traceback.format_exc())
            return False

    def _calculate_relevance_score(self, text: str, keyword: str, intent_pattern: Dict = None) -> float:
        """검색 결과의 관련도 점수 계산 (0-5점 척도)"""
        score = 1.0  # 기본 점수
        
        # 1. 기본 키워드 매칭 (2점)
        if re.search(re.escape(keyword), text, re.IGNORECASE):
            score += 2.0
        
        # 2. 검색 의도 패턴 매칭 (각 0.5점)
        if intent_pattern:
            for pattern in intent_pattern['patterns']:
                if re.search(pattern, text, re.IGNORECASE):
                    score += 0.5
                    break  # 하나의 패턴만 매칭되어도 점수 부여
            
            # 3. 관련 키워드 매칭 (각 0.3점)
            for keyword in intent_pattern['related_keywords']:
                if re.search(re.escape(keyword), text, re.IGNORECASE):
                    score += 0.3
        
        return min(5.0, score)  # 최대 5점

    def _calculate_news_quality_score(self, text: str) -> float:
        """뉴스 컨텐츠 품질 점수 계산 (0-5점 척도)"""
        score = 3.0  # 기본 점수
        
        # 광고성 문구 체크 (각 -1점 감점)
        ad_patterns = [
            r'문의|상담|예약|신청|클릭|링크|할인|이벤트|프로모션',
            r'무료|공짜|특가|세일|쿠폰|적립|마감|한정',
            r'(?:광고|제휴|후원).*(?:포함|기사|내용)',
        ]
        for pattern in ad_patterns:
            if re.search(pattern, text):
                score -= 1.0
        
        # 뉴스 품질 체크 (각 +0.5점 가점)
        quality_patterns = [
            r'분석|조사|연구|발표|보고서|통계|결과',
            r'전문가|관계자|담당자|대표|교수|연구원',
            r'(?:지난해|올해|이번|최근).*(?:조사|분석|발표)',
            r'\d+년\s*\d+월|\d+분기|전년\s*대비',
            r'증가율|감소율|상승률|하락률|성장률',
        ]
        for pattern in quality_patterns:
            if re.search(pattern, text):
                score += 0.5
        
        return max(0.0, min(5.0, score))  # 0-5점 범위로 제한

    def _calculate_blog_quality_score(self, text: str) -> float:
        """블로그 컨텐츠 품질 점수 계산 (0-5점 척도)"""
        score = 3.0  # 기본 점수
        
        # 광고성 문구 체크 (각 -1점 감점)
        ad_patterns = [
            r'문의|상담|예약|신청|클릭|링크|할인|이벤트|프로모션',
            r'무료|공짜|특가|세일|쿠폰|적립|마감|한정',
            r'(?:광고|제휴|후원).*(?:포함|기사|내용)',
        ]
        for pattern in ad_patterns:
            if re.search(pattern, text):
                score -= 1.0
        
        # 블로그 품질 체크 (각 +0.5점 가점)
        quality_patterns = [
            r'후기|리뷰|추천|비교|사용기',
            r'사진|영상|동영상|이미지',
            r'(?:최근|최신|업데이트).*(?:정보|내용)',
        ]
        for pattern in quality_patterns:
            if re.search(pattern, text):
                score += 0.5
        
        return max(0.0, min(5.0, score))  # 0-5점 범위로 제한

    def search_with_long_tail(self, main_keyword: str, max_results: int = 5) -> Dict[str, List[Dict]]:
        """검색 의도 기반 검색 실행"""
        try:
            # 검색어 전처리 및 의도 분석
            main_keyword = main_keyword.strip()
            logger.info(f"Starting search with keyword: {main_keyword}")
            
            intent_info = self._analyze_search_intent(main_keyword)
            logger.info(f"Analyzed search intent: {intent_info}")
            
            # 검색 키워드 확장
            search_keywords = self._expand_search_keywords(main_keyword, intent_info)
            logger.info(f"Expanded keywords: {search_keywords}")
            
            # 블로그 검색
            all_results = []
            for keyword in [main_keyword] + search_keywords[:3]:
                logger.info(f"Searching for keyword: {keyword}")
                blog_results = self.get_blog_list(keyword)
                if blog_results:
                    logger.info(f"Found {len(blog_results)} blog results for {keyword}")
                    for result in blog_results:
                        if not all(key in result for key in ['title', 'description', 'link']):
                            logger.warning(f"Missing required fields in result: {result}")
                            continue
                        all_results.append(result)
                
                # 뉴스 검색 추가
                news_results = self.get_news_list(keyword)
                if news_results:
                    logger.info(f"Found {len(news_results)} news results for {keyword}")
                    for result in news_results:
                        if not all(key in result for key in ['title', 'description', 'link']):
                            logger.warning(f"Missing required fields in result: {result}")
                            continue
                        result['is_news'] = True  # 뉴스 결과 구분
                        all_results.append(result)
            
            # 관련도 점수로 정렬하고 필터링
            all_results = sorted(all_results, key=lambda x: x.get('relevance_score', 0), reverse=True)
            filtered_results = [
                result for result in all_results 
                if result.get('relevance_score', 0) >= 0.5  # 최소 관련도 점수
            ]
            
            # 중복 제거
            seen_urls = set()
            unique_results = []
            for result in filtered_results:
                url = result.get('link')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_results.append(result)
            
            logger.info(f"Final unique results: {len(unique_results)}")
            
            return {
                'main_keyword': main_keyword,
                'search_keywords': search_keywords[:10],
                'results': unique_results[:max_results],
                'intent': intent_info.get('intents', ['info'])
            }
            
        except Exception as e:
            logger.error(f"Error in search_with_long_tail: {str(e)}")
            logger.error(traceback.format_exc())
            raise

    def get_blog_list(self, keyword: str, page: int = 1) -> List[Dict]:
        """블로그 검색 결과 조회"""
        try:
            # 검색 의도 분석
            intent_info = self._analyze_search_intent(keyword)
            
            # API 호출
            result = self._search_api(keyword, 'blog', start=(page-1)*10+1)
            if not result or 'items' not in result:
                return []
            
            blog_results = []
            for item in result.get('items', []):
                # HTML 태그 제거
                title = re.sub('<[^<]+?>', '', item.get('title', ''))
                description = re.sub('<[^<]+?>', '', item.get('description', ''))
                
                # 전체 내용 크롤링
                full_content = self._crawl_full_content(item.get('link', ''))
                
                # 관련도 점수 계산
                relevance_score = self._calculate_relevance_score(
                    f"{title} {description}", 
                    keyword,
                    self.intent_patterns.get(intent_info['intents'][0]) if intent_info['intents'] else None
                )
                
                # 검색 의도에 맞는 결과만 필터링 (관련도 점수 2.0 이상)
                if relevance_score >= 2.0:
                    blog_results.append({
                        'title': title,
                        'description': description,
                        'link': item.get('link', ''),
                        'blog_name': item.get('bloggername', ''),
                        'post_date': item.get('postdate', ''),
                        'relevance_score': relevance_score,
                        'full_content': full_content  # 전체 내용 추가
                    })
            
            # 관련도 점수로 정렬
            blog_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return blog_results[:10]  # 상위 10개만 반환
            
        except Exception as e:
            self.logger.error(f"블로그 검색 중 오류: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []

    def get_news_list(self, keyword: str, page: int = 1) -> List[Dict]:
        """뉴스 검색 결과 조회"""
        try:
            # 검색 의도 분석
            intent_info = self._analyze_search_intent(keyword)
            
            # API 호출
            result = self._search_api(keyword, 'news', start=(page-1)*10+1)
            if not result or 'items' not in result:
                return []
            
            news_results = []
            for item in result.get('items', []):
                # HTML 태그 제거
                title = re.sub('<[^<]+?>', '', item.get('title', ''))
                description = re.sub('<[^<]+?>', '', item.get('description', ''))
                
                # 전체 내용 크롤링
                full_content = self._crawl_full_content(item.get('link', ''))
                
                # 관련도 점수 계산
                relevance_score = self._calculate_relevance_score(
                    f"{title} {description}", 
                    keyword,
                    self.intent_patterns.get(intent_info['intents'][0]) if intent_info['intents'] else None
                )
                
                # 검색 의도에 맞는 결과만 필터링 (관련도 점수 2.0 이상)
                if relevance_score >= 2.0:
                    news_results.append({
                        'title': title,
                        'description': description,
                        'link': item.get('link', ''),
                        'pub_date': item.get('pubDate', ''),
                        'relevance_score': relevance_score,
                        'full_content': full_content  # 전체 내용 추가
                    })
            
            # 관련도 점수로 정렬
            news_results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return news_results[:10]  # 상위 10개만 반환
            
        except Exception as e:
            self.logger.error(f"뉴스 검색 중 오류: {str(e)}")
            self.logger.error(traceback.format_exc())
            return []

    def fetch_blog_list(self, keyword: str) -> List[Dict]:
        """블로그 검색 결과를 가져옵니다."""
        results = []
        try:
            response = self._search_api(keyword, "blog")
            if not response or 'items' not in response:
                return results
            
            for item in response['items']:
                # 기존 정보는 그대로 유지
                blog_info = {
                    'title': self._clean_html_tags(item.get('title', '')),
                    'description': self._clean_html_tags(item.get('description', '')),
                    'link': item.get('link', ''),
                    'blog_name': item.get('bloggername', ''),
                    'post_date': item.get('postdate', '')
                }
                
                # 전체 내용 크롤링 추가
                full_content = self._crawl_full_content(item['link'])
                if full_content:
                    blog_info['full_content'] = full_content
                    
                results.append(blog_info)
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error in fetch_blog_list: {str(e)}")
            return results

    def fetch_news_list(self, keyword: str) -> List[Dict]:
        """뉴스 검색 결과를 가져옵니다."""
        results = []
        try:
            response = self._search_api(keyword, "news")
            if not response or 'items' not in response:
                return results
            
            for item in response['items']:
                # 기존 정보는 그대로 유지
                news_info = {
                    'title': self._clean_html_tags(item.get('title', '')),
                    'description': self._clean_html_tags(item.get('description', '')),
                    'link': item.get('link', ''),
                    'pub_date': item.get('pubDate', '')
                }
                
                # 전체 내용 크롤링 추가
                full_content = self._crawl_full_content(item['link'])
                if full_content:
                    news_info['full_content'] = full_content
                    
                results.append(news_info)
                
            return results
            
        except Exception as e:
            self.logger.error(f"Error in fetch_news_list: {str(e)}")
            return results

    def _crawl_full_content(self, url: str) -> str:
        """URL에서 전체 내용을 크롤링합니다."""
        try:
            import requests
            from bs4 import BeautifulSoup
            
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 네이버 블로그
            if 'blog.naver.com' in url:
                iframe = soup.find('iframe', id='mainFrame')
                if iframe:
                    blog_url = f"https://blog.naver.com{iframe['src']}"
                    response = requests.get(blog_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    content = soup.find('div', {'class': 'se-main-container'})
                    if content:
                        return content.get_text(strip=True)
            
            # 일반 블로그/뉴스
            article = soup.find('article') or soup.find('main') or soup.find('div', {'class': ['content', 'article', 'post']})
            if article:
                return article.get_text(strip=True)
                
            # 전체 텍스트
            return soup.get_text(strip=True)
            
        except Exception as e:
            self.logger.error(f"Error crawling content from {url}: {str(e)}")
            return ""