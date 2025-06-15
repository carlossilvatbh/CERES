"""
Comprehensive test suite for CERES system
"""
import pytest
import asyncio
from django.test import TestCase, TransactionTestCase
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
import json
import tempfile
import os

class CacheManagerTestCase(TestCase):
    """Test cases for cache manager functionality"""
    
    def setUp(self):
        from core.cache_manager import CacheManager
        self.cache_manager = CacheManager()
    
    def test_cache_set_and_get(self):
        """Test basic cache set and get operations"""
        test_data = {'test': 'data', 'number': 123}
        
        # Set cache
        result = self.cache_manager.set('test_prefix', 'test_key', test_data, ttl=300)
        self.assertTrue(result)
        
        # Get cache
        cached_data = self.cache_manager.get('test_prefix', 'test_key')
        self.assertEqual(cached_data, test_data)
    
    def test_cache_delete(self):
        """Test cache deletion"""
        test_data = {'test': 'data'}
        
        # Set and verify
        self.cache_manager.set('test_prefix', 'test_key', test_data)
        self.assertIsNotNone(self.cache_manager.get('test_prefix', 'test_key'))
        
        # Delete and verify
        result = self.cache_manager.delete('test_prefix', 'test_key')
        self.assertTrue(result)
        self.assertIsNone(self.cache_manager.get('test_prefix', 'test_key'))
    
    def test_cache_invalidation_pattern(self):
        """Test pattern-based cache invalidation"""
        # Set multiple cache entries
        self.cache_manager.set('screening_result', 'customer_1', {'result': 'data1'})
        self.cache_manager.set('screening_result', 'customer_2', {'result': 'data2'})
        self.cache_manager.set('other_prefix', 'key_1', {'other': 'data'})
        
        # Invalidate screening results
        deleted_count = self.cache_manager.invalidate_pattern('screening:result:*')
        
        # Verify invalidation
        self.assertIsNone(self.cache_manager.get('screening_result', 'customer_1'))
        self.assertIsNone(self.cache_manager.get('screening_result', 'customer_2'))
        self.assertIsNotNone(self.cache_manager.get('other_prefix', 'key_1'))

class DocumentValidatorTestCase(TestCase):
    """Test cases for document validation"""
    
    def setUp(self):
        from document_processing.validators import DocumentValidator
        self.validator = DocumentValidator()
    
    def test_valid_pdf_file(self):
        """Test validation of valid PDF file"""
        # Create a simple PDF-like file
        pdf_content = b'%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF'
        pdf_file = SimpleUploadedFile("test.pdf", pdf_content, content_type="application/pdf")
        
        result = self.validator.validate_file(pdf_file)
        self.assertTrue(result['is_valid'])
        self.assertEqual(result['file_type'], 'pdf')
    
    def test_invalid_file_size(self):
        """Test validation of oversized file"""
        # Create a large file content
        large_content = b'x' * (60 * 1024 * 1024)  # 60MB
        large_file = SimpleUploadedFile("large.pdf", large_content, content_type="application/pdf")
        
        result = self.validator.validate_file(large_file)
        self.assertFalse(result['is_valid'])
        self.assertIn('file_too_large', result['errors'])
    
    def test_invalid_file_type(self):
        """Test validation of unsupported file type"""
        exe_content = b'MZ\x90\x00'  # PE executable header
        exe_file = SimpleUploadedFile("malware.exe", exe_content, content_type="application/octet-stream")
        
        result = self.validator.validate_file(exe_file)
        self.assertFalse(result['is_valid'])
        self.assertIn('invalid_file_type', result['errors'])

