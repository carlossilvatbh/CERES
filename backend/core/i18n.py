"""
Internationalization utilities for CERES
Provides translation helpers and language management
"""
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy
from django.conf import settings
from typing import Dict, Any

# Common translations used throughout the application
COMMON_TRANSLATIONS = {
    # General terms
    'name': _('Nome'),
    'email': _('E-mail'),
    'phone': _('Telefone'),
    'address': _('Endereço'),
    'date': _('Data'),
    'status': _('Status'),
    'actions': _('Ações'),
    'save': _('Salvar'),
    'cancel': _('Cancelar'),
    'delete': _('Excluir'),
    'edit': _('Editar'),
    'view': _('Visualizar'),
    'search': _('Pesquisar'),
    'filter': _('Filtrar'),
    'export': _('Exportar'),
    'import': _('Importar'),
    'download': _('Baixar'),
    'upload': _('Enviar'),
    'submit': _('Enviar'),
    'confirm': _('Confirmar'),
    'yes': _('Sim'),
    'no': _('Não'),
    'loading': _('Carregando...'),
    'error': _('Erro'),
    'success': _('Sucesso'),
    'warning': _('Aviso'),
    'info': _('Informação'),
    
    # Customer management
    'customer': _('Cliente'),
    'customers': _('Clientes'),
    'customer_name': _('Nome do Cliente'),
    'customer_id': _('ID do Cliente'),
    'customer_type': _('Tipo de Cliente'),
    'individual': _('Pessoa Física'),
    'entity': _('Pessoa Jurídica'),
    'document_number': _('Número do Documento'),
    'birth_date': _('Data de Nascimento'),
    'nationality': _('Nacionalidade'),
    'risk_level': _('Nível de Risco'),
    'low_risk': _('Baixo Risco'),
    'medium_risk': _('Médio Risco'),
    'high_risk': _('Alto Risco'),
    'critical_risk': _('Risco Crítico'),
    
    # Document processing
    'document': _('Documento'),
    'documents': _('Documentos'),
    'document_type': _('Tipo de Documento'),
    'passport': _('Passaporte'),
    'id_card': _('Carteira de Identidade'),
    'driver_license': _('Carteira de Motorista'),
    'upload_document': _('Enviar Documento'),
    'process_document': _('Processar Documento'),
    'ocr_result': _('Resultado OCR'),
    'extracted_text': _('Texto Extraído'),
    'confidence': _('Confiança'),
    'processing_time': _('Tempo de Processamento'),
    
    # Sanctions screening
    'screening': _('Screening'),
    'sanctions_screening': _('Screening de Sanções'),
    'pep_screening': _('Screening PEP'),
    'screening_result': _('Resultado do Screening'),
    'match_found': _('Correspondência Encontrada'),
    'no_match': _('Nenhuma Correspondência'),
    'high_confidence_match': _('Correspondência de Alta Confiança'),
    'potential_match': _('Correspondência Potencial'),
    'false_positive': _('Falso Positivo'),
    'screening_sources': _('Fontes de Screening'),
    'ofac': _('OFAC'),
    'un_sanctions': _('Sanções ONU'),
    'eu_sanctions': _('Sanções UE'),
    'pep_database': _('Base PEP'),
    'match_score': _('Pontuação da Correspondência'),
    'matched_name': _('Nome Correspondente'),
    'list_type': _('Tipo de Lista'),
    
    # Alerts
    'alert': _('Alerta'),
    'alerts': _('Alertas'),
    'alert_type': _('Tipo de Alerta'),
    'severity': _('Severidade'),
    'low_severity': _('Baixa'),
    'medium_severity': _('Média'),
    'high_severity': _('Alta'),
    'critical_severity': _('Crítica'),
    'acknowledged': _('Reconhecido'),
    'resolved': _('Resolvido'),
    'acknowledge_alert': _('Reconhecer Alerta'),
    'resolve_alert': _('Resolver Alerta'),
    'alert_message': _('Mensagem do Alerta'),
    'alert_timestamp': _('Data/Hora do Alerta'),
    
    # System messages
    'system_error': _('Erro do Sistema'),
    'validation_error': _('Erro de Validação'),
    'permission_denied': _('Permissão Negada'),
    'not_found': _('Não Encontrado'),
    'invalid_request': _('Solicitação Inválida'),
    'operation_successful': _('Operação Realizada com Sucesso'),
    'operation_failed': _('Operação Falhou'),
    'data_saved': _('Dados Salvos'),
    'data_deleted': _('Dados Excluídos'),
    'file_uploaded': _('Arquivo Enviado'),
    'file_processed': _('Arquivo Processado'),
    'invalid_file_format': _('Formato de Arquivo Inválido'),
    'file_too_large': _('Arquivo Muito Grande'),
    'processing_in_progress': _('Processamento em Andamento'),
    'processing_completed': _('Processamento Concluído'),
    'processing_failed': _('Processamento Falhou'),
    
    # Navigation and UI
    'dashboard': _('Painel'),
    'home': _('Início'),
    'profile': _('Perfil'),
    'settings': _('Configurações'),
    'logout': _('Sair'),
    'login': _('Entrar'),
    'register': _('Registrar'),
    'forgot_password': _('Esqueci a Senha'),
    'change_password': _('Alterar Senha'),
    'menu': _('Menu'),
    'navigation': _('Navegação'),
    'back': _('Voltar'),
    'next': _('Próximo'),
    'previous': _('Anterior'),
    'first': _('Primeiro'),
    'last': _('Último'),
    'page': _('Página'),
    'of': _('de'),
    'total': _('Total'),
    'showing': _('Mostrando'),
    'results': _('Resultados'),
    'no_results': _('Nenhum Resultado'),
    
    # Date and time
    'today': _('Hoje'),
    'yesterday': _('Ontem'),
    'tomorrow': _('Amanhã'),
    'this_week': _('Esta Semana'),
    'last_week': _('Semana Passada'),
    'this_month': _('Este Mês'),
    'last_month': _('Mês Passado'),
    'this_year': _('Este Ano'),
    'last_year': _('Ano Passado'),
    'created_at': _('Criado em'),
    'updated_at': _('Atualizado em'),
    'last_login': _('Último Login'),
    'expires_at': _('Expira em'),
}

