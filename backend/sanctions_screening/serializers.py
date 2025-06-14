"""
Sanctions Screening Serializers
"""
from rest_framework import serializers
from .models import ScreeningSource, ScreeningResult, ScreeningBatch, ScreeningAlert, ScreeningConfiguration

class ScreeningSourceSerializer(serializers.ModelSerializer):
    """
    Serializer for screening sources
    """
    class Meta:
        model = ScreeningSource
        fields = [
            'id', 'name', 'code', 'source_type', 'jurisdiction', 'authority',
            'license_type', 'reliability_score', 'is_active', 'is_available',
            'last_updated', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_updated']

class ScreeningResultSerializer(serializers.ModelSerializer):
    """
    Serializer for screening results
    """
    source = ScreeningSourceSerializer(read_only=True)
    
    class Meta:
        model = ScreeningResult
        fields = [
            'id', 'source', 'query_name', 'match_found', 'match_type',
            'confidence_score', 'matched_name', 'matched_entity_id',
            'entity_type', 'categories', 'sanctions_programs',
            'processing_time', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class ScreeningBatchSerializer(serializers.ModelSerializer):
    """
    Serializer for screening batches
    """
    sources = ScreeningSourceSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = ScreeningBatch
        fields = [
            'id', 'name', 'description', 'status', 'sources',
            'total_customers', 'processed_customers', 'matches_found',
            'progress_percentage', 'started_at', 'completed_at',
            'estimated_completion', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_customers', 'processed_customers', 'matches_found',
            'started_at', 'completed_at', 'estimated_completion', 'created_at'
        ]
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage"""
        if obj.total_customers == 0:
            return 0
        return round((obj.processed_customers / obj.total_customers) * 100, 2)

class ScreeningAlertSerializer(serializers.ModelSerializer):
    """
    Serializer for screening alerts
    """
    customer_name = serializers.SerializerMethodField()
    source_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ScreeningAlert
        fields = [
            'id', 'alert_type', 'severity', 'status', 'title', 'message',
            'customer_name', 'source_name', 'requires_action',
            'action_taken', 'action_taken_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'customer_name', 'source_name', 'created_at', 'updated_at'
        ]
    
    def get_customer_name(self, obj):
        """Get customer name if available"""
        if obj.customer and hasattr(obj.customer, 'personal_data'):
            return obj.customer.personal_data.full_name
        return None
    
    def get_source_name(self, obj):
        """Get source name if available"""
        return obj.source.name if obj.source else None

class ScreeningConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for screening configuration
    """
    class Meta:
        model = ScreeningConfiguration
        fields = [
            'id', 'name', 'description', 'exact_match_threshold',
            'fuzzy_match_threshold', 'semantic_match_threshold',
            'phonetic_match_threshold', 'high_risk_threshold',
            'medium_risk_threshold', 'max_concurrent_requests',
            'request_timeout', 'retry_attempts', 'enable_transliteration',
            'enable_semantic_matching', 'enable_phonetic_matching',
            'enable_auto_alerts', 'is_active', 'is_default',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class ScreeningRequestSerializer(serializers.Serializer):
    """
    Serializer for screening requests
    """
    customer_id = serializers.UUIDField(required=True)
    source_codes = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="List of source codes to search. If empty, all active sources will be used."
    )
    force_refresh = serializers.BooleanField(
        default=False,
        help_text="Force refresh even if recent results exist"
    )

class BatchScreeningRequestSerializer(serializers.Serializer):
    """
    Serializer for batch screening requests
    """
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    customer_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        help_text="List of customer IDs to screen"
    )
    source_codes = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="List of source codes to search. If empty, all active sources will be used."
    )

class ScreeningSummarySerializer(serializers.Serializer):
    """
    Serializer for screening summary
    """
    customer_id = serializers.UUIDField()
    total_sources_checked = serializers.IntegerField()
    matches_found = serializers.IntegerField()
    high_risk_matches = serializers.IntegerField()
    medium_risk_matches = serializers.IntegerField()
    low_risk_matches = serializers.IntegerField()
    last_screened = serializers.DateTimeField()
    overall_risk_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    risk_level = serializers.CharField()
    alerts_count = serializers.IntegerField()
    
class ScreeningMatchSerializer(serializers.Serializer):
    """
    Serializer for individual screening matches
    """
    source_name = serializers.CharField()
    source_code = serializers.CharField()
    matched_name = serializers.CharField()
    confidence_score = serializers.DecimalField(max_digits=5, decimal_places=2)
    match_type = serializers.CharField()
    entity_type = serializers.CharField()
    categories = serializers.ListField(child=serializers.CharField())
    sanctions_programs = serializers.ListField(child=serializers.CharField())
    additional_info = serializers.JSONField()
    source_url = serializers.URLField(required=False)

