from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from customer_enrollment.models import Customer
from .models import CustomerDocument, DocumentProcessingTask
from .services import DocumentProcessingService


class OCRProcessingTests(TestCase):
    """Tests for the OCR processing service"""

    def test_ocr_data_saved_and_text_block_count(self):
        """Document OCR results should be stored correctly"""
        # Insert a minimal customer record directly to match migration schema
        from django.db import connection
        import uuid
        customer_id = uuid.uuid4().hex
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO customers (id, external_id, status, risk_score, risk_level, created_at, updated_at) "
                "VALUES (%s, %s, 'pending', 0, 'unknown', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)",
                [customer_id, None],
            )

        test_file = SimpleUploadedFile("test.pdf", b"dummy", content_type="application/pdf")

        with patch("document_processing.models.document_upload_path", lambda i, f: f"docs/{f}"):
            document = CustomerDocument.objects.create(
                customer_id=customer_id,
                document_type="passport",
                file=test_file,
            )

        task = DocumentProcessingTask.objects.create(document=document, task_type="ocr")

        mocked_result = {
            "raw_text": "hello world from ocr",
            "structured_data": {"name": "John Doe"},
            "confidence": 0.9,
            "processing_time": 0.5,
        }

        with patch("document_processing.services.OCRService.extract_text", return_value=mocked_result), \
             patch("document_processing.services.DocumentProcessingService.validate_document", return_value=None):
            service = DocumentProcessingService()
            service._process_ocr(document, task)

        document.refresh_from_db()
        task.refresh_from_db()

        self.assertIsInstance(document.ocr_data, dict)
        self.assertEqual(document.ocr_data, {"raw_text": mocked_result["raw_text"]})
        self.assertEqual(
            task.result_data.get("text_blocks_found"),
            len(mocked_result["raw_text"].split()),
        )
