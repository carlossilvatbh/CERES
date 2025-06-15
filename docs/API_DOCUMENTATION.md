# CERES API Documentation

## Overview

The CERES (Compliance and Risk Evaluation System) API provides comprehensive endpoints for customer onboarding, document processing, sanctions screening, and risk assessment.

## Base URL

```
Production: https://your-app.railway.app/api/v1/
Development: http://localhost:8000/api/v1/
```

## Authentication

CERES uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Obtaining a Token

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "username": "your-username",
    "password": "your-password"
}
```

Response:
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## Core Endpoints

### Customer Management

#### Create Customer
```http
POST /api/v1/customers/
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "John Doe",
    "email": "john.doe@example.com",
    "document_number": "123456789",
    "customer_type": "individual",
    "birth_date": "1990-01-01",
    "nationality": "US"
}
```

Response:
```json
{
    "id": "customer_123",
    "name": "John Doe",
    "email": "john.doe@example.com",
    "document_number": "123456789",
    "customer_type": "individual",
    "risk_level": "low",
    "created_at": "2024-01-01T10:00:00Z",
    "status": "active"
}
```

#### Get Customer
```http
GET /api/v1/customers/{customer_id}/
Authorization: Bearer <token>
```

#### Update Customer
```http
PUT /api/v1/customers/{customer_id}/
Content-Type: application/json
Authorization: Bearer <token>

{
    "name": "John Smith",
    "email": "john.smith@example.com"
}
```

#### List Customers
```http
GET /api/v1/customers/?page=1&page_size=20&search=john
Authorization: Bearer <token>
```

### Document Processing

#### Upload Document
```http
POST /api/v1/documents/upload/
Content-Type: multipart/form-data
Authorization: Bearer <token>

{
    "customer_id": "customer_123",
    "document_type": "passport",
    "file": <binary-file-data>
}
```

Response:
```json
{
    "document_id": "doc_456",
    "customer_id": "customer_123",
    "document_type": "passport",
    "status": "processing",
    "uploaded_at": "2024-01-01T10:00:00Z",
    "file_size": 2048576,
    "file_name": "passport.pdf"
}
```

#### Get Document Processing Status
```http
GET /api/v1/documents/{document_id}/status/
Authorization: Bearer <token>
```

Response:
```json
{
    "document_id": "doc_456",
    "status": "completed",
    "processing_time": 3.45,
    "ocr_result": {
        "confidence": 92.5,
        "extracted_text": "PASSPORT\nName: John Doe\nNumber: A12345678",
        "extracted_data": {
            "name": "John Doe",
            "document_number": "A12345678",
            "expiry_date": "2030-01-01"
        }
    },
    "completed_at": "2024-01-01T10:03:45Z"
}
```

#### Get Document OCR Result
```http
GET /api/v1/documents/{document_id}/ocr/
Authorization: Bearer <token>
```

### Sanctions Screening

#### Screen Customer
```http
POST /api/v1/screening/screen/
Content-Type: application/json
Authorization: Bearer <token>

{
    "customer_id": "customer_123",
    "sources": ["ofac", "un", "eu", "opensanctions"],
    "threshold": 80
}
```

Response:
```json
{
    "screening_id": "screen_789",
    "customer_id": "customer_123",
    "status": "completed",
    "total_matches": 2,
    "high_risk_matches": 1,
    "risk_level": "high",
    "screened_at": "2024-01-01T10:00:00Z",
    "matches": [
        {
            "source": "ofac",
            "matched_name": "John Doe",
            "confidence": 95.2,
            "list_type": "SDN",
            "match_details": {
                "original_name": "JOHN DOE",
                "aliases": ["J. DOE", "JOHNNY DOE"],
                "birth_date": "1990-01-01",
                "nationality": "US"
            }
        }
    ]
}
```

#### Get Screening History
```http
GET /api/v1/screening/history/{customer_id}/
Authorization: Bearer <token>
```

#### Get Screening Sources Status
```http
GET /api/v1/screening/sources/status/
Authorization: Bearer <token>
```

Response:
```json
{
    "sources": {
        "ofac": {
            "status": "active",
            "last_updated": "2024-01-01T08:00:00Z",
            "total_entities": 15420,
            "response_time_ms": 245
        },
        "un": {
            "status": "active",
            "last_updated": "2024-01-01T08:00:00Z",
            "total_entities": 8932,
            "response_time_ms": 156
        },
        "eu": {
            "status": "active",
            "last_updated": "2024-01-01T08:00:00Z",
            "total_entities": 3421,
            "response_time_ms": 312
        },
        "opensanctions": {
            "status": "active",
            "last_updated": "2024-01-01T08:00:00Z",
            "total_entities": 45123,
            "response_time_ms": 89
        }
    }
}
```

### Risk Assessment

#### Assess Customer Risk
```http
POST /api/v1/risk/assess/
Content-Type: application/json
Authorization: Bearer <token>