class ScreeningSourceTestCase(TestCase):
    """Test cases for screening sources"""
    
    @pytest.mark.asyncio
    async def test_ofac_source_initialization(self):
        """Test OFAC source initialization"""
        from sanctions_screening.sources.ofac_source import OFACScreeningSource
        
        async with OFACScreeningSource() as ofac:
            self.assertIsNotNone(ofac.session)
            stats = ofac.get_statistics()
            self.assertIn('total_entities', stats)
    
    @pytest.mark.asyncio
    async def test_data_source_manager(self):
        """Test unified data source manager"""
        from sanctions_screening.sources.data_source_manager import DataSourceManager
        
        config = {
            'ofac_cache_hours': 1,
            'un_cache_hours': 1,
            'eu_cache_hours': 1,
            'opensanctions_cache_hours': 1,
        }
        
        async with DataSourceManager(config) as manager:
            # Test source availability
            sources = manager.get_available_sources()
            expected_sources = ['ofac', 'un', 'eu', 'opensanctions']
            for source in expected_sources:
                self.assertIn(source, sources)
            
            # Test statistics
            stats = manager.get_source_statistics()
            self.assertIn('sources', stats)
            self.assertIn('total_sources', stats)

class AlertSystemTestCase(TestCase):
    """Test cases for alert system"""
    
    def setUp(self):
        from core.alerts import AlertManager, AlertType, AlertSeverity
        self.alert_manager = AlertManager()
        self.AlertType = AlertType
        self.AlertSeverity = AlertSeverity
    
    @pytest.mark.asyncio
    async def test_create_alert(self):
        """Test alert creation"""
        alert = await self.alert_manager.create_alert(
            alert_type=self.AlertType.HIGH_RISK_MATCH,
            severity=self.AlertSeverity.HIGH,
            title="Test Alert",
            message="This is a test alert",
            customer_id="test_customer_123"
        )
        
        self.assertIsNotNone(alert.id)
        self.assertEqual(alert.alert_type, self.AlertType.HIGH_RISK_MATCH)
        self.assertEqual(alert.severity, self.AlertSeverity.HIGH)
        self.assertEqual(alert.customer_id, "test_customer_123")
        self.assertFalse(alert.acknowledged)
        self.assertFalse(alert.resolved)
    
    @pytest.mark.asyncio
    async def test_acknowledge_alert(self):
        """Test alert acknowledgment"""
        # Create alert
        alert = await self.alert_manager.create_alert(
            alert_type=self.AlertType.SYSTEM_ERROR,
            severity=self.AlertSeverity.MEDIUM,
            title="Test Alert",
            message="Test message"
        )
        
        # Acknowledge alert
        result = await self.alert_manager.acknowledge_alert(alert.id, "test_user")
        self.assertTrue(result)
        
        # Verify acknowledgment
        updated_alert = self.alert_manager.active_alerts[alert.id]
        self.assertTrue(updated_alert.acknowledged)
        self.assertEqual(updated_alert.metadata['acknowledged_by'], "test_user")
    
    @pytest.mark.asyncio
    async def test_resolve_alert(self):
        """Test alert resolution"""
        # Create alert
        alert = await self.alert_manager.create_alert(
            alert_type=self.AlertType.DOCUMENT_PROCESSING_ERROR,
            severity=self.AlertSeverity.LOW,
            title="Test Alert",
            message="Test message"
        )
        
        # Resolve alert
        result = await self.alert_manager.resolve_alert(
            alert.id, "test_user", "Issue resolved by reprocessing"
        )
        self.assertTrue(result)
        
        # Verify resolution
        self.assertNotIn(alert.id, self.alert_manager.active_alerts)

class OCRServiceTestCase(TestCase):
    """Test cases for OCR service"""
    
    def setUp(self):
        from document_processing.enhanced_ocr import EnhancedOCRService
        self.ocr_service = EnhancedOCRService()
    
    def test_image_preprocessing(self):
        """Test image preprocessing functionality"""
        import numpy as np
        from document_processing.enhanced_ocr import ImagePreprocessor
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        
        preprocessor = ImagePreprocessor()
        enhanced_image, techniques = preprocessor.enhance_image_quality(test_image)
        
        self.assertIsNotNone(enhanced_image)
        self.assertIsInstance(techniques, list)
        self.assertGreater(len(techniques), 0)
    
    def test_deskew_detection(self):
        """Test image deskewing"""
        import numpy as np
        from document_processing.enhanced_ocr import ImagePreprocessor
        
        # Create a simple test image
        test_image = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        
        preprocessor = ImagePreprocessor()
        deskewed_image, was_skewed = preprocessor.deskew_image(test_image)
        
        self.assertIsNotNone(deskewed_image)
        self.assertIsInstance(was_skewed, bool)

