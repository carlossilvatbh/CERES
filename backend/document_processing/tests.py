from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch

from customer_enrollment.models import Customer, EnrollmentSession
from document_processing.models import CustomerDocument, DocumentProcessingTask
from document_processing.services import DocumentProcessingService
import uuid


@override_settings(
    MIGRATION_MODULES={"customer_enrollment": None, "document_processing": None}
)
class DocumentUploadSessionTest(TestCase):
    """Tests for document upload during an enrollment session"""

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(created_by=self.user)
        self.session = EnrollmentSession.objects.create(
            customer=self.customer,
            status="personal_data_completed",
        )

    @patch(
        "document_processing.views.DocumentProcessingService.start_document_processing"
    )
    def test_upload_updates_enrollment_session(self, mock_start):
        file_obj = SimpleUploadedFile(
            "test.pdf", b"%PDF-1.4 test", content_type="application/pdf"
        )
        url = "/api/v1/documents/upload/"
        data = {
            "customer_id": str(self.customer.id),
            "document_type": "passport",
            "file": file_obj,
        }

        response = self.client.post(url, data, format="multipart")

        self.assertEqual(response.status_code, 201)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, "documents_uploaded")
        self.assertEqual(self.session.current_step, "review")
        self.assertEqual(self.session.completion_percentage, 75)
        mock_start.assert_called_once()
        self.assertEqual(CustomerDocument.objects.count(), 1)


@override_settings(
    MIGRATION_MODULES={"customer_enrollment": None, "document_processing": None}
)
class DocumentListPaginationTest(TestCase):
    """Tests for DocumentViewSet list pagination"""

    def setUp(self):
        self.user = User.objects.create_user(username="tester2", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(created_by=self.user)

        for i in range(25):
            CustomerDocument.objects.create(
                customer=self.customer,
                document_type="passport",
                file=SimpleUploadedFile(
                    f"file{i}.pdf", b"data", content_type="application/pdf"
                ),
                file_name=f"file{i}.pdf",
                file_size=4,
                file_hash=str(uuid.uuid4()),
                mime_type="application/pdf",
            )

    def test_list_paginated_response(self):
        url = f"/api/v1/documents/?customer_id={self.customer.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]["data"]), 20)


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

