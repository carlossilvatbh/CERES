# CERES - Customer Enrollment and Risk Evaluation System

<div align="center">
  <img src="docs/assets/ceres-logo.png" alt="CERES Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
  [![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
  [![Node.js](https://img.shields.io/badge/Node.js-20.0+-green.svg)](https://nodejs.org/)
  
  **Comprehensive KYC and Compliance System for Financial Institutions**
  
  [🚀 Demo Live](https://jgngsogp.manus.space) | [📖 Documentation](docs/) | [🐛 Issues](https://github.com/carlossilvatbh/CERES/issues) | [💬 Discussions](https://github.com/carlossilvatbh/CERES/discussions)
</div>

## 📋 Table of Contents

- [About the Project](#about-the-project)
- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Testing Guide](docs/testing-guide.md)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## 🎯 About the Project

CERES is a comprehensive compliance and risk assessment system designed specifically for financial institutions. It provides advanced KYC (Know Your Customer) capabilities, sanctions screening, document processing, and compliance reporting with support for international regulations.

### ✨ Key Features

- **🔍 Automated Screening**: Verification against 20+ international data sources (OFAC, UN, EU, etc.)
- **📄 Document Processing**: Advanced OCR and forensic document analysis
- **📊 Intelligent Dashboard**: Real-time metrics and interactive visualizations
- **🛡️ Full Compliance**: GDPR, FATF, and regional banking regulations compliance
- **🚀 Modern Architecture**: Scalable microservices with React + Django
- **🌍 International Ready**: Multi-language support (English/Portuguese) with i18n infrastructure

## 🚀 Features

### 👥 Customer Management
- ✅ Multi-step registration with real-time validation
- ✅ Personal and corporate entity data management
- ✅ Complete interaction history
- ✅ Automated risk classification
- ✅ Ultimate Beneficial Ownership (UBO) tracking

### 🔍 Sanctions Screening
- ✅ Automatic verification against global restrictive lists
- ✅ PEP (Politically Exposed Persons) detection
- ✅ Continuous monitoring and real-time alerts
- ✅ Flexible data source configuration
- ✅ Advanced fuzzy matching and transliteration

### 📄 Document Processing
- ✅ Drag & drop upload interface
- ✅ OCR with high accuracy (95%+)
- ✅ Forensic authenticity analysis
- ✅ Support for PDF, JPG, PNG (up to 10MB)
- ✅ Automated document classification

### 📊 Reports and Analytics
- ✅ Real-time dashboard with metrics
- ✅ Automated compliance report generation
- ✅ Interactive charts and visualizations
- ✅ Export to PDF, Excel, and CSV
- ✅ Regulatory reports (SAR, CTR, STR)

### 🛡️ Security and Compliance
- ✅ JWT authentication with refresh tokens
- ✅ AES-256 encryption for sensitive data
- ✅ Immutable audit trail for all operations
- ✅ GDPR/FATF compliance
- ✅ Role-based access control (RBAC)

### 🌍 International Support
- ✅ Multi-language interface (English/Portuguese)
- ✅ International document types support
- ✅ Global sanctions lists integration
- ✅ Multi-jurisdiction regulatory compliance
- ✅ Currency and date format localization

## 🛠️ Technologies

### Backend
- **Django 5.0+** - Python web framework
- **Django REST Framework** - REST APIs
- **PostgreSQL** - Primary database
- **Redis** - Cache and sessions
- **Celery** - Asynchronous processing
- **JWT** - Authentication
- **OpenAPI 3.1** - API documentation

### Frontend
- **React 18+** - User interface
- **Vite** - Build tool and dev server
- **Tailwind CSS** - CSS framework
- **React i18next** - Internationalization
- **Lucide React** - Icons
- **React Router** - Routing

### Infrastructure
- **Docker** - Containerization
- **Nginx** - Reverse proxy
- **Gunicorn** - WSGI server
- **GitHub Actions** - CI/CD

### Integrated Data Sources
- **OFAC** (Office of Foreign Assets Control)
- **UN Consolidated List** (United Nations)
- **EU Financial Sanctions** (European Union)
- **UK OFSI** (United Kingdom)
- **Central Bank BR** (Brazil)
- **OpenSanctions** (PEP and sanctions)
- **WikiData SPARQL** (Structured data)
- **OpenCorporates** (Corporate data)
- **GLEIF LEI** (Legal Entity Identifier)
- **SEC EDGAR** (Securities and Exchange Commission)
- **Companies House UK** (UK company registry)
- **Plus 10+ additional sources**

## 🚀 Installation

### Prerequisites

- Python 3.11+
- Node.js 20.0+
- PostgreSQL 14+
- Redis 6.0+
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/carlossilvatbh/CERES.git
cd CERES
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Database Configuration

```bash
# Create a PostgreSQL database
createdb ceres_db

# Configure environment variables
cp .env.example .env
# Edit the .env file with your configurations
```

### 4. Migrations and Initial Data

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json
```

### 5. Frontend Setup

```bash
cd ../frontend
npm install
```

### 6. Run the System

#### Backend (Terminal 1)
```bash
cd backend
python manage.py runserver
```

#### Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

#### Celery Worker (Terminal 3)
```bash
cd backend
celery -A ceres_project worker -l info
```

#### Redis (Terminal 4)
```bash
redis-server
```

### 7. Access the System

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs/
- **Django Admin**: http://localhost:8000/admin

**Demo credentials:**
- Username: `admin`
- Password: `admin123`

## 📖 Usage

### Customer Registration

1. Access "Customer Management" in the sidebar
2. Fill personal information (Step 1)
3. Add contact information (Step 2)
4. Upload documents (Step 3)
5. Review and confirm (Step 4)

### Sanctions Screening

1. Go to "Screening" in the menu
2. Click "New Individual Screening" or "New Entity Screening"
3. Fill the verification data
4. Wait for automatic processing
5. Analyze results and generated alerts

### Document Processing

1. Access "Documents"
2. Drag files to upload area or click "Select Files"
3. Wait for OCR processing and forensic analysis
4. View results in the document list

### Report Generation

1. Go to "Reports"
2. Configure type, period, and desired format
3. Click "Generate Report"
4. Download when ready

## 📚 API Documentation

- [📖 User Manual](docs/user-manual.md)
- [🔧 Installation Guide](docs/installation-guide.md)
- [🏗️ System Architecture](docs/architecture.md)
- [🔌 API Documentation](docs/api-documentation.md)
- [🛡️ Security Guide](docs/security-guide.md)
- [🚀 Deployment Guide](docs/deployment-guide.md)
- [🧪 Testing Guide](docs/testing-guide.md)
- [🔄 Changelog](CHANGELOG.md)

### Interactive API Documentation

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 🤝 Contributing

Contributions are very welcome! See our [Contributing Guide](CONTRIBUTING.md) for details on:

- How to report bugs
- How to suggest improvements
- Development process
- Code standards
- How to submit pull requests

### Local Development

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **Product Owner** - Overall project supervision
- **Backend Team** - Django/DRF development
- **Frontend Team** - React development
- **QA Team** - Testing and quality
- **DevOps Team** - Infrastructure and deployment
- **CTO** - Technical review and architecture

## 🆘 Support

- 📧 Email: support@ceres-system.com
- 💬 [GitHub Discussions](https://github.com/carlossilvatbh/CERES/discussions)
- 🐛 [Report Bug](https://github.com/carlossilvatbh/CERES/issues/new?template=bug_report.md)
- ✨ [Request Feature](https://github.com/carlossilvatbh/CERES/issues/new?template=feature_request.md)

## 🙏 Acknowledgments

- [OpenSanctions](https://opensanctions.org/) - Open sanctions data
- [OFAC](https://ofac.treasury.gov/) - US sanctions list
- [UN Security Council](https://www.un.org/securitycouncil/) - UN lists
- [EU Sanctions Map](https://sanctionsmap.eu/) - European Union sanctions
- Open source community for tools and libraries

---

<div align="center">
  <p>Made with ❤️ by the CERES team</p>
  <p>© 2025 CERES. Customer Enrollment and Risk Evaluation System.</p>
</div>