{
    "customer_id": "customer_123"
}
```

Response:
```json
{
    "customer_id": "customer_123",
    "overall_risk_score": 75.5,
    "risk_level": "medium",
    "risk_factors": {
        "sanctions_risk": 85.0,
        "pep_risk": 60.0,
        "geographic_risk": 45.0,
        "document_risk": 20.0
    },
    "recommendations": [
        "Enhanced due diligence required",
        "Regular monitoring recommended",
        "Document verification needed"
    ],
    "assessed_at": "2024-01-01T10:00:00Z"
}
```

### Alerts

#### Get Active Alerts
```http
GET /api/v1/alerts/?status=active&severity=high
Authorization: Bearer <token>
```

Response:
```json
{
    "count": 5,
    "results": [
        {
            "id": "alert_101",
            "alert_type": "high_risk_match",
            "severity": "high",
            "title": "High-Risk Match Found",
            "message": "Customer John Doe matched OFAC SDN list with 95.2% confidence",
            "customer_id": "customer_123",
            "created_at": "2024-01-01T10:00:00Z",
            "acknowledged": false,
            "resolved": false
        }
    ]
}
```

#### Acknowledge Alert
```http
POST /api/v1/alerts/{alert_id}/acknowledge/
Content-Type: application/json
Authorization: Bearer <token>

{
    "notes": "Reviewed by compliance team"
}
```

#### Resolve Alert
```http
POST /api/v1/alerts/{alert_id}/resolve/
Content-Type: application/json
Authorization: Bearer <token>

{
    "resolution": "False positive - different person",
    "notes": "Verified through additional documentation"
}
```

## WebSocket Endpoints

### Real-time Alerts
```javascript
const socket = new WebSocket('wss://your-app.railway.app/ws/alerts/');

socket.onmessage = function(event) {
    const alert = JSON.parse(event.data);
    console.log('New alert:', alert);
};
```

Alert message format:
```json
{
    "type": "alert",
    "alert": {
        "id": "alert_102",
        "alert_type": "document_processing_error",
        "severity": "medium",
        "title": "Document Processing Failed",
        "message": "OCR processing failed for document doc_456",
        "customer_id": "customer_123",
        "created_at": "2024-01-01T10:05:00Z"
    }
}
```

## System Endpoints

### Health Check
```http
GET /health/
```

Response:
```json
{
    "service": "CERES",
    "version": "2.0.0",
    "overall_status": "healthy",
    "timestamp": "2024-01-01T10:00:00Z",
    "uptime": "5d 12h 30m",
    "checks": {
        "database": {
            "status": "healthy",
            "response_time_ms": 45.2
        },
        "cache": {
            "status": "healthy",
            "response_time_ms": 12.1
        },
        "redis": {
            "status": "healthy",
            "response_time_ms": 8.5
        },
        "system": {
            "status": "healthy",
            "cpu_percent": 25.4,
            "memory_percent": 68.2
        }
    }
}
```

### Metrics
```http
GET /metrics/
```

Response (Prometheus format):
```
ceres_cpu_usage_percent 25.4
ceres_memory_usage_percent 68.2
ceres_database_queries_total 1542
ceres_screening_requests_total 89
ceres_cache_hits_total 2341
ceres_cache_misses_total 156
```

## Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid customer data provided",
        "details": {
            "email": ["Enter a valid email address"],
            "document_number": ["This field is required"]
        },
        "timestamp": "2024-01-01T10:00:00Z"
    }
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `VALIDATION_ERROR` | 400 | Request data validation failed |
| `AUTHENTICATION_REQUIRED` | 401 | Valid authentication required |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Internal server error |
| `SERVICE_UNAVAILABLE` | 503 | Service temporarily unavailable |

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Authentication endpoints**: 5 requests per minute
- **Document upload**: 10 requests per minute
- **Screening requests**: 20 requests per minute
- **General API**: 100 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Pagination

List endpoints support pagination:

```http
GET /api/v1/customers/?page=2&page_size=50
```

Response:
```json
{
    "count": 1250,
    "next": "https://api.example.com/customers/?page=3&page_size=50",
    "previous": "https://api.example.com/customers/?page=1&page_size=50",
    "results": [...]
}
```

## Filtering and Search

Most list endpoints support filtering and search:

```http
GET /api/v1/customers/?search=john&risk_level=high&created_after=2024-01-01
GET /api/v1/alerts/?severity=high&alert_type=high_risk_match&acknowledged=false
```

## API Versioning

The API uses URL versioning. Current version is `v1`:

```
/api/v1/customers/
/api/v2/customers/  # Future version
```

## SDKs and Libraries

### Python SDK
```python
from ceres_client import CeresClient

client = CeresClient(
    base_url='https://your-app.railway.app',
    api_key='your-api-key'
)

# Create customer
customer = client.customers.create({
    'name': 'John Doe',
    'email': 'john@example.com',
    'document_number': '123456789'
})

# Screen customer
screening = client.screening.screen_customer(
    customer_id=customer['id'],
    sources=['ofac', 'un', 'eu']
)
```

### JavaScript SDK
```javascript
import { CeresClient } from '@ceres/client';

const client = new CeresClient({
    baseUrl: 'https://your-app.railway.app',
    apiKey: 'your-api-key'
});

// Create customer
const customer = await client.customers.create({
    name: 'John Doe',
    email: 'john@example.com',
    documentNumber: '123456789'
});

// Screen customer
const screening = await client.screening.screenCustomer({
    customerId: customer.id,
    sources: ['ofac', 'un', 'eu']
});
```

## Support

For API support and questions:

- **Documentation**: [https://docs.ceres-system.com](https://docs.ceres-system.com)
- **Support Email**: support@ceres-system.com
- **GitHub Issues**: [https://github.com/carlossilvatbh/CERES/issues](https://github.com/carlossilvatbh/CERES/issues)

---

*Last updated: January 2024*

