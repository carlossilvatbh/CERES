"""
Document Processing Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import logging
import mimetypes

from customer_enrollment.models import Customer, EnrollmentSession
from .models import CustomerDocument, DocumentProcessingTask, DocumentTemplate
from .serializers import (
    CustomerDocumentSerializer, DocumentUploadSerializer, DocumentProcessingTaskSerializer,
    DocumentExtractionResultSerializer, DocumentValidationSerializer, ForensicAnalysisSerializer,
    DocumentTemplateSerializer
)
from .services import DocumentProcessingService
from ceres_project.utils import success_response, paginated_response

logger = logging.getLogger('ceres')

class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer documents
    """
    queryset = CustomerDocument.objects.all()
    serializer_class = CustomerDocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """Filter documents based on customer and permissions"""
        queryset = super().get_queryset()
        
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        verification_status = self.request.query_params.get('verification_status')
        if verification_status:
            queryset = queryset.filter(verification_status=verification_status)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List documents with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginated_response(serializer.data, self.paginator, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """Upload a new document"""
        # This method is replaced by the upload action
        return self.upload(request, *args, **kwargs)
    
    @action(detail=False, methods=['post'])
    def upload(self, request):
        """
        Upload a document for a customer
        """
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'customer_id is required'}
            )
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return success_response(
                None,
                status_code=status.HTTP_404_NOT_FOUND,
                meta={'error': 'Customer not found'}
            )
        
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create document
            document = serializer.save(
                customer=customer,
                mime_type=mimetypes.guess_type(serializer.validated_data['file'].name)[0] or 'application/octet-stream'
            )
            
            # Update enrollment session if exists
            active_session = EnrollmentSession.objects.filter(
                customer=customer,
                status__in=['personal_data_completed', 'documents_uploaded']
            ).first()
            
            if active_session:
                active_session.status = 'documents_uploaded'
                active_session.current_step = 'review'
                active_session.completion_percentage = 75
                active_session.save()
            
            # Start processing tasks
            processing_service = DocumentProcessingService()
            processing_service.start_document_processing(document)
        
        logger.info(f"Document uploaded for customer {customer.id}", extra={
            'customer_id': str(customer.id),
            'document_id': str(document.id),
            'document_type': document.document_type
        })
        
        response_serializer = CustomerDocumentSerializer(document, context={'request': request})
        return success_response(response_serializer.data, status_code=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get document processing status
        """
        document = self.get_object()
        
        # Get processing tasks
        tasks = DocumentProcessingTask.objects.filter(document=document).order_by('-created_at')
        task_serializer = DocumentProcessingTaskSerializer(tasks, many=True)
        
        response_data = {
            'document': CustomerDocumentSerializer(document, context={'request': request}).data,
            'processing_tasks': task_serializer.data,
            'overall_status': document.verification_status
        }
        
        return success_response(response_data)
    
    @action(detail=True, methods=['get'])
    def extracted_data(self, request, pk=None):
        """
        Get extracted data from document OCR
        """
        document = self.get_object()
        
        if not document.ocr_data and not document.extracted_data:
            return success_response(
                None,
                status_code=status.HTTP_404_NOT_FOUND,
                meta={'error': 'No extracted data available'}
            )
        
        response_data = {
            'document_id': document.id,
            'ocr_data': document.ocr_data,
            'extracted_data': document.extracted_data,
            'verification_status': document.verification_status,
            'processed_at': document.processed_at
        }
        
        return success_response(response_data)
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        Validate document data against customer information
        """
        document = self.get_object()
        
        processing_service = DocumentProcessingService()
        validation_result = processing_service.validate_document(document)
        
        logger.info(f"Document validation requested for {document.id}", extra={
            'document_id': str(document.id),
            'customer_id': str(document.customer.id)
        })
        
        return success_response(validation_result)
    
    @action(detail=True, methods=['get'])
    def forensic_analysis(self, request, pk=None):
        """
        Get forensic analysis results for document
        """
        document = self.get_object()
        
        if not document.forensic_analysis:
            # Start forensic analysis if not done
            processing_service = DocumentProcessingService()
            processing_service.start_forensic_analysis(document)
            
            return success_response(
                {'message': 'Forensic analysis started. Check back later for results.'},
                status_code=status.HTTP_202_ACCEPTED
            )
        
        response_data = {
            'document_id': document.id,
            'authenticity_score': document.authenticity_score,
            'analysis_details': document.forensic_analysis,
            'risk_indicators': document.forensic_analysis.get('risk_indicators', [])
        }
        
        return success_response(response_data)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """
        Reprocess document (OCR + validation)
        """
        document = self.get_object()
        
        # Reset processing status
        document.verification_status = 'processing'
        document.ocr_data = {}
        document.extracted_data = {}
        document.verification_details = {}
        document.save()
        
        # Start reprocessing
        processing_service = DocumentProcessingService()
        processing_service.start_document_processing(document)
        
        logger.info(f"Document reprocessing started for {document.id}", extra={
            'document_id': str(document.id),
            'customer_id': str(document.customer.id)
        })
        
        return success_response({
            'message': 'Document reprocessing started',
            'status': document.verification_status
        })

class DocumentTemplateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing document templates
    """
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter templates based on parameters"""
        queryset = super().get_queryset()
        
        document_type = self.request.query_params.get('document_type')
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        country = self.request.query_params.get('country')
        if country:
            queryset = queryset.filter(country=country)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('document_type', 'country')
    
    def list(self, request, *args, **kwargs):
        """List document templates"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

