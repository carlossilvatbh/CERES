# Contribuindo para o CERES

Obrigado por considerar contribuir para o CERES! 🎉

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)
- [Desenvolvimento](#desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)

## 🤝 Código de Conduta

Este projeto adere ao [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). Ao participar, você deve seguir este código.

## 🚀 Como Contribuir

### Tipos de Contribuição

Aceitamos vários tipos de contribuições:

- 🐛 **Correção de bugs**
- ✨ **Novas funcionalidades**
- 📖 **Melhorias na documentação**
- 🧪 **Testes**
- 🎨 **Melhorias de UI/UX**
- 🔧 **Refatoração de código**
- 🌐 **Traduções**

### Antes de Começar

1. Verifique se já existe uma [issue](https://github.com/carlossilvatbh/CERES/issues) relacionada
2. Se não existir, crie uma nova issue descrevendo o problema ou melhoria
3. Aguarde feedback da equipe antes de começar o desenvolvimento

## 🐛 Reportando Bugs

### Antes de Reportar

- Verifique se o bug já foi reportado nas [issues existentes](https://github.com/carlossilvatbh/CERES/issues)
- Teste na versão mais recente do projeto
- Verifique se o problema persiste em diferentes navegadores/ambientes

### Como Reportar

Use o [template de bug report](.github/ISSUE_TEMPLATE/bug_report.md) e inclua:

- **Descrição clara** do problema
- **Passos para reproduzir** o bug
- **Comportamento esperado** vs **comportamento atual**
- **Screenshots** (se aplicável)
- **Informações do ambiente**:
  - OS: [ex: Windows 10, macOS 12.0, Ubuntu 20.04]
  - Navegador: [ex: Chrome 96, Firefox 95]
  - Versão do CERES: [ex: 1.0.0]

## ✨ Sugerindo Melhorias

### Antes de Sugerir

- Verifique se a funcionalidade já foi sugerida
- Considere se a melhoria se alinha com os objetivos do projeto
- Pense em como a funcionalidade beneficiaria outros usuários

### Como Sugerir

Use o [template de feature request](.github/ISSUE_TEMPLATE/feature_request.md) e inclua:

- **Descrição clara** da funcionalidade
- **Justificativa** para a melhoria
- **Casos de uso** específicos
- **Mockups ou exemplos** (se aplicável)

## 💻 Desenvolvimento

### Configuração do Ambiente

1. **Fork** o repositório
2. **Clone** seu fork:
   ```bash
   git clone https://github.com/SEU-USERNAME/CERES.git
   cd CERES
   ```

3. **Configure o upstream**:
   ```bash
   git remote add upstream https://github.com/carlossilvatbh/CERES.git
   ```

4. **Instale as dependências**:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt

   # Frontend
   cd ../frontend
   npm install
   ```

5. **Configure o ambiente**:
   ```bash
   cp backend/.env.example backend/.env
   # Edite o arquivo .env com suas configurações
   ```

### Workflow de Desenvolvimento

1. **Crie uma branch** para sua feature:
   ```bash
   git checkout -b feature/nome-da-feature
   ```

2. **Faça suas alterações** seguindo os padrões de código

3. **Execute os testes**:
   ```bash
   # Backend
   cd backend
   python manage.py test

   # Frontend
   cd frontend
   npm test
   ```

4. **Commit suas mudanças**:
   ```bash
   git add .
   git commit -m "feat: adiciona nova funcionalidade X"
   ```

5. **Push para seu fork**:
   ```bash
   git push origin feature/nome-da-feature
   ```

6. **Abra um Pull Request**

## 📝 Padrões de Código

### Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` mudanças na documentação
- `style:` formatação, ponto e vírgula, etc
- `refactor:` refatoração de código
- `test:` adição ou correção de testes
- `chore:` tarefas de manutenção

**Exemplos:**
```
feat: adiciona screening de empresas
fix: corrige erro de validação no formulário
docs: atualiza guia de instalação
```

### Python (Backend)

- Siga o [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) para formatação
- Use [isort](https://isort.readthedocs.io/) para imports
- Docstrings no formato [Google Style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

```python
def process_document(document_path: str) -> Dict[str, Any]:
    """Processa um documento e extrai informações.
    
    Args:
        document_path: Caminho para o arquivo do documento.
        
    Returns:
        Dicionário com informações extraídas do documento.
        
    Raises:
        DocumentProcessingError: Se o documento não puder ser processado.
    """
    pass
```

### JavaScript/React (Frontend)

- Use [ESLint](https://eslint.org/) e [Prettier](https://prettier.io/)
- Componentes funcionais com hooks
- TypeScript quando possível
- Nomes de componentes em PascalCase
- Props e variáveis em camelCase

```jsx
const CustomerForm = ({ onSubmit, initialData }) => {
  const [formData, setFormData] = useState(initialData || {});
  
  const handleSubmit = (event) => {
    event.preventDefault();
    onSubmit(formData);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      {/* componente */}
    </form>
  );
};
```

### CSS/Tailwind

- Use classes utilitárias do Tailwind
- Componentes customizados em `src/components/ui/`
- Siga o design system BTS
- Mobile-first approach

## 🔄 Processo de Pull Request

### Checklist

Antes de submeter seu PR, verifique:

- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam (`npm test` e `python manage.py test`)
- [ ] Documentação foi atualizada (se necessário)
- [ ] Commits seguem o padrão Conventional Commits
- [ ] PR tem descrição clara do que foi alterado
- [ ] Screenshots incluídas (para mudanças de UI)

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças realizadas.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar
1. Passo 1
2. Passo 2
3. Passo 3

## Screenshots
(Se aplicável)

## Checklist
- [ ] Testes passam
- [ ] Código segue os padrões
- [ ] Documentação atualizada
```

### Processo de Review

1. **Automated checks** devem passar
2. **Code review** por pelo menos 1 maintainer
3. **Testing** em ambiente de staging
4. **Approval** e merge

## 🧪 Testes

### Backend (Django)

```bash
# Executar todos os testes
python manage.py test

# Executar testes específicos
python manage.py test apps.customer_enrollment.tests

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

### Frontend (React)

```bash
# Executar todos os testes
npm test

# Executar testes específicos
npm test -- --testNamePattern="CustomerForm"

# Com coverage
npm test -- --coverage
```

## 📖 Documentação

### Atualizando Docs

- Documentação da API: `docs/api-documentation.md`
- Manual do usuário: `docs/user-manual.md`
- Guias técnicos: `docs/`

### Gerando Docs da API

```bash
cd backend
python manage.py generate_api_docs
```

## 🌐 Traduções

Aceitamos traduções para outros idiomas:

1. Copie `frontend/src/locales/pt-BR.json`
2. Traduza as strings
3. Adicione o novo idioma em `frontend/src/i18n/index.js`
4. Teste a tradução
5. Submeta um PR

## 🆘 Precisa de Ajuda?

- 💬 [Discussões no GitHub](https://github.com/carlossilvatbh/CERES/discussions)
- 📧 Email: dev@ceres-system.com
- 📖 [Documentação](docs/)

## 🙏 Reconhecimento

Todos os contribuidores serão reconhecidos no arquivo [CONTRIBUTORS.md](CONTRIBUTORS.md) e nos releases do projeto.

---

**Obrigado por contribuir para o CERES! 🚀**

