"""
Pytest configuration and fixtures for CERES testing.
"""

import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from unittest.mock import Mock, patch
import factory
from faker import Faker

from sanctions_screening.models import Customer, ScreeningResult, ScreeningAlert

fake = Faker()
User = get_user_model()

@pytest.fixture
def api_client():
    """Provide an API client for testing."""
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    """Provide an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

@pytest.fixture
def admin_user():
    """Create an admin test user."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123'
    )

@pytest.fixture
def customer():
    """Create a test customer."""
    return Customer.objects.create(
        name=fake.name(),
        email=fake.email(),
        document_number=fake.ssn(),
        phone=fake.phone_number(),
        address=fake.address(),
        risk_level='medium'
    )

@pytest.fixture
def screening_result(customer):
    """Create a test screening result."""
    return ScreeningResult.objects.create(
        customer=customer,
        results={
            'ofac': {'status': 'completed', 'matches': []},
            'un': {'status': 'completed', 'matches': []}
        },
        status='completed'
    )

@pytest.fixture
def screening_alert(customer):
    """Create a test screening alert."""
    return ScreeningAlert.objects.create(
        customer=customer,
        source='ofac',
        match_data={
            'name': 'Test Match',
            'score': 85,
            'details': 'High confidence match'
        },
        risk_score=85,
        status='pending'
    )

@pytest.fixture
def mock_celery():
    """Mock Celery tasks for testing."""
    with patch('sanctions_screening.tasks.screen_customer.delay') as mock_task:
        mock_task.return_value = Mock(id='test-task-id')
        yield mock_task

@pytest.fixture
def mock_data_source():
    """Mock external data source."""
    with patch('sanctions_screening.sources.data_source_manager.DataSourceManager') as mock_manager:
        mock_instance = Mock()
        mock_manager.return_value = mock_instance
        mock_instance.screen_customer.return_value = {
            'status': 'completed',
            'matches': [],
            'source': 'test'
        }
        yield mock_instance

class CustomerFactory(factory.django.DjangoModelFactory):
    """Factory for creating test customers."""
    
    class Meta:
        model = Customer
    
    name = factory.Faker('name')
    email = factory.Faker('email')
    document_number = factory.Faker('ssn')
    phone = factory.Faker('phone_number')
    address = factory.Faker('address')
    risk_level = factory.Iterator(['low', 'medium', 'high'])

class UserFactory(factory.django.DjangoModelFactory):
    """Factory for creating test users."""
    
    class Meta:
        model = User
    
    username = factory.Faker('user_name')
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True

@pytest.fixture
def customer_factory():
    """Provide customer factory."""
    return CustomerFactory

@pytest.fixture
def user_factory():
    """Provide user factory."""
    return UserFactory
