# 🏗️ Estrutura do Projeto - Agente de Viagens com Memória

## 📁 Visão Geral da Estrutura

```
agente_viagem_com_memoria/
│
├── src/                          # Código fonte principal
│   └── agente_viagem/           # Pacote principal
│       ├── __init__.py
│       │
│       ├── config/              # Configurações
│       │   ├── __init__.py
│       │   ├── settings.py      # Configurações de ambiente
│       │   └── constants.py     # Constantes do sistema
│       │
│       ├── models/              # Modelos de dados
│       │   ├── __init__.py
│       │   ├── state.py         # Estados (Place, Trip, AgenteViagemState)
│       │   └── memory.py        # Modelo de memória
│       │
│       ├── services/            # Camada de serviços
│       │   ├── __init__.py
│       │   ├── database.py      # Serviço de banco de dados SQLite
│       │   └── memory_service.py # Serviço de memórias Qdrant
│       │
│       ├── tools/               # Ferramentas do agente
│       │   ├── __init__.py
│       │   ├── web_tools.py     # Busca web e extração de conteúdo
│       │   ├── trip_tools.py    # Gerenciamento de itinerários
│       │   └── memory_tools.py  # Ferramentas de memória
│       │
│       ├── agents/              # Agentes e workflows
│       │   ├── __init__.py
│       │   ├── travel_agent.py  # Agente principal de viagem
│       │   └── prompts.py       # Prompts do sistema
│       │
│       └── utils/               # Utilitários
│           ├── __init__.py
│           └── output_formatter.py # Formatação de saída
│
├── main.py                      # Ponto de entrada principal
│
├── pyproject.toml              # Configuração do projeto
├── uv.lock                     # Lock de dependências
├── .env.exemplo                # Exemplo de variáveis de ambiente
├── .gitignore                  # Arquivos ignorados pelo git
└── README.md                   # Documentação principal

# Arquivos legados (manter para referência ou remover após validação)
├── worflow.py                  # ⚠️ Código antigo - substituído por src/
├── state.py                    # ⚠️ Código antigo - movido para src/agente_viagem/models/
├── tools.py                    # ⚠️ Código antigo - movido para src/agente_viagem/tools/
├── memorias.py                 # ⚠️ Código antigo - movido para src/agente_viagem/services/
├── prompt.py                   # ⚠️ Código antigo - movido para src/agente_viagem/agents/
└── banco_persistencia.py       # ⚠️ Código antigo - movido para src/agente_viagem/services/
```

## 🎯 Princípios de Design

### 1. **Separação de Responsabilidades**
Cada módulo tem uma responsabilidade clara e específica:
- **config**: Gerencia configurações e constantes
- **models**: Define estruturas de dados
- **services**: Implementa lógica de negócio e acesso a dados
- **tools**: Implementa ferramentas do agente
- **agents**: Orquestra workflows e agentes
- **utils**: Fornece funcionalidades auxiliares

### 2. **Injeção de Dependências**
As classes recebem suas dependências via construtor:
```python
# Exemplo
settings = Settings()
agent = TravelAgent(settings)
db_service = DatabaseService(settings)
```

### 3. **Configuração Centralizada**
Todas as configurações são gerenciadas pela classe `Settings`:
```python
from src.agente_viagem.config import Settings

settings = Settings()  # Carrega do .env
settings.validate()    # Valida configurações
```

### 4. **Constantes Explícitas**
Valores mágicos são evitados usando constantes:
```python
from src.agente_viagem.config.constants import (
    OPENAI_MODEL,
    LIMITE_MENSAGENS_PARA_SUMARIZACAO
)
```

### 5. **Gerenciamento de Recursos**
Uso de context managers para recursos:
```python
with TravelAgent(settings) as agent:
    # Usa o agente
    pass
# Recursos são liberados automaticamente
```

## 🔧 Como Usar a Nova Estrutura

### Executar a aplicação

