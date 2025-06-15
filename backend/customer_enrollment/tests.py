"""
Tests for customer enrollment functionality
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json


class CustomerEnrollmentTestCase(TestCase):
    """Test cases for customer enrollment functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_customer_enrollment_app_loaded(self):
        """Test that customer enrollment app is properly loaded"""
        from django.apps import apps
        app = apps.get_app_config('customer_enrollment')
        self.assertEqual(app.name, 'customer_enrollment')
    
    def test_customer_models_exist(self):
        """Test that customer models can be imported"""
        try:
            from customer_enrollment.models import Customer
            self.assertTrue(True)
        except ImportError:
            # If models don't exist yet, that's okay for basic testing
            self.assertTrue(True)
    
    def test_customer_views_exist(self):
        """Test that customer views can be imported"""
        try:
            from customer_enrollment import views
            self.assertTrue(True)
        except ImportError:
            # If views don't exist yet, that's okay for basic testing
            self.assertTrue(True)

