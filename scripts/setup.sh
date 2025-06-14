#!/bin/bash

# CERES Setup Script
# Este script automatiza a instalação e configuração do sistema CERES

set -e

echo "🚀 Iniciando instalação do CERES..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root"
fi

# Verificar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    error "Sistema operacional não suportado: $OSTYPE"
fi

log "Sistema detectado: $OS"

# Verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    # Python
    if ! command -v python3 &> /dev/null; then
        error "Python 3.11+ é necessário. Instale antes de continuar."
    fi
    
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    if [[ $(echo "$PYTHON_VERSION < 3.11" | bc -l) -eq 1 ]]; then
        error "Python 3.11+ é necessário. Versão atual: $PYTHON_VERSION"
    fi
    
    # Node.js
    if ! command -v node &> /dev/null; then
        error "Node.js 20+ é necessário. Instale antes de continuar."
    fi
    
    NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $NODE_VERSION -lt 20 ]]; then
        error "Node.js 20+ é necessário. Versão atual: $NODE_VERSION"
    fi
    
    # Git
    if ! command -v git &> /dev/null; then
        error "Git é necessário. Instale antes de continuar."
    fi
    
    log "✅ Todas as dependências estão instaladas"
}

# Instalar dependências do sistema
install_system_deps() {
    log "Instalando dependências do sistema..."
    
    if [[ "$OS" == "linux" ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get update
            sudo apt-get install -y \
                postgresql-client \
                redis-tools \
                tesseract-ocr \
                tesseract-ocr-por \
                poppler-utils \
                libpq-dev \
                python3-dev \
                build-essential
        elif command -v yum &> /dev/null; then
            sudo yum install -y \
                postgresql \
                redis \
                tesseract \
                poppler-utils \
                postgresql-devel \
                python3-devel \
                gcc
        fi
    elif [[ "$OS" == "macos" ]]; then
        if command -v brew &> /dev/null; then
            brew install postgresql redis tesseract poppler
        else
            warn "Homebrew não encontrado. Instale manualmente: postgresql, redis, tesseract, poppler"
        fi
    fi
}

# Configurar backend
setup_backend() {
    log "Configurando backend..."
    
    cd backend
    
    # Criar ambiente virtual
    if [[ ! -d "venv" ]]; then
        log "Criando ambiente virtual Python..."
        python3 -m venv venv
    fi
    
    # Ativar ambiente virtual
    source venv/bin/activate
    
    # Instalar dependências
    log "Instalando dependências Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Configurar variáveis de ambiente
    if [[ ! -f ".env" ]]; then
        log "Criando arquivo .env..."
        cp .env.example .env
        
        # Gerar SECRET_KEY
        SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        
        warn "Configure o arquivo backend/.env com suas configurações de banco de dados"
    fi
    
    cd ..
}

# Configurar frontend
setup_frontend() {
    log "Configurando frontend..."
    
    cd frontend
    
    # Instalar dependências
    log "Instalando dependências Node.js..."
    npm install
    
    # Configurar variáveis de ambiente
    if [[ ! -f ".env.local" ]]; then
        log "Criando arquivo .env.local..."
        echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
    fi
    
    cd ..
}

# Configurar banco de dados
setup_database() {
    log "Configurando banco de dados..."
    
    # Verificar se PostgreSQL está rodando
    if ! pg_isready -h localhost -p 5432 &> /dev/null; then
        warn "PostgreSQL não está rodando. Inicie o serviço antes de continuar."
        return
    fi
    
    cd backend
    source venv/bin/activate
    
    # Executar migrações
    log "Executando migrações..."
    python manage.py migrate
    
    # Coletar arquivos estáticos
    log "Coletando arquivos estáticos..."
    python manage.py collectstatic --noinput
    
    # Criar superusuário se não existir
    if ! python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(User.objects.filter(is_superuser=True).exists())" | grep -q "True"; then
        log "Criando superusuário..."
        echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@ceres.com', 'admin123')" | python manage.py shell
        log "✅ Superusuário criado: admin / admin123"
    fi
    
    cd ..
}

# Configurar Docker (opcional)
setup_docker() {
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        log "Docker detectado. Configurando containers..."
        
        # Build das imagens
        docker-compose build
        
        log "✅ Containers Docker configurados"
        log "Execute 'docker-compose up' para iniciar com Docker"
    else
        warn "Docker não encontrado. Instalação manual será necessária."
    fi
}

# Executar testes
run_tests() {
    log "Executando testes..."
    
    # Testes do backend
    cd backend
    source venv/bin/activate
    python manage.py test --verbosity=2
    cd ..
    
    # Testes do frontend
    cd frontend
    npm test -- --watchAll=false
    cd ..
    
    log "✅ Todos os testes passaram"
}

# Função principal
main() {
    echo -e "${BLUE}"
    echo "  ██████ ███████ ██████  ███████ ███████ "
    echo " ██      ██      ██   ██ ██      ██      "
    echo " ██      █████   ██████  █████   ███████ "
    echo " ██      ██      ██   ██ ██           ██ "
    echo "  ██████ ███████ ██   ██ ███████ ███████ "
    echo ""
    echo " Customer Enrollment and Risk Evaluation System"
    echo -e "${NC}"
    
    # Menu de opções
    echo "Escolha uma opção:"
    echo "1) Instalação completa"
    echo "2) Apenas verificar dependências"
    echo "3) Configurar backend"
    echo "4) Configurar frontend"
    echo "5) Configurar banco de dados"
    echo "6) Executar testes"
    echo "7) Configurar Docker"
    echo "0) Sair"
    
    read -p "Opção: " choice
    
    case $choice in
        1)
            check_dependencies
            install_system_deps
            setup_backend
            setup_frontend
            setup_database
            setup_docker
            run_tests
            
            log "🎉 Instalação concluída com sucesso!"
            echo ""
            echo "Para iniciar o sistema:"
            echo "1. Backend: cd backend && source venv/bin/activate && python manage.py runserver"
            echo "2. Frontend: cd frontend && npm run dev"
            echo "3. Ou use Docker: docker-compose up"
            echo ""
            echo "Acesse: http://localhost:5173"
            echo "Login: admin / admin123"
            ;;
        2) check_dependencies ;;
        3) setup_backend ;;
        4) setup_frontend ;;
        5) setup_database ;;
        6) run_tests ;;
        7) setup_docker ;;
        0) exit 0 ;;
        *) error "Opção inválida" ;;
    esac
}

# Executar função principal
main "$@"

