"""
Customer Enrollment Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
import logging

from .models import Customer, CustomerAddress, CustomerDocument, UltimateBeneficialOwner
from .serializers import (
    CustomerSerializer, CustomerCreateSerializer, CustomerUpdateSerializer,
    CustomerListSerializer, CustomerAddressSerializer, CustomerDocumentSerializer
)
from ceres_project.utils import success_response, error_response

logger = logging.getLogger('ceres')

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers
    """
    queryset = Customer.objects.select_related('created_by').prefetch_related(
        'addresses', 'enrollment_documents', 'beneficial_owners'
    ).all()
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer_type', 'status', 'risk_level']
    search_fields = ['first_name', 'last_name', 'entity_name', 'email', 'tax_identifier']
    ordering_fields = ['created_at', 'updated_at', 'risk_score']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CustomerListSerializer
        elif self.action == 'create':
            return CustomerCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        return CustomerSerializer
    
    def perform_create(self, serializer):
        """Set created_by when creating customer"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def addresses(self, request, pk=None):
        """Get customer addresses"""
        customer = self.get_object()
        addresses = customer.addresses.all()
        serializer = CustomerAddressSerializer(addresses, many=True)
        return success_response(serializer.data, "Customer addresses retrieved successfully")
    
    @action(detail=True, methods=['post'])
    def add_address(self, request, pk=None):
        """Add address to customer"""
        customer = self.get_object()
        serializer = CustomerAddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer)
            return success_response(serializer.data, "Address added successfully", status.HTTP_201_CREATED)
        return error_response("Invalid address data", serializer.errors)
    
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        """Get customer documents"""
        customer = self.get_object()
        documents = customer.enrollment_documents.all()
        serializer = CustomerDocumentSerializer(documents, many=True)
        return success_response(serializer.data, "Customer documents retrieved successfully")
    
    @action(detail=True, methods=['post'])
    def upload_document(self, request, pk=None):
        """Upload document for customer"""
        customer = self.get_object()
        serializer = CustomerDocumentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(customer=customer, uploaded_by=request.user)
            return success_response(serializer.data, "Document uploaded successfully", status.HTTP_201_CREATED)
        return error_response("Invalid document data", serializer.errors)
    
    @action(detail=True, methods=['post'])
    def screen(self, request, pk=None):
        """Trigger screening for customer"""
        customer = self.get_object()
        
        # Here you would integrate with the screening engine
        # For now, we'll just update the last screening date
        customer.last_screening_date = timezone.now()
        customer.save()
        
        return success_response(
            {"screening_date": customer.last_screening_date},
            "Screening initiated successfully"
        )
    
    @action(detail=True, methods=['get'])
    def risk_assessment(self, request, pk=None):
        """Get customer risk assessment"""
        customer = self.get_object()
        
        risk_data = {
            "customer_id": customer.id,
            "risk_score": customer.risk_score,
            "risk_level": customer.risk_level,
            "last_assessment": customer.last_risk_assessment,
            "pep_status": customer.pep_status,
            "sanctions_match": customer.sanctions_match,
            "adverse_media": customer.adverse_media,
        }
        
        return success_response(risk_data, "Risk assessment retrieved successfully")

class CustomerAddressViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer addresses
    """
    queryset = CustomerAddress.objects.select_related('customer').all()
    serializer_class = CustomerAddressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'address_type', 'country', 'is_verified']

class CustomerDocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customer documents
    """
    queryset = CustomerDocument.objects.select_related('customer', 'uploaded_by').all()
    serializer_class = CustomerDocumentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['customer', 'document_type', 'status']
    search_fields = ['file_name', 'document_number']
    ordering_fields = ['uploaded_at', 'processed_at']
    ordering = ['-uploaded_at']
    
    def perform_create(self, serializer):
        """Set uploaded_by when creating document"""
        serializer.save(uploaded_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def process(self, request, pk=None):
        """Trigger document processing"""
        document = self.get_object()
        
        # Here you would integrate with document processing engine
        # For now, we'll just update the status
        document.status = 'processing'
        document.save()
        
        return success_response(
            {"status": document.status},
            "Document processing initiated"
        )
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve document"""
        document = self.get_object()
        document.status = 'approved'
        document.reviewed_by = request.user
        document.reviewed_at = timezone.now()
        document.save()
        
        return success_response(
            {"status": document.status},
            "Document approved successfully"
        )
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject document"""
        document = self.get_object()
        document.status = 'rejected'
        document.reviewed_by = request.user
        document.reviewed_at = timezone.now()
        document.processing_notes = request.data.get('notes', '')
        document.save()
        
        return success_response(
            {"status": document.status},
            "Document rejected"
        )

