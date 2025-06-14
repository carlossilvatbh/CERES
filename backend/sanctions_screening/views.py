"""
Sanctions Screening Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Q
import logging

from customer_enrollment.models import Customer
from .models import ScreeningSource, ScreeningResult, ScreeningBatch, ScreeningAlert, ScreeningConfiguration
from .serializers import (
    ScreeningSourceSerializer, ScreeningResultSerializer, ScreeningBatchSerializer,
    ScreeningAlertSerializer, ScreeningConfigurationSerializer, ScreeningRequestSerializer,
    BatchScreeningRequestSerializer, ScreeningSummarySerializer, ScreeningMatchSerializer
)
from .tasks import screen_customer, batch_screen_customers, create_screening_alert
from ceres_project.utils import success_response, paginated_response

logger = logging.getLogger('ceres')

class ScreeningSourceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening sources
    """
    queryset = ScreeningSource.objects.all()
    serializer_class = ScreeningSourceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter sources based on parameters"""
        queryset = super().get_queryset()
        
        source_type = self.request.query_params.get('source_type')
        if source_type:
            queryset = queryset.filter(source_type=source_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        jurisdiction = self.request.query_params.get('jurisdiction')
        if jurisdiction:
            queryset = queryset.filter(jurisdiction__icontains=jurisdiction)
        
        return queryset.order_by('source_type', 'name')
    
    def list(self, request, *args, **kwargs):
        """List screening sources"""
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get screening sources statistics
        """
        stats = {
            'total_sources': ScreeningSource.objects.count(),
            'active_sources': ScreeningSource.objects.filter(is_active=True).count(),
            'available_sources': ScreeningSource.objects.filter(is_available=True).count(),
            'by_type': {}
        }
        
        # Count by source type
        type_counts = ScreeningSource.objects.values('source_type').annotate(
            count=Count('id')
        ).order_by('source_type')
        
        for item in type_counts:
            stats['by_type'][item['source_type']] = item['count']
        
        return success_response(stats)

class ScreeningResultViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing screening results
    """
    queryset = ScreeningResult.objects.select_related('customer', 'source').all()
    serializer_class = ScreeningResultSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter results based on parameters"""
        queryset = super().get_queryset()
        
        customer_id = self.request.query_params.get('customer_id')
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
        
        source_code = self.request.query_params.get('source_code')
        if source_code:
            queryset = queryset.filter(source__code=source_code)
        
        match_found = self.request.query_params.get('match_found')
        if match_found is not None:
            queryset = queryset.filter(match_found=match_found.lower() == 'true')
        
        min_confidence = self.request.query_params.get('min_confidence')
        if min_confidence:
            try:
                queryset = queryset.filter(confidence_score__gte=float(min_confidence))
            except ValueError:
                pass
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List screening results with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginated_response(serializer.data, self.paginator, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class ScreeningViewSet(viewsets.ViewSet):
    """
    ViewSet for screening operations
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def screen_customer(self, request):
        """
        Screen a single customer
        """
        serializer = ScreeningRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        customer_id = serializer.validated_data['customer_id']
        source_codes = serializer.validated_data.get('source_codes')
        force_refresh = serializer.validated_data.get('force_refresh', False)
        
        # Verify customer exists
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return success_response(
                None,
                status_code=status.HTTP_404_NOT_FOUND,
                meta={'error': 'Customer not found'}
            )
        
        # Start screening task
        task = screen_customer.delay(
            str(customer_id),
            source_codes=source_codes,
            force_refresh=force_refresh
        )
        
        logger.info(f"Screening task started for customer {customer_id}", extra={
            'customer_id': str(customer_id),
            'task_id': task.id,
            'user_id': request.user.id
        })
        
        return success_response({
            'task_id': task.id,
            'customer_id': str(customer_id),
            'status': 'started',
            'message': 'Screening task started successfully'
        }, status_code=status.HTTP_202_ACCEPTED)
    
    @action(detail=False, methods=['post'])
    def batch_screen(self, request):
        """
        Start batch screening operation
        """
        serializer = BatchScreeningRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        name = serializer.validated_data['name']
        description = serializer.validated_data.get('description', '')
        customer_ids = serializer.validated_data['customer_ids']
        source_codes = serializer.validated_data.get('source_codes')
        
        # Verify customers exist
        customers = Customer.objects.filter(id__in=customer_ids)
        if customers.count() != len(customer_ids):
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'Some customers not found'}
            )
        
        # Get sources
        if source_codes:
            sources = ScreeningSource.objects.filter(
                code__in=source_codes,
                is_active=True
            )
        else:
            sources = ScreeningSource.objects.filter(is_active=True)
        
        # Create batch
        with transaction.atomic():
            batch = ScreeningBatch.objects.create(
                name=name,
                description=description,
                created_by=request.user
            )
            batch.customers.set(customers)
            batch.sources.set(sources)
        
        # Start batch processing
        task = batch_screen_customers.delay(str(batch.id))
        
        logger.info(f"Batch screening started: {batch.id}", extra={
            'batch_id': str(batch.id),
            'customer_count': customers.count(),
            'source_count': sources.count(),
            'task_id': task.id,
            'user_id': request.user.id
        })
        
        return success_response({
            'batch_id': str(batch.id),
            'task_id': task.id,
            'customer_count': customers.count(),
            'source_count': sources.count(),
            'status': 'started'
        }, status_code=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def customer_summary(self, request):
        """
        Get screening summary for a customer
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'customer_id parameter is required'}
            )
        
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return success_response(
                None,
                status_code=status.HTTP_404_NOT_FOUND,
                meta={'error': 'Customer not found'}
            )
        
        # Get screening results
        results = ScreeningResult.objects.filter(customer=customer)
        
        # Calculate summary statistics
        total_sources_checked = results.values('source').distinct().count()
        matches_found = results.filter(match_found=True).count()
        
        # Risk level breakdown
        high_risk_matches = results.filter(
            match_found=True,
            confidence_score__gte=90
        ).count()
        
        medium_risk_matches = results.filter(
            match_found=True,
            confidence_score__gte=70,
            confidence_score__lt=90
        ).count()
        
        low_risk_matches = results.filter(
            match_found=True,
            confidence_score__lt=70
        ).count()
        
        # Overall risk score (highest confidence match)
        highest_match = results.filter(match_found=True).order_by('-confidence_score').first()
        overall_risk_score = highest_match.confidence_score if highest_match else 0
        
        # Risk level
        if overall_risk_score >= 90:
            risk_level = 'high'
        elif overall_risk_score >= 70:
            risk_level = 'medium'
        elif overall_risk_score > 0:
            risk_level = 'low'
        else:
            risk_level = 'none'
        
        # Alerts count
        alerts_count = ScreeningAlert.objects.filter(
            customer=customer,
            status='active'
        ).count()
        
        # Last screened
        last_result = results.order_by('-created_at').first()
        last_screened = last_result.created_at if last_result else None
        
        summary_data = {
            'customer_id': customer_id,
            'total_sources_checked': total_sources_checked,
            'matches_found': matches_found,
            'high_risk_matches': high_risk_matches,
            'medium_risk_matches': medium_risk_matches,
            'low_risk_matches': low_risk_matches,
            'last_screened': last_screened,
            'overall_risk_score': overall_risk_score,
            'risk_level': risk_level,
            'alerts_count': alerts_count
        }
        
        return success_response(summary_data)
    
    @action(detail=False, methods=['get'])
    def customer_matches(self, request):
        """
        Get detailed matches for a customer
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'customer_id parameter is required'}
            )
        
        # Get matches
        matches = ScreeningResult.objects.filter(
            customer_id=customer_id,
            match_found=True
        ).select_related('source').order_by('-confidence_score')
        
        match_data = []
        for match in matches:
            match_data.append({
                'source_name': match.source.name,
                'source_code': match.source.code,
                'matched_name': match.matched_name,
                'confidence_score': match.confidence_score,
                'match_type': match.match_type,
                'entity_type': match.entity_type,
                'categories': match.categories,
                'sanctions_programs': match.sanctions_programs,
                'additional_info': match.match_details,
                'source_url': match.match_details.get('source_url', '')
            })
        
        return success_response(match_data)

class ScreeningBatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening batches
    """
    queryset = ScreeningBatch.objects.all()
    serializer_class = ScreeningBatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter batches based on user permissions"""
        queryset = super().get_queryset()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List screening batches with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginated_response(serializer.data, self.paginator, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

class ScreeningAlertViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening alerts
    """
    queryset = ScreeningAlert.objects.select_related('customer', 'source').all()
    serializer_class = ScreeningAlertSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter alerts based on parameters"""
        queryset = super().get_queryset()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        severity_filter = self.request.query_params.get('severity')
        if severity_filter:
            queryset = queryset.filter(severity=severity_filter)
        
        alert_type_filter = self.request.query_params.get('alert_type')
        if alert_type_filter:
            queryset = queryset.filter(alert_type=alert_type_filter)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List alerts with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginated_response(serializer.data, self.paginator, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """
        Acknowledge an alert
        """
        alert = self.get_object()
        
        alert.status = 'acknowledged'
        alert.action_taken_by = request.user
        alert.action_taken_at = timezone.now()
        alert.action_taken = request.data.get('action_taken', 'Alert acknowledged')
        alert.save()
        
        logger.info(f"Alert {alert.id} acknowledged by user {request.user.id}")
        
        return success_response({
            'alert_id': str(alert.id),
            'status': alert.status,
            'acknowledged_at': alert.action_taken_at
        })
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """
        Resolve an alert
        """
        alert = self.get_object()
        
        alert.status = 'resolved'
        alert.action_taken_by = request.user
        alert.action_taken_at = timezone.now()
        alert.action_taken = request.data.get('action_taken', 'Alert resolved')
        alert.save()
        
        logger.info(f"Alert {alert.id} resolved by user {request.user.id}")
        
        return success_response({
            'alert_id': str(alert.id),
            'status': alert.status,
            'resolved_at': alert.action_taken_at
        })

class ScreeningConfigurationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing screening configurations
    """
    queryset = ScreeningConfiguration.objects.all()
    serializer_class = ScreeningConfigurationSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        """List screening configurations"""
        queryset = self.get_queryset().order_by('-is_default', 'name')
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)

