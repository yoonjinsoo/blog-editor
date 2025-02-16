from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class ServiceType(Enum):
    """서비스 유형"""
    QUICKFLEX = "quickflex"  # 쿠팡 퀵플렉스
    INSTALLATION = "installation"  # 설치 기사
    DELIVERY = "delivery"  # 배송
    LOGISTICS = "logistics"  # 물류
    MOVING = "moving"  # 이사
    
@dataclass
class ContactInfo:
    """연락처 정보"""
    email: str
    phone: str
    mobile: Optional[str] = None
    kakao: Optional[str] = None
    website: Optional[str] = None

@dataclass
class CompanyInfo:
    """회사 기본 정보"""
    name: str
    business_number: str
    address: str
    ceo_name: str
    contact: ContactInfo
    description: str
    establishment_date: str
    
@dataclass
class ServiceInfo:
    """서비스별 정보"""
    type: ServiceType
    name: str
    description: str
    features: List[str]
    benefits: List[str]
    requirements: Optional[List[str]] = None
    additional_info: Optional[Dict[str, str]] = None

class CompanyProfile:
    """회사 프로필 관리"""
    
    def __init__(self):
        self.company = CompanyInfo(
            name="주식회사 엔비로지스틱",
            business_number="123-45-67890",  # 실제 사업자번호로 교체 필요
            address="서울특별시 ...",  # 실제 주소로 교체 필요
            ceo_name="홍길동",  # 실제 대표자명으로 교체 필요
            contact=ContactInfo(
                email="7health@hanmail.net",
                phone="1600-9891",
                mobile="010-9071-3365"
            ),
            description="""
            🏢 주식회사 엔비로지스틱은 물류·운송·배송 분야에서 전문적인 서비스를 제공하는 기업으로,
            고객의 다양한 요구에 맞춰 최상의 솔루션을 제공합니다.
            """.strip(),
            establishment_date="2020-01-01"  # 실제 설립일로 교체 필요
        )
        
        self.services: Dict[ServiceType, ServiceInfo] = {}
        self._initialize_services()
        
    def _initialize_services(self):
        """서비스 정보 초기화"""
        # 퀵플렉스 서비스
        self.services[ServiceType.QUICKFLEX] = ServiceInfo(
            type=ServiceType.QUICKFLEX,
            name="쿠팡 퀵플렉스",
            description="쿠팡의 혁신적인 당일배송 서비스",
            features=[
                "자율 출퇴근",
                "높은 수입",
                "안정적인 물량",
                "교육 지원"
            ],
            benefits=[
                "월 500만원 이상 수입 가능",
                "주 5일 자율 근무",
                "퀵플렉스 물량 우선 배정"
            ],
            requirements=[
                "1종 보통 운전면허 이상",
                "화물운송 자격증"
            ]
        )
        
        # 설치 기사 서비스
        self.services[ServiceType.INSTALLATION] = ServiceInfo(
            type=ServiceType.INSTALLATION,
            name="쿠팡 설치 기사",
            description="전문 설치 서비스",
            features=[
                "자율 출퇴근",
                "높은 수입",
                "교육 지원",
                "자격증 취득 지원"
            ],
            benefits=[
                "월 500만원 이상 수입 가능",
                "주 5일 자율 근무",
                "경력자 우대 수당"
            ],
            requirements=[
                "관련 자격증 보유자",
                "실무 경력 1년 이상"
            ]
        )
    
    def get_service_info(self, service_type: ServiceType) -> Optional[ServiceInfo]:
        """서비스 정보 조회"""
        return self.services.get(service_type)
    
    def add_service(self, service: ServiceInfo):
        """새로운 서비스 추가"""
        self.services[service.type] = service
    
    def update_service(self, service: ServiceInfo):
        """서비스 정보 업데이트"""
        if service.type in self.services:
            self.services[service.type] = service
            
    def get_contact_message(self, service_type: Optional[ServiceType] = None) -> str:
        """문의 정보 메시지 생성"""
        service = self.get_service_info(service_type) if service_type else None
        
        message = []
        message.append(f"🏢 {self.company.name}")
        
        if service:
            message.append(f"\n{service.description}")
        else:
            message.append(f"\n{self.company.description}")
            
        message.append("\n더 많은 정보가 필요하시면 아래 연락처로 문의하세요.")
        message.append(f"\n📧 이메일: {self.company.contact.email}")
        message.append(f"\n📞 대표번호: {self.company.contact.phone}")
        
        if self.company.contact.mobile:
            message.append(f"\n📱 핸드폰: {self.company.contact.mobile}")
            
        if self.company.contact.kakao:
            message.append(f"\n💬 카카오톡: {self.company.contact.kakao}")
            
        if self.company.contact.website:
            message.append(f"\n🌐 웹사이트: {self.company.contact.website}")
            
        return "\n".join(message)
