"""
Document Processing Models
"""
import uuid
import hashlib
from django.db import models
from django.core.validators import FileExtensionValidator
from customer_enrollment.models import Customer

def document_upload_path(instance, filename):
    """Generate upload path for documents"""
    return f'documents/{instance.customer.id}/{uuid.uuid4()}/{filename}'

class CustomerDocument(models.Model):
    """
    Model for storing customer documents
    """
    DOCUMENT_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('drivers_license', 'Driver\'s License'),
        ('proof_of_address', 'Proof of Address'),
        ('bank_statement', 'Bank Statement'),
        ('tax_return', 'Tax Return'),
        ('employment_letter', 'Employment Letter'),
        ('business_registration', 'Business Registration'),
        ('other', 'Other'),
    ]
    
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('requires_manual_review', 'Requires Manual Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='documents')
    
    # Document metadata
    document_type = models.CharField(max_length=100, choices=DOCUMENT_TYPE_CHOICES)
    document_number = models.CharField(max_length=100, blank=True)
    issuing_country = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    
    # File information
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])]
    )
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()
    file_hash = models.CharField(max_length=128, unique=True)
    mime_type = models.CharField(max_length=100)
    
    # OCR and processing results
    ocr_data = models.JSONField(default=dict, blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)
    verification_status = models.CharField(
        max_length=50, 
        choices=VERIFICATION_STATUS_CHOICES, 
        default='pending'
    )
    verification_details = models.JSONField(default=dict, blank=True)
    
    # Forensic analysis
    forensic_analysis = models.JSONField(default=dict, blank=True)
    authenticity_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'customer_documents'
        indexes = [
            models.Index(fields=['customer', 'document_type']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['created_at']),
        ]
    
    def save(self, *args, **kwargs):
        if self.file:
            # Calculate file hash
            if not self.file_hash:
                self.file_hash = self.calculate_file_hash()
            
            # Set file metadata
            if not self.file_name:
                self.file_name = self.file.name
            if not self.file_size:
                self.file_size = self.file.size
        
        super().save(*args, **kwargs)
    
    def calculate_file_hash(self):
        """Calculate SHA-256 hash of the file"""
        hash_sha256 = hashlib.sha256()
        for chunk in self.file.chunks():
            hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def __str__(self):
        return f"{self.document_type} for {self.customer}"

class DocumentProcessingTask(models.Model):
    """
    Model for tracking document processing tasks
    """
    TASK_TYPE_CHOICES = [
        ('ocr', 'OCR Processing'),
        ('forensic', 'Forensic Analysis'),
        ('validation', 'Data Validation'),
        ('categorization', 'Document Categorization'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('retrying', 'Retrying'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(CustomerDocument, on_delete=models.CASCADE, related_name='processing_tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    
    # Task details
    task_data = models.JSONField(default=dict, blank=True)
    result_data = models.JSONField(default=dict, blank=True)
    error_message = models.TextField(blank=True)
    retry_count = models.PositiveIntegerField(default=0)
    max_retries = models.PositiveIntegerField(default=3)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'document_processing_tasks'
        indexes = [
            models.Index(fields=['document', 'task_type']),
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.task_type} task for {self.document}"

class DocumentTemplate(models.Model):
    """
    Model for storing document templates and extraction rules
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_type = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    issuing_authority = models.CharField(max_length=200, blank=True)
    
    # Template configuration
    template_name = models.CharField(max_length=200)
    extraction_rules = models.JSONField(default=dict)
    validation_rules = models.JSONField(default=dict)
    
    # Template metadata
    is_active = models.BooleanField(default=True)
    confidence_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=0.8)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'document_templates'
        unique_together = ['document_type', 'country', 'template_name']
    
    def __str__(self):
        return f"{self.template_name} ({self.document_type} - {self.country})"

