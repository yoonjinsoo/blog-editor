from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
import random

@dataclass
class StyleConfig:
    """문체 설정"""
    tone: str               # 어조 (formal, casual, professional)
    formality_level: int    # 격식 수준 (1-5)
    target_audience: str    # 목표 독자층
    writing_style: str      # 글쓰기 스타일 (descriptive, narrative, etc.)

@dataclass
class StyleResult:
    """스타일 적용 결과"""
    styled_content: str     # 스타일 적용된 컨텐츠
    changes_made: List[Dict[str, Any]]  # 변경 사항
    style_metrics: Dict[str, float]     # 스타일 지표

class ContentStyler:
    """컨텐츠 스타일 조정기"""
    
    def __init__(self):
        # 문체 패턴
        self.style_patterns = {
            'formal': {
                r'합니다': '하였습니다',
                r'해요': '합니다',
                r'죠': '지요'
            },
            'casual': {
                r'하였습니다': '했어요',
                r'입니다': '이에요',
                r'습니다': '어요'
            },
            'professional': {
                r'쉽게': '용이하게',
                r'빠르게': '신속하게',
                r'좋은': '우수한'
            }
        }
        
        # 문장 연결 표현
        self.transitions = {
            'formal': [
                "따라서",
                "그러므로",
                "이에",
                "이러한 이유로"
            ],
            'casual': [
                "그래서",
                "그러니까",
                "그래요",
                "이렇게"
            ],
            'professional': [
                "이에 따라",
                "이러한 관점에서",
                "이를 고려할 때",
                "이러한 맥락에서"
            ]
        }
        
        # 종결 표현
        self.endings = {
            'formal': [
                "입니다.",
                "하였습니다.",
                "되었습니다."
            ],
            'casual': [
                "이에요.",
                "했어요.",
                "됐어요."
            ],
            'professional': [
                "할 수 있습니다.",
                "하게 됩니다.",
                "이루어집니다."
            ]
        }
        
    def apply_style(self, content: str, style_config: StyleConfig) -> StyleResult:
        """스타일 적용"""
        original_content = content
        changes_made = []
        
        # 1. 문체 패턴 적용
        styled_content, pattern_changes = self._apply_style_patterns(
            content, 
            style_config.tone
        )
        changes_made.extend(pattern_changes)
        
        # 2. 문장 연결 개선
        styled_content, transition_changes = self._improve_transitions(
            styled_content,
            style_config.tone
        )
        changes_made.extend(transition_changes)
        
        # 3. 종결 표현 조정
        styled_content, ending_changes = self._adjust_endings(
            styled_content,
            style_config.tone
        )
        changes_made.extend(ending_changes)
        
        # 4. 문장 다양성 향상
        styled_content, diversity_changes = self._enhance_sentence_diversity(
            styled_content,
            style_config
        )
        changes_made.extend(diversity_changes)
        
        # 5. 스타일 지표 계산
        style_metrics = self._calculate_style_metrics(
            original_content,
            styled_content,
            style_config
        )
        
        return StyleResult(
            styled_content=styled_content,
            changes_made=changes_made,
            style_metrics=style_metrics
        )
        
    def _apply_style_patterns(self, 
                            content: str,
                            tone: str) -> tuple[str, List[Dict[str, Any]]]:
        """문체 패턴 적용"""
        changes = []
        modified_content = content
        
        for pattern, replacement in self.style_patterns.get(tone, {}).items():
            matches = re.finditer(pattern, modified_content)
            for match in matches:
                old_text = match.group()
                modified_content = modified_content.replace(old_text, replacement)
                changes.append({
                    'type': 'style_pattern',
                    'position': match.start(),
                    'old_text': old_text,
                    'new_text': replacement
                })
                
        return modified_content, changes
        
    def _improve_transitions(self,
                           content: str,
                           tone: str) -> tuple[str, List[Dict[str, Any]]]:
        """문장 연결 개선"""
        changes = []
        sentences = re.split(r'[.!?]\s+', content)
        modified_sentences = []
        
        for i, sentence in enumerate(sentences):
            if i > 0 and not any(t in sentence for t in self.transitions[tone]):
                # 적절한 전환어 추가
                transition = random.choice(self.transitions[tone])
                modified_sentence = f"{transition}, {sentence}"
                changes.append({
                    'type': 'transition',
                    'position': len(' '.join(modified_sentences)),
                    'old_text': sentence,
                    'new_text': modified_sentence
                })
                modified_sentences.append(modified_sentence)
            else:
                modified_sentences.append(sentence)
                
        return ' '.join(modified_sentences), changes
        
    def _adjust_endings(self,
                       content: str,
                       tone: str) -> tuple[str, List[Dict[str, Any]]]:
        """종결 표현 조정"""
        changes = []
        sentences = re.split(r'[.!?]\s+', content)
        modified_sentences = []
        
        for sentence in sentences:
            modified = False
            for ending in self.endings[tone]:
                if sentence.endswith(ending.rstrip('.')):
                    continue
                    
                # 기존 종결어미를 새로운 것으로 교체
                new_ending = random.choice(self.endings[tone])
                modified_sentence = re.sub(r'[.!?]?$', '', sentence) + new_ending
                
                changes.append({
                    'type': 'ending',
                    'position': len(' '.join(modified_sentences)),
                    'old_text': sentence,
                    'new_text': modified_sentence
                })
                
                modified_sentences.append(modified_sentence)
                modified = True
                break
                
            if not modified:
                modified_sentences.append(sentence)
                
        return ' '.join(modified_sentences), changes
        
    def _enhance_sentence_diversity(self,
                                  content: str,
                                  style_config: StyleConfig) -> tuple[str, List[Dict[str, Any]]]:
        """문장 다양성 향상"""
        changes = []
        sentences = re.split(r'[.!?]\s+', content)
        modified_sentences = []
        
        # 문장 길이 다양화
        target_lengths = {
            'short': (10, 20),
            'medium': (20, 40),
            'long': (40, 60)
        }
        
        for i, sentence in enumerate(sentences):
            current_length = len(sentence)
            
            # 연속된 비슷한 길이의 문장 방지
            if (i > 0 and 
                abs(len(modified_sentences[-1]) - current_length) < 10):
                # 문장 분할 또는 병합
                if current_length > 40:
                    split_point = sentence.find('며,')
                    if split_point != -1:
                        modified_sentences.extend([
                            sentence[:split_point] + '니다.',
                            sentence[split_point+2:].strip()
                        ])
                        changes.append({
                            'type': 'diversity',
                            'position': len(' '.join(modified_sentences[:-1])),
                            'old_text': sentence,
                            'new_text': '. '.join(modified_sentences[-2:])
                        })
                        continue
                        
            modified_sentences.append(sentence)
            
        return ' '.join(modified_sentences), changes
        
    def _calculate_style_metrics(self,
                               original: str,
                               styled: str,
                               config: StyleConfig) -> Dict[str, float]:
        """스타일 지표 계산"""
        # 1. 형식성 점수
        formality_patterns = {
            r'습니다': 1.0,
            r'에요': 0.5,
            r'야': 0.0
        }
        formality_score = 0
        total_patterns = 0
        
        for pattern, score in formality_patterns.items():
            matches = len(re.findall(pattern, styled))
            formality_score += matches * score
            total_patterns += matches
            
        # 2. 문장 다양성 점수
        sentences = re.split(r'[.!?]\s+', styled)
        lengths = [len(s) for s in sentences]
        length_variance = sum((l - sum(lengths)/len(lengths))**2 for l in lengths) / len(lengths)
        diversity_score = min(1.0, length_variance / 100)
        
        # 3. 일관성 점수
        consistency_score = 1.0
        for tone_patterns in self.style_patterns.values():
            if tone_patterns != self.style_patterns[config.tone]:
                # 다른 톤의 패턴이 발견되면 점수 감소
                for pattern in tone_patterns:
                    if re.search(pattern, styled):
                        consistency_score -= 0.1
                        
        return {
            'formality': formality_score / (total_patterns or 1),
            'diversity': diversity_score,
            'consistency': max(0, consistency_score),
            'overall': (formality_score / (total_patterns or 1) + 
                       diversity_score + 
                       consistency_score) / 3
        }
