"""
Document Processing URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DocumentViewSet, DocumentTemplateViewSet

router = DefaultRouter()
router.register(r'', DocumentViewSet, basename='documents')
router.register(r'templates', DocumentTemplateViewSet, basename='document-templates')

urlpatterns = [
    path('', include(router.urls)),
]

