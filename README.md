# CERES - Customer Enrollment and Risk Evaluation System

<div align="center">
  <img src="docs/assets/ceres-logo.png" alt="CERES Logo" width="200"/>
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![React](https://img.shields.io/badge/React-18.0+-blue.svg)](https://reactjs.org/)
  [![Django](https://img.shields.io/badge/Django-5.0+-green.svg)](https://djangoproject.com/)
  [![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org/)
  [![Node.js](https://img.shields.io/badge/Node.js-20.0+-green.svg)](https://nodejs.org/)
  
  **Sistema de Compliance e Avaliação de Risco para Instituições Financeiras**
  
  [🚀 Demo Live](https://jgngsogp.manus.space) | [📖 Documentação](docs/) | [🐛 Issues](https://github.com/seu-usuario/ceres/issues) | [💬 Discussões](https://github.com/seu-usuario/ceres/discussions)
</div>

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Tecnologias](#tecnologias)
- [Instalação](#instalação)
- [Uso](#uso)
- [Documentação](#documentação)
- [Contribuição](#contribuição)
- [Licença](#licença)
- [Contato](#contato)

## 🎯 Sobre o Projeto

O CERES é um sistema completo de compliance e avaliação de risco desenvolvido especificamente para instituições financeiras. Oferece funcionalidades avançadas de KYC (Know Your Customer), screening de sanções, processamento de documentos e geração de relatórios de compliance.

### ✨ Principais Características

- **🔍 Screening Automatizado**: Verificação contra 20+ fontes de dados abertas (OFAC, UN, EU, etc.)
- **📄 Processamento de Documentos**: OCR avançado e análise forense de autenticidade
- **📊 Dashboard Inteligente**: Métricas em tempo real e visualizações interativas
- **🛡️ Compliance Total**: Conformidade com GDPR, LGPD e regulamentações FATF
- **🚀 Arquitetura Moderna**: Microserviços escaláveis com React + Django

## 🚀 Funcionalidades

### 👥 Gestão de Clientes
- ✅ Cadastro multi-step com validação em tempo real
- ✅ Gestão de dados pessoais e documentos
- ✅ Histórico completo de interações
- ✅ Classificação automática de risco

### 🔍 Screening de Sanções
- ✅ Verificação automática contra listas restritivas globais
- ✅ Detecção de PEP (Pessoas Politicamente Expostas)
- ✅ Monitoramento contínuo e alertas em tempo real
- ✅ Configuração flexível de fontes de dados

### 📄 Processamento de Documentos
- ✅ Upload com drag & drop
- ✅ OCR com Tesseract para extração de texto
- ✅ Análise forense de autenticidade
- ✅ Suporte para PDF, JPG, PNG (até 10MB)

### 📊 Relatórios e Analytics
- ✅ Dashboard com métricas em tempo real
- ✅ Geração automática de relatórios de compliance
- ✅ Gráficos interativos e visualizações
- ✅ Exportação em PDF, Excel e CSV

### 🛡️ Segurança e Compliance
- ✅ Autenticação JWT com refresh tokens
- ✅ Criptografia AES-256 para dados sensíveis
- ✅ Auditoria imutável de todas as operações
- ✅ Conformidade GDPR/LGPD

## 🛠️ Tecnologias

### Backend
- **Django 5.0+** - Framework web Python
- **Django REST Framework** - APIs REST
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e sessões
- **Celery** - Processamento assíncrono
- **JWT** - Autenticação

### Frontend
- **React 18+** - Interface do usuário
- **Vite** - Build tool e dev server
- **Tailwind CSS** - Framework CSS
- **Lucide React** - Ícones
- **React Router** - Roteamento

### Infraestrutura
- **Docker** - Containerização
- **Nginx** - Proxy reverso
- **Gunicorn** - Servidor WSGI
- **GitHub Actions** - CI/CD

### Fontes de Dados Integradas
- **OFAC** (Office of Foreign Assets Control)
- **UN Consolidated List** (Nações Unidas)
- **EU Financial Sanctions** (União Europeia)
- **UK OFSI** (Reino Unido)
- **Banco Central BR** (Brasil)
- **OpenSanctions** (PEP e sanções)
- **WikiData SPARQL** (Dados estruturados)
- **OpenCorporates** (Dados corporativos)
- **GLEIF LEI** (Legal Entity Identifier)
- **SEC EDGAR** (Securities and Exchange Commission)
- **Companies House UK** (Registro de empresas UK)
- **E mais 10+ fontes adicionais**

## 🚀 Instalação

### Pré-requisitos

- Python 3.11+
- Node.js 20.0+
- PostgreSQL 14+
- Redis 6.0+
- Git

### 1. Clone o Repositório

```bash
git clone https://github.com/seu-usuario/ceres.git
cd ceres
```

### 2. Configuração do Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows

pip install -r requirements.txt
```

### 3. Configuração do Banco de Dados

```bash
# Crie um banco PostgreSQL
createdb ceres_db

# Configure as variáveis de ambiente
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

### 4. Migrações e Dados Iniciais

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py loaddata fixtures/initial_data.json
```

### 5. Configuração do Frontend

```bash
cd ../frontend
npm install
```

### 6. Executar o Sistema

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

### 7. Acesso ao Sistema

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Admin Django**: http://localhost:8000/admin

**Credenciais de demonstração:**
- Usuário: `admin`
- Senha: `admin123`

## 📖 Uso

### Cadastro de Cliente

1. Acesse "Cadastro de Clientes" no menu lateral
2. Preencha os dados pessoais (Etapa 1)
3. Adicione informações de contato (Etapa 2)
4. Faça upload dos documentos (Etapa 3)
5. Revise e confirme (Etapa 4)

### Screening de Sanções

1. Vá para "Screening" no menu
2. Clique em "Novo Screening Individual" ou "Novo Screening Empresa"
3. Preencha os dados para verificação
4. Aguarde o processamento automático
5. Analise os resultados e alertas gerados

### Processamento de Documentos

1. Acesse "Documentos"
2. Arraste arquivos para a área de upload ou clique em "Selecionar Arquivos"
3. Aguarde o processamento OCR e análise forense
4. Visualize os resultados na lista de documentos

### Geração de Relatórios

1. Vá para "Relatórios"
2. Configure o tipo, período e formato desejado
3. Clique em "Gerar Relatório"
4. Faça download quando estiver pronto

## 📚 Documentação

- [📖 Manual do Usuário](docs/user-manual.md)
- [🔧 Guia de Instalação](docs/installation-guide.md)
- [🏗️ Arquitetura do Sistema](docs/architecture.md)
- [🔌 Documentação da API](docs/api-documentation.md)
- [🛡️ Guia de Segurança](docs/security-guide.md)
- [🚀 Guia de Deploy](docs/deployment-guide.md)
- [🧪 Guia de Testes](docs/testing-guide.md)
- [🔄 Changelog](CHANGELOG.md)

## 🤝 Contribuição

Contribuições são muito bem-vindas! Veja nosso [Guia de Contribuição](CONTRIBUTING.md) para detalhes sobre:

- Como reportar bugs
- Como sugerir melhorias
- Processo de desenvolvimento
- Padrões de código
- Como submeter pull requests

### Desenvolvimento Local

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Equipe

- **Product Owner** - Supervisão geral do projeto
- **Backend Team** - Desenvolvimento Django/DRF
- **Frontend Team** - Desenvolvimento React
- **QA Team** - Testes e qualidade
- **DevOps Team** - Infraestrutura e deploy
- **CTO** - Revisão técnica e arquitetura

## 🆘 Suporte

- 📧 Email: suporte@ceres-system.com
- 💬 [Discussões no GitHub](https://github.com/seu-usuario/ceres/discussions)
- 🐛 [Reportar Bug](https://github.com/seu-usuario/ceres/issues/new?template=bug_report.md)
- ✨ [Solicitar Feature](https://github.com/seu-usuario/ceres/issues/new?template=feature_request.md)

## 🙏 Agradecimentos

- [OpenSanctions](https://opensanctions.org/) - Dados de sanções abertas
- [OFAC](https://ofac.treasury.gov/) - Lista de sanções dos EUA
- [UN Security Council](https://www.un.org/securitycouncil/) - Listas da ONU
- [EU Sanctions Map](https://sanctionsmap.eu/) - Sanções da União Europeia
- Comunidade open source por ferramentas e bibliotecas

---

<div align="center">
  <p>Feito com ❤️ pela equipe CERES</p>
  <p>© 2025 CERES. Sistema de Compliance e Avaliação de Risco.</p>
</div>

