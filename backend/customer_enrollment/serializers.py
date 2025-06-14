"""
Customer Enrollment Serializers
"""
from rest_framework import serializers
from .models import Customer, CustomerPersonalData, CustomerContactInfo, EnrollmentSession

class CustomerPersonalDataSerializer(serializers.ModelSerializer):
    """
    Serializer for customer personal data
    """
    class Meta:
        model = CustomerPersonalData
        fields = [
            'first_name', 'middle_name', 'last_name', 'full_name',
            'date_of_birth', 'place_of_birth', 'nationality', 'gender',
            'marital_status', 'occupation', 'employer', 'annual_income',
            'source_of_wealth', 'tax_id', 'tax_country'
        ]
        extra_kwargs = {
            'full_name': {'read_only': True},
        }

class CustomerContactInfoSerializer(serializers.ModelSerializer):
    """
    Serializer for customer contact information
    """
    class Meta:
        model = CustomerContactInfo
        fields = [
            'address_line1', 'address_line2', 'city', 'state_province',
            'postal_code', 'country', 'phone_primary', 'phone_secondary',
            'email_primary', 'email_secondary'
        ]

class CustomerSerializer(serializers.ModelSerializer):
    """
    Main customer serializer with nested personal data and contact info
    """
    personal_data = CustomerPersonalDataSerializer(read_only=True)
    contact_info = CustomerContactInfoSerializer(read_only=True)
    
    class Meta:
        model = Customer
        fields = [
            'id', 'external_id', 'status', 'risk_score', 'risk_level',
            'created_at', 'updated_at', 'personal_data', 'contact_info'
        ]
        read_only_fields = ['id', 'risk_score', 'risk_level', 'created_at', 'updated_at']

class EnrollmentSessionSerializer(serializers.ModelSerializer):
    """
    Serializer for enrollment sessions
    """
    customer = CustomerSerializer(read_only=True)
    
    class Meta:
        model = EnrollmentSession
        fields = [
            'id', 'customer', 'status', 'current_step', 'completion_percentage',
            'started_at', 'last_activity_at', 'completed_at', 'session_data'
        ]
        read_only_fields = [
            'id', 'started_at', 'last_activity_at', 'completed_at'
        ]

class EnrollmentStartSerializer(serializers.Serializer):
    """
    Serializer for starting a new enrollment
    """
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=50, required=False)
    
    def validate(self, data):
        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError(
                "Either email or phone number is required to start enrollment."
            )
        return data

class PersonalDataUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating personal data during enrollment
    """
    class Meta:
        model = CustomerPersonalData
        fields = [
            'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'place_of_birth', 'nationality', 'gender',
            'marital_status', 'occupation', 'employer', 'annual_income',
            'source_of_wealth', 'tax_id', 'tax_country'
        ]
    
    def validate_date_of_birth(self, value):
        """Validate that the person is at least 18 years old"""
        if value:
            from datetime import date
            today = date.today()
            age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
            if age < 18:
                raise serializers.ValidationError("Customer must be at least 18 years old.")
        return value

class ContactInfoUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating contact information during enrollment
    """
    class Meta:
        model = CustomerContactInfo
        fields = [
            'address_line1', 'address_line2', 'city', 'state_province',
            'postal_code', 'country', 'phone_primary', 'phone_secondary',
            'email_primary', 'email_secondary'
        ]

class EnrollmentSubmitSerializer(serializers.Serializer):
    """
    Serializer for submitting enrollment
    """
    terms_accepted = serializers.BooleanField(required=True)
    privacy_policy_accepted = serializers.BooleanField(required=True)
    marketing_consent = serializers.BooleanField(required=False, default=False)
    
    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Terms and conditions must be accepted.")
        return value
    
    def validate_privacy_policy_accepted(self, value):
        if not value:
            raise serializers.ValidationError("Privacy policy must be accepted.")
        return value

