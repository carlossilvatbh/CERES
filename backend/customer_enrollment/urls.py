"""
Customer Enrollment URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CustomerViewSet, EnrollmentViewSet

router = DefaultRouter()
router.register(r'', CustomerViewSet, basename='customers')
router.register(r'enrollment', EnrollmentViewSet, basename='enrollment')

urlpatterns = [
    path('', include(router.urls)),
]

