"""
Document Processing Serializers
"""
from rest_framework import serializers
from .models import CustomerDocument, DocumentProcessingTask, DocumentTemplate

class CustomerDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer for customer documents
    """
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerDocument
        fields = [
            'id', 'document_type', 'document_number', 'issuing_country',
            'issue_date', 'expiry_date', 'file_name', 'file_size', 'mime_type',
            'verification_status', 'authenticity_score', 'created_at', 'updated_at',
            'processed_at', 'file_url'
        ]
        read_only_fields = [
            'id', 'file_size', 'mime_type', 'created_at', 'updated_at', 'processed_at'
        ]
    
    def get_file_url(self, obj):
        """Get secure URL for file access"""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None

class DocumentUploadSerializer(serializers.ModelSerializer):
    """
    Serializer for document upload
    """
    file = serializers.FileField(required=True)
    
    class Meta:
        model = CustomerDocument
        fields = [
            'document_type', 'document_number', 'issuing_country',
            'issue_date', 'expiry_date', 'file'
        ]
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 10MB)
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError("File size cannot exceed 10MB.")
        
        # Check file type
        allowed_types = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg']
        if value.content_type not in allowed_types:
            raise serializers.ValidationError(
                "Only PDF, JPEG, and PNG files are allowed."
            )
        
        return value

class DocumentProcessingTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for document processing tasks
    """
    class Meta:
        model = DocumentProcessingTask
        fields = [
            'id', 'task_type', 'status', 'retry_count', 'max_retries',
            'error_message', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'started_at', 'completed_at'
        ]

class DocumentExtractionResultSerializer(serializers.Serializer):
    """
    Serializer for OCR extraction results
    """
    document_id = serializers.UUIDField()
    extracted_data = serializers.JSONField()
    confidence_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    processing_time = serializers.DecimalField(max_digits=8, decimal_places=3)
    
class DocumentValidationSerializer(serializers.Serializer):
    """
    Serializer for document validation
    """
    document_id = serializers.UUIDField()
    is_valid = serializers.BooleanField()
    validation_errors = serializers.ListField(child=serializers.CharField())
    validation_warnings = serializers.ListField(child=serializers.CharField())
    
class ForensicAnalysisSerializer(serializers.Serializer):
    """
    Serializer for forensic analysis results
    """
    document_id = serializers.UUIDField()
    authenticity_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    analysis_details = serializers.JSONField()
    risk_indicators = serializers.ListField(child=serializers.CharField())
    
class DocumentTemplateSerializer(serializers.ModelSerializer):
    """
    Serializer for document templates
    """
    class Meta:
        model = DocumentTemplate
        fields = [
            'id', 'document_type', 'country', 'issuing_authority',
            'template_name', 'is_active', 'confidence_threshold',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

