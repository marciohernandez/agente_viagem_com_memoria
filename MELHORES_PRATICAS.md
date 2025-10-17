# 🔧 Guia de Melhores Práticas - Agente de Viagens com Memória

Este documento descreve as melhores práticas implementadas no projeto e recomendações para desenvolvimento futuro.

## 📚 Índice

1. [Organização de Código](#organização-de-código)
2. [Configuração e Ambiente](#configuração-e-ambiente)
3. [Gerenciamento de Dependências](#gerenciamento-de-dependências)
4. [Padrões de Código](#padrões-de-código)
5. [Tratamento de Erros](#tratamento-de-erros)
6. [Testes](#testes)
7. [Documentação](#documentação)
8. [Segurança](#segurança)

## 🗂️ Organização de Código

### Estrutura de Pacotes

O projeto segue a estrutura de pacotes recomendada para projetos Python:

```
src/
  agente_viagem/
    config/         # Configurações isoladas
    models/         # Modelos de dados
    services/       # Lógica de negócio
    tools/          # Ferramentas do agente
    agents/         # Orquestração de workflows
    utils/          # Utilitários
```

**Benefícios:**
- ✅ Código organizado e fácil de navegar
- ✅ Responsabilidades claras
- ✅ Facilita testes unitários
- ✅ Permite reutilização de componentes

### Separação de Responsabilidades (SoC)

Cada módulo tem uma única responsabilidade:

```python
# ❌ Evite misturar responsabilidades
class Agent:
    def __init__(self):
        self.db = sqlite3.connect("db.sqlite")  # Responsabilidade de DB
        self.config = load_config()              # Responsabilidade de Config
        self.llm = ChatOpenAI()                  # Responsabilidade de LLM

# ✅ Prefira separação clara
class Agent:
    def __init__(self, db_service: DatabaseService, config: Settings):
        self.db_service = db_service
        self.config = config
```

## ⚙️ Configuração e Ambiente

### Centralização de Configurações

Use a classe `Settings` para gerenciar todas as configurações:

```python
from src.agente_viagem.config import Settings

# ✅ Bom - configurações centralizadas
settings = Settings()
settings.validate()  # Valida antes de usar

# ❌ Evite - acesso direto a variáveis de ambiente
import os
api_key = os.getenv("OPENAI_API_KEY")
```

### Constantes vs Valores Mágicos

Sempre use constantes nomeadas:

```python
# ❌ Evite valores mágicos
if len(messages) > 10:
    summarize()

# ✅ Use constantes
from src.agente_viagem.config import LIMITE_MENSAGENS_PARA_SUMARIZACAO

if len(messages) > LIMITE_MENSAGENS_PARA_SUMARIZACAO:
    summarize()
```

### Validação de Configurações

Sempre valide configurações críticas:

```python
class Settings:
    def validate(self) -> None:
        """Valida se as configurações obrigatórias estão presentes."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não encontrada")
```

## 📦 Gerenciamento de Dependências

### Uso do pyproject.toml

Mantenha todas as dependências no `pyproject.toml`:

```toml
[project]
dependencies = [
    "langchain>=0.3.27",
    "langgraph>=0.6.9",
    # ...
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "black>=24.0.0",
]
```

### Instalação de Dependências

```bash
# Produção
uv sync

# Desenvolvimento (inclui ferramentas de dev)
uv sync --all-extras
```

## 🎨 Padrões de Código

### Type Hints

Sempre use type hints para melhor IDE support e documentação:

```python
# ✅ Bom
def store_memories(
    self,
    memories: List[Memory],
    user_id: Optional[str] = None
) -> str:
    pass

# ❌ Evite
def store_memories(self, memories, user_id=None):
    pass
```

### Docstrings

Use docstrings no estilo Google:

```python
def retrieve_memories(
    self,
    query: str,
    limit: int = 5
) -> str:
    """Recupera memórias por similaridade semântica.
    
    Args:
        query: Consulta para busca de similaridade
        limit: Número máximo de memórias a retornar
        
    Returns:
        String formatada com memórias encontradas
        
    Raises:
        ValueError: Se limit for maior que MAX_MEMORY_RETRIEVAL_LIMIT
    """
    pass
```

### Context Managers

Use context managers para gerenciar recursos:

```python
# ✅ Bom - recursos são liberados automaticamente
with TravelAgent(settings) as agent:
    result = agent.workflow.stream(...)

# ❌ Evite - recursos podem vazar
agent = TravelAgent(settings)
result = agent.workflow.stream(...)
# Esqueceu de chamar agent.close()
```

### Injeção de Dependências

Injete dependências via construtor:

```python
# ✅ Bom - testável e flexível
class TravelAgent:
    def __init__(self, settings: Settings, db_service: DatabaseService):
        self.settings = settings
        self.db_service = db_service

# ❌ Evite - acoplamento forte
class TravelAgent:
    def __init__(self):
        self.settings = Settings()  # Cria internamente
        self.db_service = DatabaseService()
```

## 🔍 Tratamento de Erros

### Validação de Entrada

Valide entradas antes de processar:

```python
def retrieve_memories(self, limit: int = 5) -> str:
    if limit > MAX_MEMORY_RETRIEVAL_LIMIT:
        raise ValueError(
            f"Limite {limit} excede o máximo permitido de {MAX_MEMORY_RETRIEVAL_LIMIT}"
        )
    # Processa...
```

### Mensagens de Erro Informativas

Forneça mensagens claras e acionáveis:

```python
# ✅ Bom - mensagem clara e solução
raise ValueError(
    "OPENAI_API_KEY não encontrada. "
    "Configure no arquivo .env ou como variável de ambiente."
)

# ❌ Evite - mensagem vaga
raise ValueError("Configuração inválida")
```

### Try-Except Específicos

Capture exceções específicas, não genéricas:

```python
# ✅ Bom - captura específica
try:
    response = self.client.get(url)
except httpx.ConnectError as e:
    return f"Erro de conexão: {str(e)}"
except httpx.TimeoutError as e:
    return f"Timeout: {str(e)}"

# ❌ Evite - captura genérica
try:
    response = self.client.get(url)
except Exception as e:
    return f"Erro: {str(e)}"
```

## 🧪 Testes

### Estrutura de Testes

Organize testes seguindo a estrutura do código:

```
tests/
  test_config/
    test_settings.py
  test_models/
    test_state.py
  test_services/
    test_database.py
    test_memory_service.py
  test_tools/
    test_web_tools.py
```

### Testes Unitários

Teste cada componente isoladamente:

```python
import pytest
from src.agente_viagem.config import Settings

def test_settings_validation():
    """Testa validação de configurações."""
    settings = Settings()
    
    # Deve validar com sucesso se OPENAI_API_KEY está presente
    with pytest.raises(ValueError, match="OPENAI_API_KEY não encontrada"):
        settings.openai_api_key = ""
        settings.validate()
```

### Mocks e Fixtures

Use mocks para dependências externas:

```python
import pytest
from unittest.mock import Mock

@pytest.fixture
def mock_qdrant_client():
    """Mock do cliente Qdrant."""
    client = Mock()
    client.collection_exists.return_value = True
    return client

def test_memory_service(mock_qdrant_client):
    """Testa serviço de memórias com mock."""
    # Usa o mock ao invés de conexão real
    pass
```

## 📖 Documentação

### README.md

Mantenha o README atualizado com:
- Visão geral do projeto
- Instruções de instalação
- Exemplos de uso
- Estrutura do projeto

### ESTRUTURA.md

Documente a organização do código:
- Descrição de cada módulo
- Fluxo de dados
- Padrões utilizados

### Docstrings

Documente todas as classes públicas e métodos:

```python
class MemoryService:
    """Gerencia memórias de longo prazo usando Qdrant.
    
    Esta classe fornece métodos para armazenar e recuperar
    memórias em um banco vetorial Qdrant.
    
    Attributes:
        settings: Configurações da aplicação
        collection_name: Nome da coleção Qdrant
    """
```

## 🔒 Segurança

### Nunca Commit Secrets

Use `.gitignore` para excluir:

```gitignore
.env
*.sqlite
*.db
secrets/
```

### Variáveis de Ambiente

Armazene secrets em variáveis de ambiente:

```bash
# .env (nunca commitar)
OPENAI_API_KEY=sk-...
QDRANT_API_KEY=...
```

### Validação de Entrada

Sempre valide entrada do usuário:

```python
def store_memories(self, memories: List[Memory]) -> str:
    # Valida entrada
    if not memories:
        return "Nenhuma memória fornecida"
    
    # Valida estrutura
    for mem in memories:
        if not mem.content:
            return f"Memória inválida: conteúdo vazio"
```

## 📋 Checklist de Código Limpo

Antes de fazer commit, verifique:

- [ ] Código está organizado em módulos apropriados
- [ ] Configurações estão centralizadas
- [ ] Type hints estão presentes
- [ ] Docstrings estão completas
- [ ] Tratamento de erros é específico
- [ ] Testes cobrem funcionalidade principal
- [ ] Documentação está atualizada
- [ ] Sem secrets no código
- [ ] Código formatado (Black/Ruff)
- [ ] Imports organizados

## 🚀 Próximos Passos

Para melhorar ainda mais o projeto:

1. **Logging**: Implementar logging estruturado
2. **Métricas**: Adicionar métricas de performance
3. **CI/CD**: Configurar pipeline de integração contínua
4. **Testes**: Aumentar cobertura de testes
5. **Type Checking**: Adicionar mypy para verificação de tipos
6. **API**: Criar API REST para o agente
7. **Containerização**: Criar Dockerfile para deployment

## 📚 Referências

- [PEP 8 - Style Guide for Python Code](https://pep8.org/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [The Twelve-Factor App](https://12factor.net/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
