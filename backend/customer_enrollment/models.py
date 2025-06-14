"""
Customer Enrollment Models
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import EmailValidator, RegexValidator
from django.utils import timezone

class Customer(models.Model):
    """
    Main customer model representing the Customer Information File (CIF)
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_review', 'In Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    ]
    
    RISK_LEVEL_CHOICES = [
        ('unknown', 'Unknown'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    external_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    risk_score = models.IntegerField(default=0)
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, default='unknown')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_customers')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='updated_customers')
    
    class Meta:
        db_table = 'customers'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Customer {self.external_id or self.id}"

class CustomerPersonalData(models.Model):
    """
    Personal data for customers
    """
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('separated', 'Separated'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='personal_data')
    
    # Name fields
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=300)
    
    # Personal information
    date_of_birth = models.DateField(null=True, blank=True)
    place_of_birth = models.CharField(max_length=200, blank=True)
    nationality = models.CharField(max_length=100, blank=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True)
    marital_status = models.CharField(max_length=50, choices=MARITAL_STATUS_CHOICES, blank=True)
    
    # Professional information
    occupation = models.CharField(max_length=200, blank=True)
    employer = models.CharField(max_length=200, blank=True)
    annual_income = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    source_of_wealth = models.TextField(blank=True)
    
    # Tax information
    tax_id = models.CharField(max_length=50, blank=True)
    tax_country = models.CharField(max_length=100, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_personal_data'
    
    def save(self, *args, **kwargs):
        # Auto-generate full_name if not provided
        if not self.full_name:
            name_parts = [self.first_name, self.middle_name, self.last_name]
            self.full_name = ' '.join(filter(None, name_parts))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.full_name

class CustomerContactInfo(models.Model):
    """
    Contact information for customers
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name='contact_info')
    
    # Address
    address_line1 = models.CharField(max_length=200, blank=True)
    address_line2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Contact details
    phone_primary = models.CharField(
        max_length=50, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    phone_secondary = models.CharField(
        max_length=50, 
        blank=True,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Enter a valid phone number.')]
    )
    email_primary = models.EmailField(blank=True, validators=[EmailValidator()])
    email_secondary = models.EmailField(blank=True, validators=[EmailValidator()])
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_contact_info'
    
    def __str__(self):
        return f"Contact info for {self.customer}"

class EnrollmentSession(models.Model):
    """
    Tracks enrollment sessions for customers
    """
    STATUS_CHOICES = [
        ('started', 'Started'),
        ('personal_data_completed', 'Personal Data Completed'),
        ('documents_uploaded', 'Documents Uploaded'),
        ('submitted', 'Submitted'),
        ('completed', 'Completed'),
        ('abandoned', 'Abandoned'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='enrollment_sessions')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='started')
    
    # Session data
    session_data = models.JSONField(default=dict, blank=True)
    current_step = models.CharField(max_length=50, default='personal_data')
    completion_percentage = models.IntegerField(default=0)
    
    # Timestamps
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Resume functionality
    resume_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    resume_expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'enrollment_sessions'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['resume_token']),
            models.Index(fields=['last_activity_at']),
        ]
    
    def is_expired(self):
        """Check if the resume token is expired"""
        if not self.resume_expires_at:
            return True
        return timezone.now() > self.resume_expires_at
    
    def generate_resume_token(self):
        """Generate a new resume token"""
        import secrets
        self.resume_token = secrets.token_urlsafe(32)
        self.resume_expires_at = timezone.now() + timezone.timedelta(days=30)
        self.save()
        return self.resume_token
    
    def __str__(self):
        return f"Enrollment session {self.id} for {self.customer}"

