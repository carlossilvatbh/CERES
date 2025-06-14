# Documentação da API - CERES

## 📖 Índice

- [Introdução](#introdução)
- [Autenticação](#autenticação)
- [Endpoints](#endpoints)
- [Modelos de Dados](#modelos-de-dados)
- [Códigos de Resposta](#códigos-de-resposta)
- [Exemplos](#exemplos)
- [SDKs](#sdks)

## 🎯 Introdução

A API REST do CERES oferece acesso programático a todas as funcionalidades do sistema de compliance.

### URL Base
```
https://api.ceres-system.com/v1/
```

### Formato de Dados
- **Request**: JSON
- **Response**: JSON
- **Encoding**: UTF-8
- **Date Format**: ISO 8601 (YYYY-MM-DDTHH:mm:ssZ)

### Versionamento
- Versão atual: `v1`
- Header: `Accept: application/vnd.ceres.v1+json`
- Backward compatibility mantida por 12 meses

## 🔐 Autenticação

### JWT (JSON Web Tokens)

#### Obter Token
```http
POST /auth/login/
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Resposta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "expires_in": 3600
}
```

#### Usar Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Renovar Token
```http
POST /auth/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## 🔌 Endpoints

### Customer Enrollment

#### Listar Clientes
```http
GET /customers/
```

**Parâmetros de Query:**
- `page`: Número da página (padrão: 1)
- `page_size`: Itens por página (padrão: 20, máx: 100)
- `search`: Busca por nome ou documento
- `risk_level`: Filtro por nível de risco (low, medium, high)
- `created_after`: Data de criação (YYYY-MM-DD)

**Resposta:**
```json
{
  "count": 1247,
  "next": "https://api.ceres-system.com/v1/customers/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "full_name": "João Silva",
      "document_number": "123.456.789-00",
      "email": "joao@email.com",
      "risk_level": "low",
      "created_at": "2025-06-14T10:30:00Z",
      "updated_at": "2025-06-14T10:30:00Z"
    }
  ]
}
```

#### Criar Cliente
```http
POST /customers/
Content-Type: application/json

{
  "full_name": "Maria Santos",
  "document_number": "987.654.321-00",
  "birth_date": "1990-05-15",
  "nationality": "BR",
  "email": "maria@email.com",
  "phone": "+5511999999999",
  "address": {
    "street": "Rua das Flores, 123",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01234-567",
    "country": "BR"
  }
}
```

#### Obter Cliente
```http
GET /customers/{id}/
```

#### Atualizar Cliente
```http
PUT /customers/{id}/
PATCH /customers/{id}/
```

#### Excluir Cliente
```http
DELETE /customers/{id}/
```

### Document Processing

#### Listar Documentos
```http
GET /documents/
```

**Parâmetros:**
- `customer_id`: Filtrar por cliente
- `status`: pending, processing, processed, error
- `document_type`: rg, cpf, proof_address, proof_income

#### Upload de Documento
```http
POST /documents/
Content-Type: multipart/form-data

file: [arquivo]
customer_id: uuid-here
document_type: rg
```

**Resposta:**
```json
{
  "id": "doc-uuid",
  "customer_id": "customer-uuid",
  "document_type": "rg",
  "file_name": "rg_joao.pdf",
  "file_size": 2048576,
  "status": "pending",
  "uploaded_at": "2025-06-14T10:30:00Z"
}
```

#### Status do Processamento
```http
GET /documents/{id}/processing-status/
```

**Resposta:**
```json
{
  "status": "processed",
  "progress": 100,
  "extracted_data": {
    "name": "João Silva",
    "document_number": "123456789",
    "birth_date": "1985-03-20",
    "confidence": 0.95
  },
  "forensic_analysis": {
    "authenticity_score": 0.92,
    "tampering_detected": false,
    "quality_score": 0.88
  }
}
```

### Sanctions Screening

#### Iniciar Screening
```http
POST /screening/
Content-Type: application/json

{
  "customer_id": "uuid-here",
  "screening_type": "individual",
  "sources": ["ofac", "un", "eu"],
  "threshold": 0.8
}
```

#### Listar Screenings
```http
GET /screening/
```

**Parâmetros:**
- `customer_id`: Filtrar por cliente
- `status`: pending, running, completed, failed
- `risk_level`: low, medium, high
- `created_after`: Data de criação

#### Resultado do Screening
```http
GET /screening/{id}/results/
```

**Resposta:**
```json
{
  "id": "screening-uuid",
  "customer_id": "customer-uuid",
  "status": "completed",
  "risk_level": "medium",
  "total_matches": 2,
  "sources_checked": ["ofac", "un", "eu"],
  "matches": [
    {
      "source": "ofac",
      "list_name": "SDN List",
      "matched_name": "João Silva Santos",
      "similarity_score": 0.85,
      "additional_info": {
        "birth_date": "1985-03-20",
        "nationality": "BR",
        "aliases": ["J. Silva", "João Santos"]
      }
    }
  ],
  "completed_at": "2025-06-14T10:35:00Z"
}
```

### Reports

#### Gerar Relatório
```http
POST /reports/generate/
Content-Type: application/json

{
  "report_type": "compliance",
  "period": {
    "start_date": "2025-05-01",
    "end_date": "2025-05-31"
  },
  "format": "pdf",
  "filters": {
    "risk_levels": ["medium", "high"],
    "sources": ["ofac", "un"]
  }
}
```

#### Status do Relatório
```http
GET /reports/{id}/status/
```

#### Download do Relatório
```http
GET /reports/{id}/download/
```

### Data Sources

#### Listar Fontes
```http
GET /data-sources/
```

**Resposta:**
```json
{
  "sources": [
    {
      "id": "ofac",
      "name": "OFAC SDN List",
      "type": "sanctions",
      "status": "active",
      "last_updated": "2025-06-14T06:00:00Z",
      "record_count": 12547,
      "update_frequency": "daily"
    }
  ]
}
```

#### Atualizar Fonte
```http
POST /data-sources/{id}/update/
```

## 📊 Modelos de Dados

### Customer
```json
{
  "id": "string (uuid)",
  "full_name": "string (required)",
  "document_number": "string (required, unique)",
  "birth_date": "date",
  "nationality": "string (ISO 3166-1 alpha-2)",
  "email": "string (email format)",
  "phone": "string",
  "risk_level": "enum (low, medium, high)",
  "status": "enum (active, inactive, blocked)",
  "address": {
    "street": "string",
    "city": "string",
    "state": "string",
    "zip_code": "string",
    "country": "string (ISO 3166-1 alpha-2)"
  },
  "created_at": "datetime (ISO 8601)",
  "updated_at": "datetime (ISO 8601)"
}
```

### Document
```json
{
  "id": "string (uuid)",
  "customer_id": "string (uuid, foreign key)",
  "document_type": "enum (rg, cpf, proof_address, proof_income)",
  "file_name": "string",
  "file_size": "integer (bytes)",
  "file_url": "string (url)",
  "status": "enum (pending, processing, processed, error)",
  "extracted_data": "object",
  "forensic_analysis": "object",
  "uploaded_at": "datetime (ISO 8601)",
  "processed_at": "datetime (ISO 8601)"
}
```

### Screening
```json
{
  "id": "string (uuid)",
  "customer_id": "string (uuid, foreign key)",
  "screening_type": "enum (individual, corporate)",
  "status": "enum (pending, running, completed, failed)",
  "risk_level": "enum (low, medium, high)",
  "sources_checked": "array of strings",
  "total_matches": "integer",
  "matches": "array of objects",
  "created_at": "datetime (ISO 8601)",
  "completed_at": "datetime (ISO 8601)"
}
```

## 📋 Códigos de Resposta

### Sucesso (2xx)
- `200 OK`: Requisição bem-sucedida
- `201 Created`: Recurso criado com sucesso
- `202 Accepted`: Requisição aceita para processamento
- `204 No Content`: Sucesso sem conteúdo de resposta

### Erro do Cliente (4xx)
- `400 Bad Request`: Dados inválidos
- `401 Unauthorized`: Não autenticado
- `403 Forbidden`: Acesso negado
- `404 Not Found`: Recurso não encontrado
- `422 Unprocessable Entity`: Erro de validação
- `429 Too Many Requests`: Rate limit excedido

### Erro do Servidor (5xx)
- `500 Internal Server Error`: Erro interno
- `502 Bad Gateway`: Erro de gateway
- `503 Service Unavailable`: Serviço indisponível

### Formato de Erro
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Dados de entrada inválidos",
    "details": {
      "field": "document_number",
      "message": "CPF inválido"
    },
    "timestamp": "2025-06-14T10:30:00Z",
    "request_id": "req-uuid-here"
  }
}
```

## 💡 Exemplos

### Fluxo Completo: Cadastro e Screening

#### 1. Criar Cliente
```bash
curl -X POST https://api.ceres-system.com/v1/customers/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Ana Costa",
    "document_number": "111.222.333-44",
    "birth_date": "1988-12-10",
    "email": "ana@email.com"
  }'
```

#### 2. Upload de Documento
```bash
curl -X POST https://api.ceres-system.com/v1/documents/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@rg_ana.pdf" \
  -F "customer_id=customer-uuid" \
  -F "document_type=rg"
```

#### 3. Iniciar Screening
```bash
curl -X POST https://api.ceres-system.com/v1/screening/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "customer-uuid",
    "screening_type": "individual"
  }'
```

#### 4. Verificar Resultado
```bash
curl -X GET https://api.ceres-system.com/v1/screening/screening-uuid/results/ \
  -H "Authorization: Bearer $TOKEN"
```

### Rate Limiting

#### Headers de Rate Limit
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

#### Limites por Endpoint
- **Autenticação**: 5 req/min
- **Upload**: 10 req/min
- **Screening**: 100 req/hour
- **Consultas**: 1000 req/hour

## 🛠️ SDKs

### Python
```bash
pip install ceres-python-sdk
```

```python
from ceres import CeresClient

client = CeresClient(
    base_url="https://api.ceres-system.com/v1/",
    token="your-jwt-token"
)

# Criar cliente
customer = client.customers.create({
    "full_name": "João Silva",
    "document_number": "123.456.789-00",
    "email": "joao@email.com"
})

# Iniciar screening
screening = client.screening.create({
    "customer_id": customer.id,
    "screening_type": "individual"
})
```

### JavaScript/Node.js
```bash
npm install @ceres/sdk
```

```javascript
const { CeresClient } = require('@ceres/sdk');

const client = new CeresClient({
  baseURL: 'https://api.ceres-system.com/v1/',
  token: 'your-jwt-token'
});

// Criar cliente
const customer = await client.customers.create({
  full_name: 'João Silva',
  document_number: '123.456.789-00',
  email: 'joao@email.com'
});

// Upload de documento
const document = await client.documents.upload({
  file: fs.createReadStream('rg.pdf'),
  customer_id: customer.id,
  document_type: 'rg'
});
```

### PHP
```bash
composer require ceres/php-sdk
```

```php
<?php
use Ceres\CeresClient;

$client = new CeresClient([
    'base_url' => 'https://api.ceres-system.com/v1/',
    'token' => 'your-jwt-token'
]);

// Criar cliente
$customer = $client->customers()->create([
    'full_name' => 'João Silva',
    'document_number' => '123.456.789-00',
    'email' => 'joao@email.com'
]);

// Iniciar screening
$screening = $client->screening()->create([
    'customer_id' => $customer['id'],
    'screening_type' => 'individual'
]);
?>
```

## 🔧 Webhooks

### Configuração
```http
POST /webhooks/
Content-Type: application/json

{
  "url": "https://your-app.com/webhooks/ceres",
  "events": ["screening.completed", "document.processed"],
  "secret": "your-webhook-secret"
}
```

### Eventos Disponíveis
- `customer.created`
- `customer.updated`
- `document.uploaded`
- `document.processed`
- `screening.started`
- `screening.completed`
- `alert.created`

### Payload do Webhook
```json
{
  "event": "screening.completed",
  "data": {
    "id": "screening-uuid",
    "customer_id": "customer-uuid",
    "risk_level": "medium",
    "matches_found": 2
  },
  "timestamp": "2025-06-14T10:30:00Z",
  "signature": "sha256=..."
}
```

---

**© 2025 CERES. Sistema de Compliance e Avaliação de Risco.**

