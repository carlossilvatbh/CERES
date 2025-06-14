"""
Customer Enrollment URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, CustomerAddressViewSet, CustomerDocumentViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customers')
router.register(r'addresses', CustomerAddressViewSet, basename='customer-addresses')
router.register(r'documents', CustomerDocumentViewSet, basename='customer-documents')

urlpatterns = [
    path('', include(router.urls)),
]

