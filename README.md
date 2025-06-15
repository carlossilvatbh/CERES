# CERES - Compliance and Risk Evaluation System

## 🚀 Complete Implementation - Version 2.0

### ✅ **Critical Deployment Fixes**
- **nixpacks.toml**: Complete Railway.app configuration with PostgreSQL, Redis, Tesseract
- **Modular Settings**: Structured configuration (base/development/production)
- **Railway.json**: Multi-service configuration (web, worker, beat)
- **PostgreSQL**: Migration from SQLite to PostgreSQL with dj_database_url
- **Deployment Scripts**: Automation for Celery workers

### 🔍 **Implemented Screening Sources**
- **OFAC (US Treasury)**: Official XML download and parsing
- **UN Consolidated List**: United Nations API with XML fallback
- **EU Sanctions**: European Union consolidated list
- **OpenSanctions PEP**: Politically Exposed Persons database
- **DataSourceManager**: Unified manager with parallel search

### 🧠 **Advanced OCR**
- **Image Preprocessing**: Deskewing, noise reduction, contrast enhancement
- **Multiple Configurations**: PSM 3, 6, 7 with adaptive threshold
- **Structured Extraction**: Specific parsing for passports, ID cards, driver licenses
- **Robust Error Handling**: Fallbacks and confidence scoring

### ⚡ **Distributed Cache System**
- **Redis Cache**: Intelligent caching with configurable TTL
- **Automatic Invalidation**: Based on domain events
- **Performance Monitoring**: Execution and memory metrics
- **Batch Processing**: Optimization for large volumes

### 🚨 **Real-time Alert System**
- **WebSocket**: Instant alerts via channels/channels-redis
- **Configurable Severity**: Low, Medium, High, Critical
- **Specific Types**: High-risk match, document errors, system errors
- **Acknowledge/Resolve**: Complete management workflow

### 🏗️ **Domain-Driven Architecture**
- **Clear Boundaries**: Customer, Document, Screening, Alerting
- **Event-Driven**: Domain events with event bus
- **Repository Pattern**: Abstract interfaces for persistence
- **Application Services**: Complex operation orchestration

### 🌍 **Internationalization**
- **Multiple Languages**: Portuguese (BR), English, Spanish
- **Complete Translations**: UI, error messages, alerts
- **Localized Formatting**: Dates, currencies, numbers
- **i18n Utilities**: Dynamic translation helpers

### 🛡️ **Critical Bug Fixes**
- **BUG-01**: Robust document validation (MIME, size, security)
- **BUG-02**: Celery error handling with dict.get() and fallbacks
- **BUG-03**: Fixed infinite re-render with useCallback and useMemo

### 📊 **Monitoring and Performance**
- **Performance Decorators**: Automatic execution time measurement
- **Memory Monitoring**: Alerts for excessive memory usage
- **Database Optimization**: Slow query logging
- **Cache Statistics**: Detailed cache metrics

## 🔧 **Technologies Used**

### Backend
- **Django 5.0.4** + **DRF 3.15.2**
- **PostgreSQL** with dj_database_url
- **Redis** for cache and WebSocket
- **Celery 5.4.1** for async processing
- **Channels 4.0.0** for WebSocket
- **OpenCV + Tesseract** for advanced OCR

### Screening & APIs
- **aiohttp** for async requests
- **fuzzywuzzy** for fuzzy matching
- **xml.etree.ElementTree** for XML parsing
- **requests** for REST APIs

### Deployment
- **Railway.app** as platform
- **Gunicorn** as WSGI server
- **WhiteNoise** for static files
- **Nixpacks** for automated builds

## 📁 **Project Structure**

