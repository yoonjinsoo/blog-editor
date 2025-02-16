from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class ServiceInfo:
    """서비스 정보를 담는 클래스"""
    name: str
    features: List[str]
    benefits: List[str]
    connection_points: List[str]
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ServiceInfo':
        """딕셔너리로부터 ServiceInfo 생성"""
        return ServiceInfo(
            name=data.get('name', ''),
            features=data.get('features', []),
            benefits=data.get('benefits', []),
            connection_points=data.get('connection_points', [])
        )
    
    def get_connection_templates(self) -> Dict[str, List[str]]:
        """서비스 연결을 위한 문장 템플릿"""
        return {
            'intro': [
                f"이러한 상황에서 {self.name}이(가) 도움이 될 수 있습니다.",
                f"이제 {self.name}으로 더 쉽게 관리해보세요.",
                f"바로 이런 문제를 {self.name}이(가) 해결해드립니다."
            ],
            'feature': [
                f"{self.name}의 {'{feature}'} 기능을 활용하면 {'{context}'} 가능합니다.",
                f"특히 {'{feature}'} 기능으로 {'{context}'} 효율적으로 관리할 수 있습니다.",
                f"{'{context}'} {self.name}의 {'{feature}'} 기능을 추천드립니다."
            ],
            'benefit': [
                f"{self.name}을(를) 사용하면 {'{benefit}'} 장점이 있습니다.",
                f"{'{context}'} {self.name}의 {'{benefit}'} 혜택을 누려보세요.",
                f"무엇보다 {'{benefit}'} 것이 {self.name}의 큰 장점입니다."
            ],
            'conclusion': [
                f"지금 바로 {self.name}으로 시작해보세요.",
                f"{self.name}과 함께 더 나은 미래를 준비해보세요.",
                f"더 자세한 내용은 {self.name}에서 확인해보세요."
            ]
        }

@dataclass
class ContentContext:
    """컨텐츠 생성을 위한 컨텍스트 정보"""
    keyword: str
    service: ServiceInfo
    target_audience: str = "일반"
    tone: str = "정보성"
    company: str = ""
    contact_info: str = ""
    
    def get_connection_point(self, sentence: str) -> Dict[str, Any]:
        """문장에 적합한 서비스 연결 포인트 찾기"""
        connection = {
            'type': None,
            'template': None,
            'params': {}
        }
        
        # 1. 특징 연결 확인
        for feature in self.service.features:
            if any(keyword in sentence for keyword in feature.split()):
                connection.update({
                    'type': 'feature',
                    'params': {
                        'feature': feature,
                        'context': sentence
                    }
                })
                break
                
        # 2. 혜택 연결 확인
        if not connection['type']:
            for benefit in self.service.benefits:
                if any(keyword in sentence for keyword in benefit.split()):
                    connection.update({
                        'type': 'benefit',
                        'params': {
                            'benefit': benefit,
                            'context': sentence
                        }
                    })
                    break
                    
        # 3. 연결 포인트 확인
        if not connection['type']:
            for point in self.service.connection_points:
                if point in sentence:
                    connection.update({
                        'type': 'intro',
                        'params': {
                            'context': sentence
                        }
                    })
                    break
                    
        # 템플릿 선택
        if connection['type']:
            templates = self.service.get_connection_templates()
            connection['template'] = templates[connection['type']]
            
        return connection