# Alert type translations
ALERT_TYPE_TRANSLATIONS = {
    'high_risk_match': _('Correspondência de Alto Risco'),
    'document_processing_error': _('Erro no Processamento de Documento'),
    'system_error': _('Erro do Sistema'),
    'compliance_violation': _('Violação de Compliance'),
    'suspicious_activity': _('Atividade Suspeita'),
    'data_quality_issue': _('Problema de Qualidade de Dados'),
    'performance_issue': _('Problema de Performance'),
}

# Status translations
STATUS_TRANSLATIONS = {
    'active': _('Ativo'),
    'inactive': _('Inativo'),
    'pending': _('Pendente'),
    'approved': _('Aprovado'),
    'rejected': _('Rejeitado'),
    'suspended': _('Suspenso'),
    'completed': _('Concluído'),
    'in_progress': _('Em Andamento'),
    'failed': _('Falhou'),
    'cancelled': _('Cancelado'),
}

def get_language_choices():
    """Get available language choices"""
    return [
        ('pt-br', _('Português (Brasil)')),
        ('en', _('English')),
        ('es', _('Español')),
    ]

def get_translated_choices(choices_dict: Dict[str, str]) -> list:
    """
    Convert a dictionary of choices to translated tuples
    
    Args:
        choices_dict: Dictionary with key-value pairs
        
    Returns:
        List of (key, translated_value) tuples
    """
    return [(key, _(value)) for key, value in choices_dict.items()]

def get_user_language(request):
    """Get user's preferred language from request"""
    if hasattr(request, 'user') and request.user.is_authenticated:
        # Try to get from user profile
        if hasattr(request.user, 'profile') and hasattr(request.user.profile, 'language'):
            return request.user.profile.language
    
    # Fallback to session or browser language
    return request.LANGUAGE_CODE if hasattr(request, 'LANGUAGE_CODE') else settings.LANGUAGE_CODE

def format_currency(amount: float, currency: str = 'BRL') -> str:
    """Format currency amount based on locale"""
    import locale
    from django.utils.translation import get_language
    
    current_lang = get_language()
    
    if current_lang == 'pt-br':
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
            return locale.currency(amount, grouping=True)
        except:
            return f'R$ {amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    elif current_lang == 'en':
        return f'${amount:,.2f}'
    elif current_lang == 'es':
        return f'€{amount:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    else:
        return f'{amount:,.2f}'

def format_date(date_obj, format_type: str = 'short'):
    """Format date based on locale"""
    from django.utils.formats import date_format
    from django.utils.translation import get_language
    
    if not date_obj:
        return ''
    
    current_lang = get_language()
    
    if format_type == 'short':
        if current_lang == 'pt-br':
            return date_obj.strftime('%d/%m/%Y')
        elif current_lang == 'en':
            return date_obj.strftime('%m/%d/%Y')
        elif current_lang == 'es':
            return date_obj.strftime('%d/%m/%Y')
    elif format_type == 'long':
        return date_format(date_obj, 'DATE_FORMAT')
    
    return date_format(date_obj)

def get_error_messages():
    """Get common error messages in current language"""
    return {
        'required': _('Este campo é obrigatório.'),
        'invalid': _('Valor inválido.'),
        'max_length': _('Certifique-se de que este valor tenha no máximo %(limit_value)d caracteres.'),
        'min_length': _('Certifique-se de que este valor tenha pelo menos %(limit_value)d caracteres.'),
        'invalid_email': _('Digite um endereço de e-mail válido.'),
        'invalid_date': _('Digite uma data válida.'),
        'invalid_number': _('Digite um número válido.'),
        'file_too_large': _('O arquivo é muito grande. Tamanho máximo permitido: %(max_size)s.'),
        'invalid_file_type': _('Tipo de arquivo não suportado.'),
        'permission_denied': _('Você não tem permissão para realizar esta ação.'),
        'not_found': _('O item solicitado não foi encontrado.'),
        'duplicate': _('Este item já existe.'),
        'network_error': _('Erro de conexão. Tente novamente.'),
        'server_error': _('Erro interno do servidor. Tente novamente mais tarde.'),
    }