```
CERES/
├── backend/
│   ├── ceres_project/
│   │   ├── settings/          # Modular settings
│   │   │   ├── base.py
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── celery.py          # Optimized Celery config
│   │   └── routing.py         # WebSocket routing
│   ├── core/                  # Central utilities
│   │   ├── alerts.py          # Alert system
│   │   ├── cache_manager.py   # Distributed cache
│   │   ├── domain.py          # Domain-driven design
│   │   ├── i18n.py           # Internationalization
│   │   ├── performance.py     # Monitoring
│   │   └── monitoring.py      # Health checks
│   ├── sanctions_screening/
│   │   └── sources/           # Screening sources
│   │       ├── ofac_source.py
│   │       ├── un_source.py
│   │       ├── eu_source.py
│   │       ├── opensanctions_source.py
│   │       └── data_source_manager.py
│   ├── document_processing/
│   │   ├── enhanced_ocr.py    # Advanced OCR
│   │   └── validators.py      # Robust validation
│   ├── tests/                 # Comprehensive tests
│   │   └── test_comprehensive.py
│   └── requirements.txt       # Updated dependencies
├── frontend/
│   ├── src/
│   │   ├── hooks/
│   │   │   └── useApi.js      # Optimized hook
│   │   └── pages/
│   │       └── DashboardPage.jsx  # Optimized component
├── scripts/                   # Deployment scripts
│   ├── start_worker.sh
│   └── start_beat.sh
├── docs/                      # Documentation
│   ├── API_DOCUMENTATION.md
│   ├── DEPLOYMENT_GUIDE.md
│   ├── USER_MANUAL.md
│   └── MAINTENANCE_GUIDE.md
├── nixpacks.toml             # Railway configuration
├── railway.json              # Multi-services
├── .env.railway              # Environment template
└── README.md                 # This file
```

## 🚀 **Railway.app Deployment**

### Prerequisites
1. Railway.app account
2. Connected GitHub repository
3. Configured environment variables

### Required Services
- **PostgreSQL**: Main database
- **Redis**: Cache and WebSocket
- **Web Service**: Django application
- **Worker Service**: Celery worker
- **Beat Service**: Celery beat (optional)

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://...
REDIS_URL=redis://...

# Django
SECRET_KEY=your-secret-key
DEBUG=False
DJANGO_ENVIRONMENT=production

# Screening APIs
OPENSANCTIONS_API_KEY=your-api-key  # Optional

# Email (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## 📈 **Performance Metrics**

### Screening
- **OFAC**: ~2-3s for complete download
- **UN**: ~1-2s via JSON API
- **EU**: ~3-4s for XML parsing
- **OpenSanctions**: ~0.5s per query

### OCR
- **Simple documents**: ~1-2s
- **Complex documents**: ~3-5s
- **Preprocessing**: +0.5-1s
- **Average confidence**: 85-95%

### Cache
- **Hit rate**: >90% after warm-up
- **Response time**: <50ms for cache hits
- **Default TTL**: 24h for screening, 2h for OCR

## 🔒 **Security**

### Document Validation
- **MIME type verification**
- **File size limits** (50MB)
- **Magic number validation**
- **Virus scanning ready**

### API Security
- **JWT Authentication**
- **Configured CORS**
- **Rate limiting ready**
- **Input sanitization**

### Production Security
- **HTTPS enforcement**
- **HSTS headers**
- **XSS protection**
- **CSRF protection**

## 📚 **Technical Documentation**

- **API Documentation**: `/api/schema/swagger-ui/`
- **Admin Interface**: `/admin/`
- **Health Check**: `/health/`
- **Metrics**: `/metrics/` (Prometheus ready)

## 🧪 **Testing**

### Test Coverage
- **Unit Tests**: Core functionality
- **Integration Tests**: Complete workflows
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability scanning

### Running Tests
```bash
# Install test dependencies
pip install -r requirements.txt

# Run tests with coverage
pytest --cov=. --cov-report=html --cov-fail-under=85

# Run specific test categories
pytest tests/test_comprehensive.py::CacheManagerTestCase
pytest tests/test_comprehensive.py::ScreeningSourceTestCase
```

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Implement tests
4. Commit changes
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License. See the LICENSE file for details.

---

**Developed with ❤️ for compliance and risk management**