```bash
# Ativar ambiente virtual
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

# Executar
python main.py
```

### Importar componentes

```python
# Configurações
from src.agente_viagem.config import Settings, OPENAI_MODEL

# Modelos
from src.agente_viagem.models import Place, Trip, AgenteViagemState, Memory

# Serviços
from src.agente_viagem.services import DatabaseService, MemoryService

# Ferramentas
from src.agente_viagem.tools import (
    search,
    buscar_conteudo_completo_site,
    add_trips,
    store_memory_tool,
    retrieve_memories_tool
)

# Agentes
from src.agente_viagem.agents import TravelAgent

# Utilitários
from src.agente_viagem.utils import print_stream_update
```

### Exemplo de uso programático

```python
from langchain_core.messages import HumanMessage
from src.agente_viagem.agents import TravelAgent
from src.agente_viagem.config import Settings

# Inicializa
settings = Settings()
settings.validate()

# Cria agente
with TravelAgent(settings) as agent:
    # Configura conversa
    config = {
        "configurable": {
            "thread_id": "conversa_1",
            "user_id": "Maria"
        }
    }
    
    # Executa
    for chunk in agent.workflow.stream(
        {"messages": [HumanMessage(content="Quero viajar para Portugal")]},
        config=config,
        stream_mode="updates"
    ):
        # Processa resultado
        pass
```

## 📚 Módulos Principais

### `config/settings.py`
Gerencia todas as configurações do sistema:
- Carrega variáveis de ambiente
- Valida configurações obrigatórias
- Fornece valores padrão

### `config/constants.py`
Define todas as constantes do sistema:
- Modelos de IA
- Limites e timeouts
- Configurações padrão

### `models/state.py`
Define os estados do agente:
- `Place`: Lugar turístico
- `Trip`: Itinerário de viagem
- `AgenteViagemState`: Estado completo do agente

### `services/database.py`
Gerencia persistência SQLite:
- Conexão com banco de dados
- Checkpointer do LangGraph
- Context manager para cleanup

### `services/memory_service.py`
Gerencia memórias no Qdrant:
- Armazenamento de memórias
- Busca por similaridade
- Filtros por tipo e usuário

### `agents/travel_agent.py`
Agente principal:
- Cria workflow LangGraph
- Gerencia sumarização
- Orquestra ferramentas

## 🔄 Migração do Código Antigo

Os arquivos na raiz (`worflow.py`, `state.py`, etc.) foram refatorados:

| Arquivo Antigo | Novo Localização |
|----------------|------------------|
| `worflow.py` | `src/agente_viagem/agents/travel_agent.py` + `main.py` |
| `state.py` | `src/agente_viagem/models/state.py` |
| `tools.py` | `src/agente_viagem/tools/web_tools.py` + `trip_tools.py` |
| `memorias.py` | `src/agente_viagem/services/memory_service.py` + `tools/memory_tools.py` |
| `prompt.py` | `src/agente_viagem/agents/prompts.py` |
| `banco_persistencia.py` | `src/agente_viagem/services/database.py` |

## ✅ Benefícios da Nova Estrutura

1. **Manutenibilidade**: Código organizado e fácil de encontrar
2. **Testabilidade**: Módulos independentes facilitam testes
3. **Escalabilidade**: Fácil adicionar novos agentes, ferramentas ou serviços
4. **Reutilização**: Componentes podem ser usados em outros projetos
5. **Documentação**: Estrutura clara facilita entendimento
6. **Type Safety**: Uso adequado de tipos Python
7. **Configuração**: Gerenciamento centralizado de configs

## 🧪 Próximos Passos

- [ ] Adicionar testes unitários
- [ ] Implementar logging estruturado
- [ ] Adicionar validação de entrada
- [ ] Criar CLI interativo
- [ ] Adicionar métricas e monitoramento
- [ ] Documentar APIs com docstrings detalhadas
- [ ] Implementar tratamento de erros mais robusto
