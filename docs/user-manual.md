# Manual do Usuário - CERES

## 📖 Índice

- [Introdução](#introdução)
- [Primeiros Passos](#primeiros-passos)
- [Dashboard](#dashboard)
- [Cadastro de Clientes](#cadastro-de-clientes)
- [Processamento de Documentos](#processamento-de-documentos)
- [Screening de Sanções](#screening-de-sanções)
- [Relatórios](#relatórios)
- [Configurações](#configurações)
- [Solução de Problemas](#solução-de-problemas)

## 🎯 Introdução

O CERES (Customer Enrollment and Risk Evaluation System) é um sistema completo de compliance e avaliação de risco para instituições financeiras. Este manual irá guiá-lo através de todas as funcionalidades do sistema.

### Objetivos do Sistema

- **KYC (Know Your Customer)**: Cadastro e verificação completa de clientes
- **Screening de Sanções**: Verificação automática contra listas restritivas
- **Processamento de Documentos**: OCR e análise de autenticidade
- **Compliance**: Relatórios e métricas de conformidade regulatória

## 🚀 Primeiros Passos

### Acesso ao Sistema

1. **URL de Acesso**: https://jgngsogp.manus.space
2. **Credenciais de Demonstração**:
   - Usuário: `admin`
   - Senha: `admin123`

### Interface Principal

Após o login, você verá:
- **Sidebar**: Menu de navegação principal
- **Header**: Busca global e perfil do usuário
- **Área Principal**: Conteúdo da página atual
- **Notificações**: Alertas e atualizações em tempo real

## 📊 Dashboard

O Dashboard é a página inicial que oferece uma visão geral do sistema.

### Métricas Principais

#### Cards de Resumo
- **Total de Clientes**: 1.247 (+12% vs mês anterior)
- **Documentos Pendentes**: 23 (-5% vs ontem)
- **Screenings Ativos**: 8 (Em processamento)
- **Alertas de Alto Risco**: 3 (Requer atenção imediata)

#### Gráficos Interativos

**Atividade Mensal**
- Visualiza clientes cadastrados e screenings por mês
- Permite identificar tendências e sazonalidades
- Dados dos últimos 6 meses

**Distribuição de Risco**
- Baixo Risco: 78% (verde)
- Médio Risco: 18% (amarelo)
- Alto Risco: 4% (vermelho)

### Atividades Recentes

Lista das últimas ações no sistema:
- Novos clientes cadastrados
- Documentos processados
- Screenings concluídos
- Alertas gerados

### Ações Rápidas

Botões para acesso direto às funcionalidades mais usadas:
- **Novo Cliente**: Inicia cadastro de cliente
- **Screening**: Inicia nova verificação

## 👥 Cadastro de Clientes

O módulo de cadastro permite registrar novos clientes através de um processo estruturado em 4 etapas.

### Etapa 1: Dados Pessoais

**Campos Obrigatórios:**
- Nome completo
- CPF/CNPJ
- Data de nascimento
- Nacionalidade
- Estado civil

**Campos Opcionais:**
- Nome da mãe
- Profissão
- Renda mensal
- Patrimônio

**Validações:**
- CPF/CNPJ válido
- Data de nascimento (maior de 18 anos)
- Formato de campos

### Etapa 2: Informações de Contato

**Endereço:**
- CEP (busca automática)
- Logradouro
- Número e complemento
- Bairro, cidade, estado

**Contatos:**
- Telefone principal
- Telefone secundário (opcional)
- Email principal
- Email secundário (opcional)

**Validações:**
- CEP válido
- Email em formato correto
- Telefone com DDD

### Etapa 3: Upload de Documentos

**Documentos Aceitos:**
- RG ou CNH
- CPF
- Comprovante de residência
- Comprovante de renda

**Especificações:**
- Formatos: PDF, JPG, PNG
- Tamanho máximo: 10MB por arquivo
- Resolução mínima: 300 DPI (recomendado)

**Processo:**
1. Arraste arquivos ou clique para selecionar
2. Aguarde upload e processamento OCR
3. Verifique dados extraídos automaticamente
4. Corrija informações se necessário

### Etapa 4: Revisão e Confirmação

**Verificação Final:**
- Revise todos os dados inseridos
- Confirme documentos anexados
- Aceite termos e condições
- Finalize o cadastro

**Pós-Cadastro:**
- Cliente recebe ID único
- Screening automático é iniciado
- Notificação é enviada por email

## 📄 Processamento de Documentos

O sistema processa documentos automaticamente usando OCR e análise forense.

### Upload de Documentos

#### Métodos de Upload
1. **Drag & Drop**: Arraste arquivos para a área designada
2. **Seleção Manual**: Clique em "Selecionar Arquivos"
3. **API**: Upload programático via API REST

#### Formatos Suportados
- **PDF**: Documentos digitais e escaneados
- **JPG/JPEG**: Fotos de documentos
- **PNG**: Imagens de alta qualidade

#### Limitações
- Tamanho máximo: 10MB por arquivo
- Máximo 5 arquivos simultâneos
- Resolução mínima: 150 DPI

### Processamento Automático

#### OCR (Reconhecimento Óptico)
- Extração de texto usando Tesseract
- Reconhecimento de campos estruturados
- Validação de dados extraídos
- Correção automática de erros comuns

#### Análise Forense
- Verificação de autenticidade
- Detecção de alterações
- Análise de metadados
- Verificação de assinaturas digitais

### Status de Processamento

#### Estados Possíveis
- **Pendente**: Aguardando processamento
- **Processando**: OCR em andamento
- **Processado**: Concluído com sucesso
- **Erro**: Falha no processamento

#### Filtros Disponíveis
- Todos os documentos
- Por status
- Por tipo de documento
- Por data de upload

### Resultados

#### Dados Extraídos
- Texto completo do documento
- Campos estruturados (nome, CPF, etc.)
- Metadados do arquivo
- Índice de confiança

#### Ações Disponíveis
- Visualizar documento original
- Editar dados extraídos
- Reprocessar documento
- Excluir documento

## 🔍 Screening de Sanções

O módulo de screening verifica clientes contra listas restritivas globais.

### Tipos de Screening

#### Screening Individual
Para pessoas físicas:
- Nome completo
- CPF
- Data de nascimento
- Nacionalidade

#### Screening Empresarial
Para pessoas jurídicas:
- Razão social
- CNPJ
- Sócios e administradores
- Atividade econômica

### Fontes de Dados

#### Listas Oficiais (20+ fontes)
- **OFAC** (EUA): 12.547 registros
- **UN Consolidated List**: 8.932 registros
- **EU Financial Sanctions**: 5.621 registros
- **UK OFSI**: 3.456 registros
- **Banco Central BR**: Lista CSJT

#### Listas PEP
- **OpenSanctions**: Pessoas politicamente expostas
- **WikiData**: Dados estruturados
- **IPU Parline**: Parlamentares globais

#### Dados Corporativos
- **OpenCorporates**: Registro de empresas
- **GLEIF LEI**: Identificadores legais
- **SEC EDGAR**: Empresas listadas (EUA)

### Processo de Screening

#### Execução Automática
1. **Normalização**: Padronização de nomes
2. **Busca Fuzzy**: Correspondência aproximada
3. **Scoring**: Cálculo de similaridade
4. **Filtragem**: Remoção de falsos positivos
5. **Classificação**: Baixo/Médio/Alto risco

#### Configurações
- Threshold de similaridade
- Fontes ativas/inativas
- Frequência de atualização
- Regras de negócio customizadas

### Resultados e Alertas

#### Classificação de Risco
- **Baixo Risco**: 0 matches encontrados
- **Médio Risco**: Matches com baixa similaridade
- **Alto Risco**: Matches com alta similaridade

#### Detalhes do Match
- Nome encontrado na lista
- Fonte da informação
- Percentual de similaridade
- Dados adicionais (aliases, datas)

#### Ações Recomendadas
- **Baixo**: Aprovação automática
- **Médio**: Revisão manual
- **Alto**: Bloqueio e investigação

### Monitoramento Contínuo

#### Atualizações Automáticas
- Verificação diária das fontes
- Download de novas listas
- Re-screening de clientes existentes
- Notificações de novos matches

#### Alertas em Tempo Real
- Email para compliance officer
- Notificações no dashboard
- Integração com sistemas externos
- Logs de auditoria

## 📊 Relatórios

O módulo de relatórios oferece análises detalhadas e documentação de compliance.

### Tipos de Relatórios

#### Relatórios Pré-Definidos
- **Compliance Mensal**: Resumo das atividades
- **Análise de Risco**: Distribuição e tendências
- **Auditoria de Documentos**: Status de processamento
- **Performance de Screening**: Eficácia das verificações

#### Relatórios Personalizados
- Seleção de métricas específicas
- Filtros por período
- Agrupamento por categorias
- Formatos de exportação

### Geração de Relatórios

#### Configuração
1. **Tipo**: Selecione o template desejado
2. **Período**: Defina intervalo de datas
3. **Formato**: PDF, Excel ou CSV
4. **Filtros**: Aplique critérios específicos

#### Processamento
- Geração assíncrona
- Notificação por email
- Download automático
- Armazenamento temporário

### Métricas Disponíveis

#### Métricas de Volume
- Clientes processados
- Documentos analisados
- Screenings realizados
- Alertas gerados

#### Métricas de Performance
- Taxa de detecção
- Tempo médio de processamento
- Falsos positivos
- SLA compliance

#### Métricas de Risco
- Distribuição por nível
- Evolução temporal
- Fontes mais efetivas
- Padrões identificados

### Visualizações

#### Gráficos Interativos
- Barras: Comparação de volumes
- Pizza: Distribuição percentual
- Linha: Tendências temporais
- Área: Evolução acumulada

#### Tabelas Detalhadas
- Dados granulares
- Ordenação e filtros
- Exportação de dados
- Links para detalhes

### Agendamento

#### Relatórios Recorrentes
- Frequência configurável
- Destinatários por email
- Formatos automáticos
- Versionamento histórico

## ⚙️ Configurações

### Configurações de Sistema

#### Fontes de Dados
- Ativar/desativar fontes
- Configurar URLs de API
- Definir frequência de atualização
- Configurar credenciais

#### Regras de Negócio
- Thresholds de similaridade
- Critérios de classificação
- Regras de auto-aprovação
- Escalação de alertas

### Configurações de Usuário

#### Perfil
- Dados pessoais
- Preferências de notificação
- Configurações de interface
- Histórico de atividades

#### Permissões
- Módulos acessíveis
- Níveis de autorização
- Aprovações necessárias
- Logs de auditoria

## 🔧 Solução de Problemas

### Problemas Comuns

#### Login
**Problema**: Não consigo fazer login
**Soluções**:
- Verifique usuário e senha
- Limpe cache do navegador
- Tente navegador diferente
- Contate administrador

#### Upload de Documentos
**Problema**: Erro no upload
**Soluções**:
- Verifique tamanho do arquivo (máx. 10MB)
- Confirme formato suportado
- Teste conexão de internet
- Tente arquivo diferente

#### Screening Lento
**Problema**: Screening demora muito
**Soluções**:
- Verifique status das fontes
- Aguarde processamento assíncrono
- Contate suporte técnico

### Códigos de Erro

#### Erros de Sistema
- **500**: Erro interno do servidor
- **404**: Página não encontrada
- **403**: Acesso negado
- **401**: Não autenticado

#### Erros de Validação
- **400**: Dados inválidos
- **422**: Entidade não processável
- **413**: Arquivo muito grande
- **415**: Tipo de mídia não suportado

### Contato para Suporte

#### Canais de Suporte
- **Email**: suporte@ceres-system.com
- **Telefone**: +55 11 9999-9999
- **Chat**: Disponível no sistema
- **Documentação**: docs.ceres-system.com

#### Informações para Suporte
- Versão do sistema
- Navegador utilizado
- Descrição do problema
- Passos para reproduzir
- Screenshots (se aplicável)

---

**© 2025 CERES. Sistema de Compliance e Avaliação de Risco.**

