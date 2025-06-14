"""
Sanctions Screening URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ScreeningSourceViewSet, ScreeningResultViewSet, ScreeningViewSet,
    ScreeningBatchViewSet, ScreeningAlertViewSet, ScreeningConfigurationViewSet
)

router = DefaultRouter()
router.register(r'sources', ScreeningSourceViewSet, basename='screening-sources')
router.register(r'results', ScreeningResultViewSet, basename='screening-results')
router.register(r'operations', ScreeningViewSet, basename='screening-operations')
router.register(r'batches', ScreeningBatchViewSet, basename='screening-batches')
router.register(r'alerts', ScreeningAlertViewSet, basename='screening-alerts')
router.register(r'configurations', ScreeningConfigurationViewSet, basename='screening-configurations')

urlpatterns = [
    path('', include(router.urls)),
]

