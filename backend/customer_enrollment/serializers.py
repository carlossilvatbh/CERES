"""
Customer Enrollment Serializers
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Customer, CustomerAddress, CustomerDocument, UltimateBeneficialOwner

class CustomerAddressSerializer(serializers.ModelSerializer):
    """Serializer for customer addresses"""
    
    class Meta:
        model = CustomerAddress
        fields = [
            'id', 'address_type', 'street_address_1', 'street_address_2',
            'city', 'state_province', 'postal_code', 'country',
            'is_verified', 'verified_date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'is_verified', 'verified_date', 'created_at', 'updated_at']

class CustomerDocumentSerializer(serializers.ModelSerializer):
    """Serializer for customer documents"""
    
    class Meta:
        model = CustomerDocument
        fields = [
            'id', 'document_type', 'status', 'file_name', 'file_path',
            'file_size', 'document_number', 'issue_date', 'expiry_date',
            'issuing_authority', 'issuing_country', 'ocr_text', 'ocr_confidence',
            'authenticity_score', 'processing_notes', 'uploaded_at', 'processed_at'
        ]
        read_only_fields = [
            'id', 'status', 'file_size', 'ocr_text', 'ocr_confidence',
            'authenticity_score', 'processing_notes', 'uploaded_at', 'processed_at'
        ]

class UltimateBeneficialOwnerSerializer(serializers.ModelSerializer):
    """Serializer for Ultimate Beneficial Owners"""
    
    class Meta:
        model = UltimateBeneficialOwner
        fields = [
            'id', 'first_name', 'last_name', 'date_of_birth', 'nationality',
            'ownership_percentage', 'control_type', 'address', 'country',
            'is_pep', 'pep_details', 'sanctions_match', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sanctions_match', 'created_at', 'updated_at']

class CustomerSerializer(serializers.ModelSerializer):
    """Main customer serializer with nested relationships"""
    
    addresses = CustomerAddressSerializer(many=True, read_only=True)
    documents = CustomerDocumentSerializer(many=True, read_only=True, source='enrollment_documents')
    beneficial_owners = UltimateBeneficialOwnerSerializer(many=True, read_only=True)
    full_name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_type', 'status', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'place_of_birth', 'gender', 'entity_name', 'entity_type',
            'incorporation_date', 'incorporation_country', 'nationality', 'tax_identifier',
            'email', 'phone', 'risk_score', 'risk_level', 'last_risk_assessment',
            'pep_status', 'sanctions_match', 'adverse_media', 'created_at', 'updated_at',
            'last_screening_date', 'metadata', 'full_name', 'display_name',
            'addresses', 'documents', 'beneficial_owners'
        ]
        read_only_fields = [
            'id', 'risk_score', 'risk_level', 'last_risk_assessment',
            'pep_status', 'sanctions_match', 'adverse_media',
            'created_at', 'updated_at', 'last_screening_date'
        ]
    
    def validate(self, data):
        """Validate customer data based on customer type"""
        customer_type = data.get('customer_type', 'individual')
        
        if customer_type == 'individual':
            if not data.get('first_name') or not data.get('last_name'):
                raise serializers.ValidationError(
                    "First name and last name are required for individuals"
                )
        elif customer_type == 'entity':
            if not data.get('entity_name'):
                raise serializers.ValidationError(
                    "Entity name is required for legal entities"
                )
        
        return data

class CustomerCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for customer creation"""
    
    class Meta:
        model = Customer
        fields = [
            'customer_type', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'place_of_birth', 'gender', 'entity_name',
            'entity_type', 'incorporation_date', 'incorporation_country',
            'nationality', 'tax_identifier', 'email', 'phone', 'metadata'
        ]

class CustomerUpdateSerializer(serializers.ModelSerializer):
    """Serializer for customer updates"""
    
    class Meta:
        model = Customer
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth',
            'place_of_birth', 'gender', 'entity_name', 'entity_type',
            'incorporation_date', 'incorporation_country', 'nationality',
            'tax_identifier', 'email', 'phone', 'metadata'
        ]

class CustomerListSerializer(serializers.ModelSerializer):
    """Simplified serializer for customer lists"""
    
    full_name = serializers.CharField(read_only=True)
    display_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'customer_type', 'status', 'full_name', 'display_name',
            'entity_name', 'risk_level', 'created_at', 'updated_at'
        ]

