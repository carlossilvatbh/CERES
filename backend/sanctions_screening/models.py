"""
Sanctions Screening Models
"""
import uuid
from django.db import models
from customer_enrollment.models import Customer

class ScreeningSource(models.Model):
    """
    Model for managing screening data sources
    """
    SOURCE_TYPE_CHOICES = [
        ('sanctions', 'Sanctions List'),
        ('pep', 'Politically Exposed Persons'),
        ('media', 'Negative Media'),
        ('corporate', 'Corporate Registry'),
        ('law_enforcement', 'Law Enforcement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=50, unique=True)
    source_type = models.CharField(max_length=50, choices=SOURCE_TYPE_CHOICES)
    
    # Source configuration
    api_url = models.URLField(blank=True)
    data_url = models.URLField(blank=True)
    update_frequency = models.CharField(max_length=50, default='daily')  # daily, weekly, monthly
    last_updated = models.DateTimeField(null=True, blank=True)
    
    # Source metadata
    jurisdiction = models.CharField(max_length=100, blank=True)
    authority = models.CharField(max_length=200, blank=True)
    license_type = models.CharField(max_length=100, default='open_source')
    reliability_score = models.DecimalField(max_digits=3, decimal_places=2, default=1.0)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_available = models.BooleanField(default=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'screening_sources'
        indexes = [
            models.Index(fields=['source_type', 'is_active']),
            models.Index(fields=['code']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class ScreeningResult(models.Model):
    """
    Model for storing screening results
    """
    MATCH_TYPE_CHOICES = [
        ('exact', 'Exact Match'),
        ('fuzzy', 'Fuzzy Match'),
        ('semantic', 'Semantic Match'),
        ('phonetic', 'Phonetic Match'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='screening_results')
    source = models.ForeignKey(ScreeningSource, on_delete=models.CASCADE, related_name='screening_results')
    
    # Query information
    query_name = models.CharField(max_length=300)
    query_data = models.JSONField(default=dict, blank=True)
    
    # Match information
    match_found = models.BooleanField(default=False)
    match_type = models.CharField(max_length=50, choices=MATCH_TYPE_CHOICES, blank=True)
    confidence_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    
    # Match details
    matched_name = models.CharField(max_length=300, blank=True)
    matched_entity_id = models.CharField(max_length=200, blank=True)
    match_details = models.JSONField(default=dict, blank=True)
    
    # Additional data
    entity_type = models.CharField(max_length=100, blank=True)  # individual, entity, vessel, etc.
    categories = models.TextField(blank=True)  # JSON stored as text
    sanctions_programs = models.TextField(blank=True)  # JSON stored as text
    
    # Raw response
    raw_response = models.JSONField(default=dict, blank=True)
    
    # Processing metadata
    processing_time = models.DecimalField(max_digits=8, decimal_places=3, default=0)
    api_version = models.CharField(max_length=50, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'screening_results'
        indexes = [
            models.Index(fields=['customer', 'source']),
            models.Index(fields=['match_found', 'confidence_score']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Screening result for {self.customer} in {self.source.name}"

class ScreeningBatch(models.Model):
    """
    Model for managing batch screening operations
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Batch configuration
    sources = models.ManyToManyField(ScreeningSource, related_name='screening_batches')
    customers = models.ManyToManyField(Customer, related_name='screening_batches')
    
    # Status and progress
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    total_customers = models.PositiveIntegerField(default=0)
    processed_customers = models.PositiveIntegerField(default=0)
    matches_found = models.PositiveIntegerField(default=0)
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    estimated_completion = models.DateTimeField(null=True, blank=True)
    
    # Results summary
    results_summary = models.JSONField(default=dict, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'screening_batches'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Screening batch: {self.name}"

class ScreeningAlert(models.Model):
    """
    Model for screening alerts and notifications
    """
    ALERT_TYPE_CHOICES = [
        ('high_risk_match', 'High Risk Match'),
        ('new_sanctions', 'New Sanctions Added'),
        ('source_unavailable', 'Source Unavailable'),
        ('threshold_exceeded', 'Threshold Exceeded'),
        ('manual_review_required', 'Manual Review Required'),
    ]
    
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('acknowledged', 'Acknowledged'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Related objects
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    screening_result = models.ForeignKey(ScreeningResult, on_delete=models.CASCADE, null=True, blank=True)
    source = models.ForeignKey(ScreeningSource, on_delete=models.CASCADE, null=True, blank=True)
    
    # Alert content
    title = models.CharField(max_length=200)
    message = models.TextField()
    alert_data = models.JSONField(default=dict, blank=True)
    
    # Actions
    requires_action = models.BooleanField(default=False)
    action_taken = models.TextField(blank=True)
    action_taken_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True, blank=True)
    action_taken_at = models.DateTimeField(null=True, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'screening_alerts'
        indexes = [
            models.Index(fields=['alert_type', 'severity']),
            models.Index(fields=['status']),
            models.Index(fields=['customer']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.alert_type} alert for {self.customer}"

class ScreeningConfiguration(models.Model):
    """
    Model for storing screening configuration and thresholds
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    
    # Threshold configuration
    exact_match_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=100.0)
    fuzzy_match_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=85.0)
    semantic_match_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80.0)
    phonetic_match_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=75.0)
    
    # Source weights
    source_weights = models.JSONField(default=dict, blank=True)
    
    # Alert thresholds
    high_risk_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=90.0)
    medium_risk_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=70.0)
    
    # Processing configuration
    max_concurrent_requests = models.PositiveIntegerField(default=10)
    request_timeout = models.PositiveIntegerField(default=30)  # seconds
    retry_attempts = models.PositiveIntegerField(default=3)
    
    # Feature flags
    enable_transliteration = models.BooleanField(default=True)
    enable_semantic_matching = models.BooleanField(default=True)
    enable_phonetic_matching = models.BooleanField(default=True)
    enable_auto_alerts = models.BooleanField(default=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = 'screening_configurations'
    
    def save(self, *args, **kwargs):
        # Ensure only one default configuration
        if self.is_default:
            ScreeningConfiguration.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

