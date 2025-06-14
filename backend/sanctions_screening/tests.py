from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from customer_enrollment.models import Customer
from sanctions_screening.models import (
    ScreeningSource,
    ScreeningResult,
    ScreeningBatch,
    ScreeningAlert,
)


@override_settings(
    MIGRATION_MODULES={
        "customer_enrollment": None,
        "sanctions_screening": None,
    }
)
class ScreeningPaginationTests(TestCase):
    """Tests for paginated list endpoints"""

    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="pass")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.customer = Customer.objects.create(created_by=self.user)

        self.source = ScreeningSource.objects.create(
            name="Test Source",
            code="TSRC",
            source_type="sanctions",
        )

        # create screening results
        for i in range(25):
            ScreeningResult.objects.create(
                customer=self.customer,
                source=self.source,
                query_name="John Doe",
            )

        # create batches
        for i in range(25):
            ScreeningBatch.objects.create(
                name=f"batch{i}",
                created_by=self.user,
            )

        # create alerts
        for i in range(25):
            ScreeningAlert.objects.create(
                alert_type="high_risk_match",
                severity="high",
                status="active",
                title=f"alert {i}",
                message="msg",
            )

    def test_results_list_paginated(self):
        url = f"/api/v1/screening/results/?customer_id={self.customer.id}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]["data"]), 20)

    def test_batches_list_paginated(self):
        response = self.client.get("/api/v1/screening/batches/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]["data"]), 20)

    def test_alerts_list_paginated(self):
        response = self.client.get("/api/v1/screening/alerts/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 25)
        self.assertEqual(len(response.data["results"]["data"]), 20)
