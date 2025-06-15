# Contributing to CERES

Thank you for your interest in contributing to CERES! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

Before contributing, ensure you have:
- Node.js 18+ and pnpm 8+
- Python 3.11+ and pip
- PostgreSQL 13+
- Redis 6+
- Git

### Development Setup

1. **Fork and Clone**
```bash
git clone https://github.com/YOUR_USERNAME/CERES.git
cd CERES
```

2. **Setup Backend**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py createsuperuser
```

3. **Setup Frontend**
```bash
cd frontend
pnpm install
```

4. **Start Development Servers**
```bash
# Terminal 1: Backend
cd backend && python manage.py runserver

# Terminal 2: Frontend  
cd frontend && pnpm dev

# Terminal 3: Celery (optional)
cd backend && celery -A ceres_project worker -l info
```

## 📋 Development Guidelines

### Code Style

**Python (Backend)**
- Follow PEP 8
- Use Black for formatting: `black .`
- Use isort for imports: `isort .`
- Use flake8 for linting: `flake8 .`
- Type hints are encouraged

**TypeScript (Frontend)**
- Follow ESLint configuration
- Use Prettier for formatting: `pnpm format`
- Use TypeScript strict mode
- Prefer functional components with hooks

### Commit Messages

Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(auth): add JWT token refresh mechanism
fix(screening): resolve timeout issue in batch processing
docs(api): update authentication endpoints documentation
```

### Branch Naming

- `feature/description` - New features
- `fix/description` - Bug fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test improvements

## 🧪 Testing

### Running Tests

**Backend Tests**
```bash
cd backend
pytest                    # Run all tests
pytest -m unit           # Unit tests only
pytest -m integration    # Integration tests only
pytest --cov=.           # With coverage
```

**Frontend Tests**
```bash
cd frontend
pnpm test                # Run all tests
pnpm test:coverage       # With coverage
pnpm test:ui             # Interactive UI
```

### Writing Tests

**Backend Test Structure**
```python
# tests/unit/test_models.py
import pytest
from sanctions_screening.models import Customer

@pytest.mark.unit
def test_customer_creation():
    customer = Customer.objects.create(
        name="Test Customer",
        email="test@example.com"
    )
    assert customer.name == "Test Customer"
```

**Frontend Test Structure**
```typescript
// src/components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '../Button'

describe('Button', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
```

## 📝 Documentation

### API Documentation

- Update OpenAPI schemas for new endpoints
- Include request/response examples
- Document error responses
- Add authentication requirements

### Code Documentation

**Python Docstrings**
```python
def screen_customer(customer_id: int, sources: List[str]) -> Dict[str, Any]:
    """
    Screen a customer against sanctions lists.
    
    Args:
        customer_id: ID of the customer to screen
        sources: List of screening sources to check
        
    Returns:
        Dict containing screening results and metadata
        
    Raises:
        CustomerNotFound: If customer doesn't exist
        ScreeningError: If screening process fails
    """
```

**TypeScript JSDoc**
```typescript
/**
 * Validates customer data before submission
 * @param data - Customer data to validate
 * @returns Validation result with errors if any
 */
export function validateCustomerData(data: CustomerData): ValidationResult {
  // Implementation
}
```

## 🔄 Pull Request Process

### Before Submitting

1. **Update your branch**
```bash
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main
```

2. **Run tests**
```bash
# Backend
cd backend && pytest

# Frontend
cd frontend && pnpm test
```

3. **Check code quality**
```bash
# Backend
cd backend && black . && isort . && flake8 .

# Frontend
cd frontend && pnpm lint && pnpm type-check
```

### PR Requirements

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] Commit messages follow convention
- [ ] PR description explains changes
- [ ] Breaking changes documented

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
```

## 🐛 Bug Reports

### Before Reporting

1. Check existing issues
2. Reproduce the bug
3. Test on latest version
4. Gather system information

### Bug Report Template

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Browser: [e.g., Chrome 91]
- CERES Version: [e.g., 2.0.0]

**Additional Context**
Screenshots, logs, etc.
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Feature Description**
Clear description of the feature

**Problem Statement**
What problem does this solve?

**Proposed Solution**
How should this work?

**Alternatives Considered**
Other solutions you've considered

**Additional Context**
Mockups, examples, etc.
```

## 🏗️ Architecture Guidelines

### Backend Architecture

- Follow Django best practices
- Use Django REST Framework for APIs
- Implement proper error handling
- Use Celery for background tasks
- Follow repository pattern for data access

### Frontend Architecture

- Use React functional components
- Implement proper error boundaries
- Use React Query for server state
- Follow atomic design principles
- Implement proper loading states

### Database Guidelines

- Use migrations for schema changes
- Index frequently queried fields
- Use foreign keys for relationships
- Implement soft deletes where appropriate
- Document complex queries

## 🔒 Security Guidelines

### Security Checklist

- [ ] Input validation implemented
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF protection
- [ ] Authentication required
- [ ] Authorization checked
- [ ] Sensitive data encrypted
- [ ] Audit logging implemented

### Security Review Process

1. Code review by security-aware developer
2. Automated security scanning
3. Manual security testing
4. Documentation review

## 📊 Performance Guidelines

### Performance Checklist

- [ ] Database queries optimized
- [ ] Proper indexing implemented
- [ ] Caching strategy applied
- [ ] Bundle size optimized
- [ ] Images optimized
- [ ] API responses paginated
- [ ] Background tasks used for heavy operations

### Performance Testing

- Load testing for APIs
- Frontend performance audits
- Database query analysis
- Memory usage monitoring

## 🤝 Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow
- Follow project guidelines
- Report inappropriate behavior

### Communication Channels

- **Issues**: Bug reports and feature requests
- **Discussions**: Questions and general discussion
- **Pull Requests**: Code contributions
- **Email**: security@ceres-system.com (security issues)

## 📚 Resources

### Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Tools and Extensions

**VS Code Extensions**
- Python
- Pylance
- ES7+ React/Redux/React-Native snippets
- Prettier
- ESLint
- GitLens

**Browser Extensions**
- React Developer Tools
- Redux DevTools

## 🎯 Roadmap Participation

### How to Contribute to Roadmap

1. Review current roadmap in README
2. Discuss ideas in GitHub Discussions
3. Create detailed feature proposals
4. Participate in planning discussions
5. Volunteer for implementation

### Priority Areas

- Performance optimization
- Security enhancements
- User experience improvements
- API enhancements
- Documentation improvements

---

Thank you for contributing to CERES! Your contributions help make compliance and risk management more accessible and effective for organizations worldwide.
