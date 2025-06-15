"""
Domain-driven design boundaries for CERES
Defines clear boundaries between different business domains
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Domain Events
@dataclass
class DomainEvent:
    """Base class for domain events"""
    event_id: str
    event_type: str
    aggregate_id: str
    occurred_at: datetime
    data: Dict[str, Any]

@dataclass
class CustomerCreatedEvent(DomainEvent):
    """Event fired when a customer is created"""
    pass

@dataclass
class DocumentProcessedEvent(DomainEvent):
    """Event fired when a document is processed"""
    pass

@dataclass
class ScreeningCompletedEvent(DomainEvent):
    """Event fired when screening is completed"""
    pass

@dataclass
class HighRiskMatchFoundEvent(DomainEvent):
    """Event fired when a high-risk match is found"""
    pass

# Domain Services Interfaces
class ICustomerDomainService(ABC):
    """Interface for customer domain service"""
    
    @abstractmethod
    async def create_customer(self, customer_data: Dict[str, Any]) -> str:
        """Create a new customer"""
        pass
    
    @abstractmethod
    async def update_customer(self, customer_id: str, customer_data: Dict[str, Any]) -> bool:
        """Update customer information"""
        pass
    
    @abstractmethod
    async def get_customer(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        pass
    
    @abstractmethod
    async def calculate_risk_score(self, customer_id: str) -> float:
        """Calculate customer risk score"""
        pass

class IDocumentProcessingService(ABC):
    """Interface for document processing service"""
    
    @abstractmethod
    async def process_document(self, document_data: bytes, document_type: str) -> Dict[str, Any]:
        """Process a document and extract information"""
        pass
    
    @abstractmethod
    async def validate_document(self, document_data: bytes) -> bool:
        """Validate document format and content"""
        pass
    
    @abstractmethod
    async def extract_customer_data(self, ocr_result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract customer data from OCR result"""
        pass

