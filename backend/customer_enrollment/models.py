"""
Enhanced customer models with international support
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

class Customer(models.Model):
    """
    Enhanced customer model supporting both individuals and entities
    with international compliance requirements
    """
    
    CUSTOMER_TYPES = [
        ('individual', _('Individual')),
        ('entity', _('Legal Entity')),
    ]
    
    RISK_LEVELS = [
        ('low', _('Low Risk')),
        ('medium', _('Medium Risk')),
        ('high', _('High Risk')),
        ('critical', _('Critical Risk')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('suspended', _('Suspended')),
        ('closed', _('Closed')),
    ]
    
    # Primary fields
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer_type = models.CharField(max_length=20, choices=CUSTOMER_TYPES, default='individual')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Individual fields
    first_name = models.CharField(max_length=100, blank=True, verbose_name=_('First Name'))
    middle_name = models.CharField(max_length=100, blank=True, verbose_name=_('Middle Name'))
    last_name = models.CharField(max_length=100, blank=True, verbose_name=_('Last Name'))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    place_of_birth = models.CharField(max_length=200, blank=True, verbose_name=_('Place of Birth'))
    gender = models.CharField(max_length=10, choices=[('M', _('Male')), ('F', _('Female')), ('O', _('Other'))], blank=True)
    
    # Entity fields
    entity_name = models.CharField(max_length=200, blank=True, verbose_name=_('Entity Name'))
    entity_type = models.CharField(max_length=50, blank=True, verbose_name=_('Entity Type'))
    incorporation_date = models.DateField(null=True, blank=True, verbose_name=_('Incorporation Date'))
    incorporation_country = models.CharField(max_length=3, blank=True, verbose_name=_('Incorporation Country'))
    
    # Common fields
    nationality = models.CharField(max_length=3, blank=True, verbose_name=_('Nationality'))  # ISO 3166-1 alpha-3
    tax_identifier = models.CharField(max_length=50, blank=True, verbose_name=_('Tax Identifier'))
    email = models.EmailField(blank=True, verbose_name=_('Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone'))
    
    # Risk assessment
    risk_score = models.IntegerField(default=0, verbose_name=_('Risk Score'))
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='low')
    last_risk_assessment = models.DateTimeField(null=True, blank=True)
    
    # Compliance
    pep_status = models.BooleanField(default=False, verbose_name=_('PEP Status'))
    sanctions_match = models.BooleanField(default=False, verbose_name=_('Sanctions Match'))
    adverse_media = models.BooleanField(default=False, verbose_name=_('Adverse Media'))
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_screening_date = models.DateTimeField(null=True, blank=True)
    
    # Additional data (JSON field for flexibility)
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['customer_type', 'status']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['last_screening_date']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.customer_type == 'individual':
            return f"{self.first_name} {self.last_name}".strip() or f"Customer {self.id}"
        else:
            return self.entity_name or f"Entity {self.id}"
    
    @property
    def full_name(self):
        """Get full name for individuals"""
        if self.customer_type == 'individual':
            parts = [self.first_name, self.middle_name, self.last_name]
            return ' '.join(part for part in parts if part)
        return self.entity_name
    
    @property
    def display_name(self):
        """Get display name for any customer type"""
        return self.full_name
    
    def get_risk_color(self):
        """Get color code for risk level"""
        colors = {
            'low': '#10B981',      # Green
            'medium': '#F59E0B',   # Yellow
            'high': '#EF4444',     # Red
            'critical': '#7C2D12', # Dark Red
        }
        return colors.get(self.risk_level, '#6B7280')

class CustomerAddress(models.Model):
    """
    Customer address model supporting multiple addresses per customer
    """
    
    ADDRESS_TYPES = [
        ('residential', _('Residential')),
        ('business', _('Business')),
        ('mailing', _('Mailing')),
        ('registered', _('Registered Office')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='addresses')
    address_type = models.CharField(max_length=20, choices=ADDRESS_TYPES, default='residential')
    
    # Address fields
    street_address_1 = models.CharField(max_length=200, verbose_name=_('Street Address 1'))
    street_address_2 = models.CharField(max_length=200, blank=True, verbose_name=_('Street Address 2'))
    city = models.CharField(max_length=100, verbose_name=_('City'))
    state_province = models.CharField(max_length=100, blank=True, verbose_name=_('State/Province'))
    postal_code = models.CharField(max_length=20, blank=True, verbose_name=_('Postal Code'))
    country = models.CharField(max_length=3, verbose_name=_('Country'))  # ISO 3166-1 alpha-3
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Customer Address')
        verbose_name_plural = _('Customer Addresses')
        ordering = ['address_type', '-created_at']
    
    def __str__(self):
        return f"{self.customer.display_name} - {self.get_address_type_display()}"
    
    @property
    def full_address(self):
        """Get formatted full address"""
        parts = [
            self.street_address_1,
            self.street_address_2,
            self.city,
            self.state_province,
            self.postal_code,
            self.country
        ]
        return ', '.join(part for part in parts if part)

class CustomerDocument(models.Model):
    """
    Customer document model for KYC documentation
    """
    
    DOCUMENT_TYPES = [
        ('passport', _('Passport')),
        ('national_id', _('National ID')),
        ('drivers_license', _('Driver\'s License')),
        ('utility_bill', _('Utility Bill')),
        ('bank_statement', _('Bank Statement')),
        ('proof_of_address', _('Proof of Address')),
        ('articles_of_incorporation', _('Articles of Incorporation')),
        ('certificate_of_good_standing', _('Certificate of Good Standing')),
        ('beneficial_ownership', _('Beneficial Ownership Declaration')),
        ('other', _('Other')),
    ]
    
    STATUS_CHOICES = [
        ('pending', _('Pending Review')),
        ('processing', _('Processing')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('expired', _('Expired')),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='enrollment_documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # File information
    file_name = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='customer_documents/')
    file_size = models.PositiveIntegerField()
    file_hash = models.CharField(max_length=64, blank=True)  # SHA-256 hash
    
    # Document details
    document_number = models.CharField(max_length=100, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    issuing_authority = models.CharField(max_length=200, blank=True)
    issuing_country = models.CharField(max_length=3, blank=True)
    
    # Processing results
    ocr_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    authenticity_score = models.FloatField(null=True, blank=True)
    processing_notes = models.TextField(blank=True)
    
    # Metadata
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reviewed_documents')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Customer Document')
        verbose_name_plural = _('Customer Documents')
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['customer', 'document_type']),
            models.Index(fields=['status']),
            models.Index(fields=['uploaded_at']),
        ]
    
    def __str__(self):
        return f"{self.customer.display_name} - {self.get_document_type_display()}"

class UltimateBeneficialOwner(models.Model):
    """
    Ultimate Beneficial Owner (UBO) model for entity customers
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    entity_customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='beneficial_owners',
        limit_choices_to={'customer_type': 'entity'}
    )
    
    # UBO details
    first_name = models.CharField(max_length=100, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=100, verbose_name=_('Last Name'))
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'))
    nationality = models.CharField(max_length=3, verbose_name=_('Nationality'))
    
    # Ownership details
    ownership_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Ownership %'))
    control_type = models.CharField(max_length=50, blank=True, verbose_name=_('Control Type'))
    
    # Address
    address = models.TextField(verbose_name=_('Address'))
    country = models.CharField(max_length=3, verbose_name=_('Country'))
    
    # PEP and sanctions
    is_pep = models.BooleanField(default=False, verbose_name=_('Is PEP'))
    pep_details = models.TextField(blank=True, verbose_name=_('PEP Details'))
    sanctions_match = models.BooleanField(default=False, verbose_name=_('Sanctions Match'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Ultimate Beneficial Owner')
        verbose_name_plural = _('Ultimate Beneficial Owners')
        ordering = ['-ownership_percentage', 'last_name', 'first_name']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.ownership_percentage}%)"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

