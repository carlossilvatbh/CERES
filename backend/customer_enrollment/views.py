"""
Customer Enrollment Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
import logging

from .models import Customer, CustomerPersonalData, CustomerContactInfo, EnrollmentSession
from .serializers import (
    CustomerSerializer, EnrollmentSessionSerializer, EnrollmentStartSerializer,
    PersonalDataUpdateSerializer, ContactInfoUpdateSerializer, EnrollmentSubmitSerializer
)
from ceres_project.utils import success_response, paginated_response

logger = logging.getLogger('ceres')

class CustomerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing customers
    """
    queryset = Customer.objects.select_related('personal_data', 'contact_info').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter customers based on user permissions"""
        queryset = super().get_queryset()
        
        # Add filtering based on status, risk level, etc.
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        risk_level_filter = self.request.query_params.get('risk_level')
        if risk_level_filter:
            queryset = queryset.filter(risk_level=risk_level_filter)
        
        return queryset.order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """List customers with pagination"""
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return paginated_response(serializer.data, self.paginator, request)
        
        serializer = self.get_serializer(queryset, many=True)
        return success_response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve a specific customer"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return success_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cif(self, request, pk=None):
        """
        Get complete Customer Information File (CIF)
        """
        customer = self.get_object()
        
        # Gather all customer data
        cif_data = {
            'customer': CustomerSerializer(customer).data,
            'enrollment_sessions': EnrollmentSessionSerializer(
                customer.enrollment_sessions.all(), many=True
            ).data,
            'documents': [],  # Will be populated by document service
            'screening_results': [],  # Will be populated by screening service
            'risk_flags': [],  # Will be populated by risk service
            'cases': [],  # Will be populated by case management service
        }
        
        logger.info(f"CIF accessed for customer {customer.id}", extra={
            'customer_id': str(customer.id),
            'user_id': request.user.id
        })
        
        return success_response(cif_data)

class EnrollmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing enrollment sessions
    """
    queryset = EnrollmentSession.objects.select_related('customer').all()
    serializer_class = EnrollmentSessionSerializer
    
    def get_permissions(self):
        """
        Allow unauthenticated access for starting enrollment
        """
        if self.action == 'start':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a new enrollment session
        """
        serializer = EnrollmentStartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create new customer
            customer = Customer.objects.create()
            
            # Create enrollment session
            session = EnrollmentSession.objects.create(
                customer=customer,
                status='started',
                current_step='personal_data'
            )
            
            # Generate resume token
            resume_token = session.generate_resume_token()
            
            # Create initial contact info if email/phone provided
            contact_data = {}
            if serializer.validated_data.get('email'):
                contact_data['email_primary'] = serializer.validated_data['email']
            if serializer.validated_data.get('phone'):
                contact_data['phone_primary'] = serializer.validated_data['phone']
            
            if contact_data:
                CustomerContactInfo.objects.create(
                    customer=customer,
                    **contact_data
                )
        
        logger.info(f"Enrollment started for customer {customer.id}", extra={
            'customer_id': str(customer.id),
            'session_id': str(session.id)
        })
        
        response_data = {
            'session_id': session.id,
            'customer_id': customer.id,
            'resume_token': resume_token,
            'current_step': session.current_step,
            'status': session.status
        }
        
        return success_response(response_data, status_code=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get enrollment session status
        """
        session = self.get_object()
        serializer = self.get_serializer(session)
        return success_response(serializer.data)
    
    @action(detail=True, methods=['put'])
    def personal_data(self, request, pk=None):
        """
        Update personal data for enrollment session
        """
        session = self.get_object()
        
        if session.status not in ['started', 'personal_data_completed']:
            return success_response(
                None, 
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'Cannot update personal data at this stage'}
            )
        
        serializer = PersonalDataUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create or update personal data
            personal_data, created = CustomerPersonalData.objects.get_or_create(
                customer=session.customer,
                defaults=serializer.validated_data
            )
            
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(personal_data, attr, value)
                personal_data.save()
            
            # Update session status
            session.status = 'personal_data_completed'
            session.current_step = 'documents'
            session.completion_percentage = 25
            session.save()
        
        logger.info(f"Personal data updated for customer {session.customer.id}", extra={
            'customer_id': str(session.customer.id),
            'session_id': str(session.id)
        })
        
        return success_response({
            'status': session.status,
            'current_step': session.current_step,
            'completion_percentage': session.completion_percentage
        })
    
    @action(detail=True, methods=['put'])
    def contact_info(self, request, pk=None):
        """
        Update contact information for enrollment session
        """
        session = self.get_object()
        
        serializer = ContactInfoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Create or update contact info
            contact_info, created = CustomerContactInfo.objects.get_or_create(
                customer=session.customer,
                defaults=serializer.validated_data
            )
            
            if not created:
                for attr, value in serializer.validated_data.items():
                    setattr(contact_info, attr, value)
                contact_info.save()
        
        logger.info(f"Contact info updated for customer {session.customer.id}", extra={
            'customer_id': str(session.customer.id),
            'session_id': str(session.id)
        })
        
        return success_response({
            'status': session.status,
            'current_step': session.current_step,
            'completion_percentage': session.completion_percentage
        })
    
    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """
        Submit enrollment for review
        """
        session = self.get_object()
        
        if session.status != 'documents_uploaded':
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'Cannot submit enrollment at this stage'}
            )
        
        serializer = EnrollmentSubmitSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            # Update session
            session.status = 'submitted'
            session.current_step = 'review'
            session.completion_percentage = 100
            session.completed_at = timezone.now()
            session.save()
            
            # Update customer status
            session.customer.status = 'in_review'
            session.customer.save()
            
            # Store consent data
            session.session_data.update({
                'terms_accepted': serializer.validated_data['terms_accepted'],
                'privacy_policy_accepted': serializer.validated_data['privacy_policy_accepted'],
                'marketing_consent': serializer.validated_data.get('marketing_consent', False),
                'submitted_at': timezone.now().isoformat()
            })
            session.save()
        
        logger.info(f"Enrollment submitted for customer {session.customer.id}", extra={
            'customer_id': str(session.customer.id),
            'session_id': str(session.id)
        })
        
        # TODO: Trigger screening and risk assessment processes
        
        return success_response({
            'status': session.status,
            'customer_status': session.customer.status,
            'completion_percentage': session.completion_percentage,
            'message': 'Enrollment submitted successfully for review'
        })
    
    @action(detail=False, methods=['get'])
    def resume(self, request):
        """
        Resume enrollment session using token
        """
        resume_token = request.query_params.get('token')
        if not resume_token:
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'Resume token is required'}
            )
        
        try:
            session = EnrollmentSession.objects.get(resume_token=resume_token)
        except EnrollmentSession.DoesNotExist:
            return success_response(
                None,
                status_code=status.HTTP_404_NOT_FOUND,
                meta={'error': 'Invalid resume token'}
            )
        
        if session.is_expired():
            return success_response(
                None,
                status_code=status.HTTP_400_BAD_REQUEST,
                meta={'error': 'Resume token has expired'}
            )
        
        # Update last activity
        session.last_activity_at = timezone.now()
        session.save()
        
        serializer = self.get_serializer(session)
        return success_response(serializer.data)

