from django.test import TestCase
from rest_framework import status

from ceres_project.utils import success_response


class SuccessResponseTest(TestCase):
    """Tests for the success_response utility function"""

    def test_success_response_with_meta(self):
        meta = {"page": 2}
        response = success_response({"foo": "bar"}, meta=meta)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["meta"], meta)
        self.assertEqual(response.data["data"], {"foo": "bar"})

    def test_success_response_without_meta(self):
        response = success_response({"foo": "bar"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertNotIn("meta", response.data)