class IScreeningService(ABC):
    """Interface for screening service"""
    
    @abstractmethod
    async def screen_customer(self, customer_data: Dict[str, Any], sources: List[str]) -> Dict[str, Any]:
        """Screen customer against sanctions and PEP lists"""
        pass
    
    @abstractmethod
    async def update_screening_sources(self) -> Dict[str, bool]:
        """Update all screening data sources"""
        pass
    
    @abstractmethod
    async def get_screening_history(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get screening history for customer"""
        pass

class IAlertService(ABC):
    """Interface for alert service"""
    
    @abstractmethod
    async def create_alert(self, alert_type: str, severity: str, message: str, 
                          customer_id: Optional[str] = None) -> str:
        """Create a new alert"""
        pass
    
    @abstractmethod
    async def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """Acknowledge an alert"""
        pass
    
    @abstractmethod
    async def resolve_alert(self, alert_id: str, user_id: str, resolution: str) -> bool:
        """Resolve an alert"""
        pass

class IRiskAssessmentService(ABC):
    """Interface for risk assessment service"""
    
    @abstractmethod
    async def assess_customer_risk(self, customer_id: str) -> Dict[str, Any]:
        """Assess overall customer risk"""
        pass
    
    @abstractmethod
    async def calculate_risk_factors(self, customer_data: Dict[str, Any], 
                                   screening_results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate individual risk factors"""
        pass
    
    @abstractmethod
    async def get_risk_recommendations(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Get risk mitigation recommendations"""
        pass

# Repository Interfaces
class ICustomerRepository(ABC):
    """Interface for customer repository"""
    
    @abstractmethod
    async def save(self, customer: Dict[str, Any]) -> str:
        """Save customer to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """Get customer by ID"""
        pass
    
    @abstractmethod
    async def get_by_document(self, document_number: str) -> Optional[Dict[str, Any]]:
        """Get customer by document number"""
        pass
    
    @abstractmethod
    async def search(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search customers by criteria"""
        pass

class IDocumentRepository(ABC):
    """Interface for document repository"""
    
    @abstractmethod
    async def save(self, document: Dict[str, Any]) -> str:
        """Save document to repository"""
        pass
    
    @abstractmethod
    async def get_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID"""
        pass
    
    @abstractmethod
    async def get_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get documents by customer ID"""
        pass

class IScreeningRepository(ABC):
    """Interface for screening repository"""
    
    @abstractmethod
    async def save_result(self, screening_result: Dict[str, Any]) -> str:
        """Save screening result"""
        pass
    
    @abstractmethod
    async def get_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get screening results by customer ID"""
        pass
    
    @abstractmethod
    async def get_high_risk_matches(self, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """Get high-risk matches above threshold"""
        pass

# Event Bus Interface
class IEventBus(ABC):
    """Interface for event bus"""
    
    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """Publish domain event"""
        pass
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable) -> None:
        """Subscribe to domain events"""
        pass

# Application Services (Orchestration Layer)
class CustomerApplicationService:
    """Application service for customer operations"""
    
    def __init__(self, 
                 customer_service: ICustomerDomainService,
                 customer_repository: ICustomerRepository,
                 event_bus: IEventBus):
        self.customer_service = customer_service
        self.customer_repository = customer_repository
        self.event_bus = event_bus
    
    async def onboard_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Complete customer onboarding process"""
        try:
            # Create customer
            customer_id = await self.customer_service.create_customer(customer_data)
            
            # Publish event
            event = CustomerCreatedEvent(
                event_id=f"customer_created_{customer_id}",
                event_type="customer_created",
                aggregate_id=customer_id,
                occurred_at=datetime.now(),
                data=customer_data
            )
            await self.event_bus.publish(event)
            
            return {
                'customer_id': customer_id,
                'status': 'created',
                'next_steps': ['document_upload', 'screening']
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

class DocumentProcessingApplicationService:
    """Application service for document processing"""
    
    def __init__(self,
                 document_service: IDocumentProcessingService,
                 customer_service: ICustomerDomainService,
                 document_repository: IDocumentRepository,
                 event_bus: IEventBus):
        self.document_service = document_service
        self.customer_service = customer_service
        self.document_repository = document_repository
        self.event_bus = event_bus
    
    async def process_customer_document(self, customer_id: str, document_data: bytes, 
                                      document_type: str) -> Dict[str, Any]:
        """Process customer document and update customer data"""
        try:
            # Process document
            processing_result = await self.document_service.process_document(
                document_data, document_type
            )
            
            # Extract customer data
            extracted_data = await self.document_service.extract_customer_data(
                processing_result
            )
            
            # Update customer with extracted data
            if extracted_data:
                await self.customer_service.update_customer(customer_id, extracted_data)
            
            # Save document
            document_record = {
                'customer_id': customer_id,
                'document_type': document_type,
                'processing_result': processing_result,
                'extracted_data': extracted_data,
                'processed_at': datetime.now()
            }
            document_id = await self.document_repository.save(document_record)
            
            # Publish event
            event = DocumentProcessedEvent(
                event_id=f"document_processed_{document_id}",
                event_type="document_processed",
                aggregate_id=customer_id,
                occurred_at=datetime.now(),
                data={
                    'document_id': document_id,
                    'document_type': document_type,
                    'extracted_data': extracted_data
                }
            )
            await self.event_bus.publish(event)
            
            return {
                'document_id': document_id,
                'status': 'processed',
                'extracted_data': extracted_data,
                'confidence': processing_result.get('confidence', 0)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

class ScreeningApplicationService:
    """Application service for screening operations"""
    
    def __init__(self,
                 screening_service: IScreeningService,
                 customer_service: ICustomerDomainService,
                 alert_service: IAlertService,
                 screening_repository: IScreeningRepository,
                 event_bus: IEventBus):
        self.screening_service = screening_service
        self.customer_service = customer_service
        self.alert_service = alert_service
        self.screening_repository = screening_repository
        self.event_bus = event_bus
    
    async def screen_customer_comprehensive(self, customer_id: str, 
                                          sources: Optional[List[str]] = None) -> Dict[str, Any]:
        """Comprehensive customer screening with risk assessment"""
        try:
            # Get customer data
            customer_data = await self.customer_service.get_customer(customer_id)
            if not customer_data:
                return {'error': 'Customer not found', 'status': 'failed'}
            
            # Perform screening
            screening_result = await self.screening_service.screen_customer(
                customer_data, sources or ['ofac', 'un', 'eu', 'opensanctions']
            )
            
            # Save screening result
            screening_id = await self.screening_repository.save_result({
                'customer_id': customer_id,
                'screening_result': screening_result,
                'screened_at': datetime.now()
            })
            
            # Check for high-risk matches
            high_risk_matches = [
                match for match in screening_result.get('matches', [])
                if match.get('confidence', 0) >= 80
            ]
            
            # Create alerts for high-risk matches
            for match in high_risk_matches:
                await self.alert_service.create_alert(
                    alert_type='high_risk_match',
                    severity='high',
                    message=f"High-risk match found: {match.get('matched_name', 'Unknown')}",
                    customer_id=customer_id
                )
                
                # Publish high-risk event
                event = HighRiskMatchFoundEvent(
                    event_id=f"high_risk_match_{screening_id}",
                    event_type="high_risk_match_found",
                    aggregate_id=customer_id,
                    occurred_at=datetime.now(),
                    data={
                        'screening_id': screening_id,
                        'match': match
                    }
                )
                await self.event_bus.publish(event)
            
            # Publish screening completed event
            event = ScreeningCompletedEvent(
                event_id=f"screening_completed_{screening_id}",
                event_type="screening_completed",
                aggregate_id=customer_id,
                occurred_at=datetime.now(),
                data={
                    'screening_id': screening_id,
                    'total_matches': len(screening_result.get('matches', [])),
                    'high_risk_matches': len(high_risk_matches)
                }
            )
            await self.event_bus.publish(event)
            
            return {
                'screening_id': screening_id,
                'status': 'completed',
                'total_matches': len(screening_result.get('matches', [])),
                'high_risk_matches': len(high_risk_matches),
                'risk_level': 'high' if high_risk_matches else 'low',
                'matches': screening_result.get('matches', [])
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }

# Domain boundaries configuration
DOMAIN_BOUNDARIES = {
    'customer_management': {
        'services': [ICustomerDomainService],
        'repositories': [ICustomerRepository],
        'events': [CustomerCreatedEvent],
        'application_services': [CustomerApplicationService]
    },
    'document_processing': {
        'services': [IDocumentProcessingService],
        'repositories': [IDocumentRepository],
        'events': [DocumentProcessedEvent],
        'application_services': [DocumentProcessingApplicationService]
    },
    'sanctions_screening': {
        'services': [IScreeningService, IRiskAssessmentService],
        'repositories': [IScreeningRepository],
        'events': [ScreeningCompletedEvent, HighRiskMatchFoundEvent],
        'application_services': [ScreeningApplicationService]
    },
    'alerting': {
        'services': [IAlertService],
        'repositories': [],
        'events': [],
        'application_services': []
    }
}

