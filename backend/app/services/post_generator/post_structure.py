from typing import Dict, List, Optional
import json
from pathlib import Path

class PostStructure:
    """블로그 포스트 구조 정의"""
    
    def __init__(self):
        self.structure_config = {
            'blog_post_template': {
                'title': {
                    'pattern': ' {keywords} {year}년 {benefit}!',
                    'max_length': 45
                },
                'intro': {
                    'max_length': 300,
                    'sections': [
                        '핵심 메시지',
                        '신뢰성 있는 데이터/통계',
                        '독자 관심 유도'
                    ]
                },
                'table_of_contents': {
                    'sections': [
                        '주요 내용',
                        '상세 정보',
                        '지원 방법',
                        '자주 묻는 질문'
                    ]
                },
                'main_sections': [
                    {
                        'title': ' {section_title}',
                        'content_structure': [
                            '핵심 정보',
                            '구체적 데이터',
                            '내부 링크',
                            '중요 포인트'
                        ]
                    }
                ],
                'qa_section': {
                    'title': '? 자주 묻는 질문',
                    'min_questions': 5,
                    'max_questions': 7,
                    'question_pattern': 'Q. {question}',
                    'answer_length': {
                        'min': 100,
                        'max': 200
                    }
                },
                'conclusion': {
                    'max_length': 200,
                    'sections': [
                        '핵심 내용 요약',
                        '행동 유도 문구',
                        '연락처/신청 방법'
                    ]
                },
                'tags': {
                    'in_content': {
                        'min': 3,
                        'max': 4
                    },
                    'bottom': {
                        'min': 20,
                        'max': 30
                    }
                },
                'formatting': {
                    'paragraph_max_length': 4,  # 
                    'use_emojis': True,
                    'heading_levels': ['H2', 'H3', 'H4'],
                    'spacing': {
                        'between_sections': 2,  # 
                        'between_paragraphs': 1  # 
                    }
                },
                'seo_requirements': {
                    'keyword_density': {
                        'min': 2,
                        'max': 3
                    },
                    'internal_links': {
                        'min': 2,
                        'max': 3
                    },
                    'external_links': {
                        'min': 1,
                        'max': 2
                    }
                }
            },
            'common_seo_elements': {
                'thumbnail': {
                    'required': True,
                    'position': 'top',
                    'count': 1,
                    'types': ['jpg', 'png']
                },
                'images': {
                    'required': True,
                    'min_count': 3,
                    'recommended_count': 5,
                    'types': ['jpg', 'png', 'gif'],
                    'alt_text': True
                },
                'heading_structure': {
                    'h1': {'count': 1, 'position': 'top'},
                    'h2': {'min_count': 3},
                    'h3': {'min_count': 5}
                },
                'meta': {
                    'title_length': {'min': 30, 'max': 60},
                    'description_length': {'min': 100, 'max': 160},
                    'keywords': {'min_count': 5, 'max_count': 10}
                }
            },
            'intent_structures': {
                'income': {
                    'sections': [
                        {
                            'type': 'intro',
                            'title': '소개 및 개요',
                            'elements': {
                                'text': {'required': True},
                                'image': {'required': True, 'count': 1},
                                'stats': {'required': True}
                            }
                        },
                        {
                            'type': 'background',
                            'title': '시장 현황 및 배경',
                            'elements': {
                                'text': {'required': True},
                                'chart': {'required': True},
                                'data_table': {'required': True}
                            }
                        },
                        {
                            'type': 'methods',
                            'title': '수익 창출 방법',
                            'elements': {
                                'text': {'required': True},
                                'steps': {'required': True},
                                'images': {'required': True, 'count': 3},
                                'gif': {'optional': True}
                            }
                        }
                    ],
                    'seo_requirements': {
                        'keyword_density': {'main': 2, 'related': 1},
                        'internal_links': {'min_count': 3},
                        'external_links': {'min_count': 2}
                    }
                },
                'product': {
                    'sections': [
                        {
                            'type': 'intro',
                            'title': '제품 소개',
                            'elements': {
                                'text': {'required': True},
                                'product_images': {
                                    'required': True,
                                    'count': {'min': 3, 'max': 5},
                                    'types': ['jpg', 'png']
                                }
                            }
                        },
                        {
                            'type': 'features',
                            'title': '주요 특징',
                            'elements': {
                                'text': {'required': True},
                                'feature_images': {'required': True, 'count': {'min': 3}},
                                'demonstration_gif': {'required': True}
                            }
                        }
                    ],
                    'seo_requirements': {
                        'keyword_density': {'main': 1.5, 'related': 1}
                    }
                },
                'info': {
                    'sections': [
                        {
                            'type': 'intro',
                            'title': '개요',
                            'elements': {
                                'text': {'required': True},
                                'image': {'required': True, 'count': 1}
                            }
                        },
                        {
                            'type': 'background',
                            'title': '배경 설명',
                            'elements': {
                                'text': {'required': True},
                                'image': {'required': True, 'count': 1}
                            }
                        },
                        {
                            'type': 'methods',
                            'title': '상세 내용',
                            'elements': {
                                'text': {'required': True},
                                'steps': {'required': True},
                                'images': {'required': True, 'count': 2}
                            }
                        }
                    ],
                    'seo_requirements': {
                        'keyword_density': {'main': 1.5, 'related': 1},
                        'internal_links': {'min_count': 2},
                        'external_links': {'min_count': 1}
                    }
                },
                'blog_post_template': {
                    'meta': {
                        'category': {
                            'required': True,
                            'type': 'string'
                        },
                        'main_keyword': {
                            'required': True,
                            'type': 'string'
                        },
                        'sub_keywords': {
                            'required': True,
                            'type': 'list',
                            'min_count': 3,
                            'max_count': 5
                        },
                        'target_audience': {
                            'required': True,
                            'type': 'string'
                        }
                    },
                    'content': {
                        'title': {
                            'required': True,
                            'max_length': 40,
                            'patterns': [
                                '[연도] [키워드]로 [혜택] 얻는 방법',
                                '[숫자]가지 [키워드] [혜택] 비법',
                                '[키워드] 완벽 가이드: [혜택] 노하우'
                            ]
                        },
                        'intro': {
                            'required': True,
                            'sections': {
                                'hook': {'required': True, 'max_length': 100},
                                'problem': {'required': True, 'max_length': 150},
                                'solution_hint': {'required': True, 'max_length': 150},
                                'overview': {'required': True, 'max_length': 200}
                            }
                        },
                        'main_sections': {
                            'required': True,
                            'min_count': 3,
                            'max_count': 4,
                            'structure': {
                                'subtitle': {'required': True, 'max_length': 50},
                                'content': {'required': True, 'min_length': 300},
                                'example': {'required': False},
                                'image': {
                                    'required': True,
                                    'properties': {
                                        'url': {'required': True},
                                        'alt': {'required': True},
                                        'caption': {'required': True}
                                    }
                                }
                            }
                        },
                        'conclusion': {
                            'required': True,
                            'sections': {
                                'summary': {'required': True, 'max_length': 300},
                                'action_items': {'required': True, 'min_count': 3},
                                'engagement': {'required': True, 'max_length': 100}
                            }
                        }
                    },
                    'seo': {
                        'meta_description': {
                            'required': True,
                            'min_length': 100,
                            'max_length': 160
                        },
                        'tags': {
                            'required': True,
                            'min_count': 5,
                            'max_count': 10
                        },
                        'internal_links': {
                            'required': True,
                            'min_count': 3,
                            'max_count': 5
                        },
                        'external_links': {
                            'required': True,
                            'min_count': 2,
                            'max_count': 3
                        }
                    }
                }
            }
        }
    
    def get_structure_for_intent(self, intent: str) -> Dict:
        """특정 의도에 대한 포스트 구조 반환"""
        if intent not in self.structure_config['intent_structures']:
            intent = 'info'  # 기본값
        return {
            'common': self.structure_config['common_seo_elements'],
            'specific': self.structure_config['intent_structures'][intent]
        }

    def validate_structure(self, post_data: Dict, intent: str) -> Dict:
        """포스트 구조 검증"""
        structure = self.get_structure_for_intent(intent)
        validation_result = {
            'is_valid': True,
            'missing_elements': [],
            'seo_score': 0
        }
        
        # 필수 요소 검증
        for section in structure['specific']['sections']:
            for element, config in section['elements'].items():
                if config.get('required', False) and element not in post_data.get(section['type'], {}):
                    validation_result['is_valid'] = False
                    validation_result['missing_elements'].append(f"{section['type']}.{element}")
        
        # SEO 점수 계산
        validation_result['seo_score'] = self._calculate_seo_score(post_data, structure)
        
        return validation_result

    def _calculate_seo_score(self, post_data: Dict, structure: Dict) -> int:
        """SEO 점수 계산"""
        score = 0
        max_score = 100
        
        # 이미지 점수 (30점)
        required_images = structure['common']['images']['min_count']
        actual_images = len(post_data.get('images', []))
        score += min(30, (actual_images / required_images) * 30)
        
        # 키워드 밀도 점수 (30점)
        if 'keyword_density' in structure['specific']['seo_requirements']:
            target_density = structure['specific']['seo_requirements']['keyword_density']['main']
            actual_density = self._calculate_keyword_density(post_data)
            if actual_density >= target_density:
                score += 30
            else:
                score += (actual_density / target_density) * 30
        
        # 헤딩 구조 점수 (20점)
        if self._validate_heading_structure(post_data, structure['common']['heading_structure']):
            score += 20
        
        # 링크 점수 (20점)
        required_links = structure['specific']['seo_requirements'].get('internal_links', {}).get('min_count', 0)
        actual_links = len(post_data.get('links', []))
        score += min(20, (actual_links / max(1, required_links)) * 20)
        
        return round(score)

    def _calculate_keyword_density(self, post_data: Dict) -> float:
        """키워드 밀도 계산"""
        if 'content' not in post_data or 'keyword' not in post_data:
            return 0.0
        
        content = post_data['content'].lower()
        keyword = post_data['keyword'].lower()
        
        word_count = len(content.split())
        keyword_count = content.count(keyword)
        
        return (keyword_count / word_count) * 100 if word_count > 0 else 0

    def _validate_heading_structure(self, post_data: Dict, heading_rules: Dict) -> bool:
        """헤딩 구조 검증"""
        if 'headings' not in post_data:
            return False
            
        headings = post_data['headings']
        
        # H1 태그 검증
        if heading_rules['h1']['count'] != len([h for h in headings if h['level'] == 1]):
            return False
            
        # H2 태그 검증
        if len([h for h in headings if h['level'] == 2]) < heading_rules['h2']['min_count']:
            return False
            
        # H3 태그 검증
        if len([h for h in headings if h['level'] == 3]) < heading_rules['h3']['min_count']:
            return False
            
        return True