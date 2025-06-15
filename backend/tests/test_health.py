"""
Tests for health check endpoints
"""
from django.test import TestCase, Client
from django.urls import reverse
import json


class HealthCheckTestCase(TestCase):
    """Test cases for health check functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_health_check_endpoint(self):
        """Test that health check endpoint returns 200"""
        response = self.client.get('/api/health/')
        self.assertEqual(response.status_code, 200)
        
        # Check response content
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'CERES Backend API')
        self.assertIn('checks', data)
        self.assertIn('database', data['checks'])
        self.assertIn('cache', data['checks'])
    
    def test_healthz_endpoint(self):
        """Test that /healthz endpoint works (Railway standard)"""
        response = self.client.get('/healthz/')
        self.assertEqual(response.status_code, 200)
        
        # Check response content
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'CERES Backend API')
    
    def test_api_info_endpoint(self):
        """Test that API info endpoint returns correct information"""
        response = self.client.get('/api/health/info/')
        self.assertEqual(response.status_code, 200)
        
        # Check response content
        data = json.loads(response.content)
        self.assertEqual(data['name'], 'CERES API')
        self.assertIn('documentation', data)
        self.assertIn('endpoints', data)