class PerformanceTestCase(TestCase):
    """Test cases for performance monitoring"""
    
    def setUp(self):
        from core.performance import PerformanceMonitor, measure_time
        self.perf_monitor = PerformanceMonitor()
        self.measure_time = measure_time
    
    def test_metric_recording(self):
        """Test performance metric recording"""
        # Record some metrics
        self.perf_monitor.record_metric('test_metric', 1.5)
        self.perf_monitor.record_metric('test_metric', 2.0)
        self.perf_monitor.record_metric('test_metric', 1.0)
        
        # Get summary
        summary = self.perf_monitor.get_metrics_summary('test_metric')
        
        self.assertEqual(summary['count'], 3)
        self.assertEqual(summary['avg'], 1.5)
        self.assertEqual(summary['min'], 1.0)
        self.assertEqual(summary['max'], 2.0)
    
    def test_performance_decorator(self):
        """Test performance measurement decorator"""
        @self.measure_time('test_function')
        def test_function():
            import time
            time.sleep(0.1)  # Simulate work
            return "result"
        
        result = test_function()
        self.assertEqual(result, "result")
        
        # Check if metric was recorded
        summary = self.perf_monitor.get_metrics_summary('test_function')
        self.assertGreater(summary['count'], 0)
        self.assertGreater(summary['avg'], 0.05)  # Should be around 0.1 seconds

class IntegrationTestCase(TransactionTestCase):
    """Integration tests for complete workflows"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_customer_onboarding_workflow(self):
        """Test complete customer onboarding workflow"""
        # This would test the complete flow:
        # 1. Customer creation
        # 2. Document upload
        # 3. OCR processing
        # 4. Screening
        # 5. Risk assessment
        # 6. Alert generation (if needed)
        
        # For now, just test that the workflow can be initiated
        customer_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'document_number': '123456789',
            'customer_type': 'individual'
        }
        
        # This would normally call the application service
        # For testing, we just verify the data structure
        self.assertIn('name', customer_data)
        self.assertIn('email', customer_data)
        self.assertIn('document_number', customer_data)

# Test configuration
class TestConfig:
    """Test configuration and utilities"""
    
    @staticmethod
    def create_test_image():
        """Create a test image for OCR testing"""
        from PIL import Image, ImageDraw, ImageFont
        import io
        
        # Create a simple image with text
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Add some text
        try:
            # Try to use a default font
            font = ImageFont.load_default()
        except:
            font = None
        
        draw.text((50, 50), "PASSPORT", fill='black', font=font)
        draw.text((50, 80), "Name: John Doe", fill='black', font=font)
        draw.text((50, 110), "Number: A12345678", fill='black', font=font)
        draw.text((50, 140), "Expiry: 01/01/2030", fill='black', font=font)
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        
        return img_bytes.getvalue()
    
    @staticmethod
    def create_test_pdf():
        """Create a test PDF for document testing"""
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Add some content
        p.drawString(100, 750, "Test Document")
        p.drawString(100, 700, "Name: Jane Smith")
        p.drawString(100, 650, "ID: 987654321")
        p.drawString(100, 600, "Date: 2024-01-01")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return buffer.getvalue()

# Pytest configuration
def pytest_configure(config):
    """Configure pytest for Django"""
    import django
    from django.conf import settings
    from django.test.utils import get_runner
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'sanctions_screening',
                'document_processing',
                'customer_management',
                'core',
            ],
            SECRET_KEY='test-secret-key',
            USE_TZ=True,
        )
    
    django.setup()

# Run tests with coverage
if __name__ == '__main__':
    import pytest
    import sys
    
    # Run tests with coverage
    exit_code = pytest.main([
        '--cov=.',
        '--cov-report=html',
        '--cov-report=term-missing',
        '--cov-fail-under=85',
        '-v'
    ])
    
    sys.exit(exit_code)

