# 🏗️ Arquitetura do Sistema - Agente de Viagens com Memória

## Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                         main.py                                  │
│                    (Ponto de Entrada)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    src/agente_viagem/                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   agents/                                   │ │
│  │  ┌──────────────────────────────────────────────┐          │ │
│  │  │         TravelAgent                           │          │ │
│  │  │  - build_workflow()                           │          │ │
│  │  │  - _summarize_conversation()                  │          │ │
│  │  │  - _create_react_agent()                      │          │ │
│  │  └──────────────────────────────────────────────┘          │ │
│  │  ┌──────────────────────────────────────────────┐          │ │
│  │  │         prompts.py                            │          │ │
│  │  │  - PROMPT_AGENTE_VIAGEM                       │          │ │
│  │  └──────────────────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   tools/                                    │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │  web_tools   │  │  trip_tools  │  │  memory_tools    │ │ │
│  │  │              │  │              │  │                  │ │ │
│  │  │ • search     │  │ • add_trips  │  │ • store_memory   │ │ │
│  │  │ • fetch_url  │  │              │  │ • retrieve_mem   │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                  services/                                  │ │
│  │  ┌──────────────────────┐  ┌────────────────────────────┐ │ │
│  │  │  DatabaseService     │  │  MemoryService             │ │ │
│  │  │                      │  │                            │ │ │
│  │  │ • checkpointer       │  │ • store_memories()         │ │ │
│  │  │ • connection         │  │ • retrieve_memories()      │ │ │
│  │  │ • close()            │  │ • _initialize_collection() │ │ │
│  │  └──────────────────────┘  └────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   models/                                   │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐ │ │
│  │  │  state.py    │  │  memory.py   │  │                  │ │ │
│  │  │              │  │              │  │                  │ │ │
│  │  │ • Place      │  │ • Memory     │  │                  │ │ │
│  │  │ • Trip       │  │              │  │                  │ │ │
│  │  │ • AgentState │  │              │  │                  │ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                             │                                    │
│                             ▼                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   config/                                   │ │
│  │  ┌──────────────────────┐  ┌────────────────────────────┐ │ │
│  │  │  settings.py         │  │  constants.py              │ │ │
│  │  │                      │  │                            │ │ │
│  │  │ • Settings class     │  │ • OPENAI_MODEL             │ │ │
│  │  │ • validate()         │  │ • EMBEDDING_MODEL          │ │ │
│  │  │                      │  │ • LIMITE_MENSAGENS         │ │ │
│  │  └──────────────────────┘  └────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                   utils/                                    │ │
│  │  ┌──────────────────────────────────────────────┐          │ │
│  │  │         output_formatter.py                   │          │ │
│  │  │  - print_stream_update()                      │          │ │
│  │  └──────────────────────────────────────────────┘          │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Dependências Externas                          │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   SQLite     │  │   Qdrant     │  │   OpenAI             │  │
│  │   Database   │  │   Vector DB  │  │   API                │  │
│  └──────────────┘  └──────────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Fluxo de Dados

```
1. Usuário → main.py
              ↓
2. main.py → TravelAgent.workflow
              ↓
3. TravelAgent → Summarize Node (se necessário)
              ↓
4. TravelAgent → Agent Node (ReACT loop)
              ↓
5. Agent → Tools (search, add_trips, memory_tools)
              ↓
6. Tools → Services (MemoryService, DatabaseService)
              ↓
7. Services → External Systems (Qdrant, SQLite)
              ↓
8. Response ← Agent ← Services ← External Systems
              ↓
9. main.py ← TravelAgent
              ↓
10. User ← Formatted Output
```

## Camadas da Aplicação

```
┌─────────────────────────────────────────────┐
│        Presentation Layer (main.py)         │  ← Interface com usuário
├─────────────────────────────────────────────┤
│      Orchestration Layer (agents/)          │  ← Workflows e lógica de orquestração
├─────────────────────────────────────────────┤
│         Tool Layer (tools/)                 │  ← Ferramentas específicas
├─────────────────────────────────────────────┤
│       Business Layer (services/)            │  ← Lógica de negócio
├─────────────────────────────────────────────┤
│         Data Layer (models/)                │  ← Modelos de dados
├─────────────────────────────────────────────┤
│      Configuration Layer (config/)          │  ← Configurações e constantes
├─────────────────────────────────────────────┤
│         Utility Layer (utils/)              │  ← Funções auxiliares
└─────────────────────────────────────────────┘
```

## Princípios Arquiteturais

### 1. Separation of Concerns (SoC)
Cada camada tem responsabilidades bem definidas e não se sobrepõem.

### 2. Dependency Inversion
Camadas superiores dependem de abstrações, não de implementações concretas.

```python
# ✅ Bom - depende de abstração
class TravelAgent:
    def __init__(self, settings: Settings):
        self.db_service = DatabaseService(settings)

# ❌ Ruim - depende de implementação concreta
class TravelAgent:
    def __init__(self):
        self.db = sqlite3.connect("db.sqlite")
```

### 3. Single Responsibility
Cada classe/módulo tem apenas uma razão para mudar.

```python
# DatabaseService: gerencia apenas persistência
# MemoryService: gerencia apenas memórias
# TravelAgent: gerencia apenas workflow
```

### 4. Open/Closed Principle
Aberto para extensão, fechado para modificação.

```python
# Fácil adicionar novas ferramentas sem modificar TravelAgent
new_tool = create_custom_tool()
agent = TravelAgent(tools=[*existing_tools, new_tool])
```

### 5. DRY (Don't Repeat Yourself)
Configurações centralizadas evitam duplicação.

```python
# Antes: valores repetidos em vários arquivos
# Depois: uma única fonte de verdade em constants.py
```

## Padrões de Design Utilizados

### 1. Service Layer Pattern
```python
# Services encapsulam lógica de negócio e acesso a dados
class MemoryService:
    def store_memories(...)
    def retrieve_memories(...)
```

### 2. Factory Pattern
```python
# TravelAgent cria componentes internos
def _create_react_agent(self):
    return create_react_agent(...)
```

### 3. Context Manager Pattern
```python
# Gerenciamento automático de recursos
with TravelAgent(settings) as agent:
    # Usa o agente
# Recursos liberados automaticamente
```

### 4. Strategy Pattern
```python
# Diferentes estratégias para ferramentas
search_tool = SearchTool()
memory_tool = MemoryTool()
trip_tool = TripTool()
```

### 5. Configuration Pattern
```python
# Configurações centralizadas e validadas
settings = Settings()
settings.validate()
```

## Benefícios da Arquitetura

### ✅ Manutenibilidade
- Código organizado facilita localização de bugs
- Mudanças são isoladas em módulos específicos
- Documentação clara de responsabilidades

### ✅ Testabilidade
- Componentes independentes facilitam testes unitários
- Mocks e stubs são fáceis de criar
- Injeção de dependências permite substituição

### ✅ Escalabilidade
- Fácil adicionar novos agentes, ferramentas ou serviços
- Estrutura suporta crescimento do projeto
- Pronta para microserviços se necessário

### ✅ Reutilização
- Componentes podem ser usados em outros projetos
- Services são independentes de agentes
- Tools podem ser compartilhadas

### ✅ Clareza
- Estrutura intuitiva facilita onboarding
- Fluxo de dados é claro
- Responsabilidades são explícitas

## Evolução Futura

A arquitetura atual suporta facilmente:

```
┌─────────────────────────────────────────────┐
│  1. Novos Agentes                           │
│     • HotelRecommendationAgent              │
│     • FlightBookingAgent                    │
│     • RestaurantAgent                       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  2. Novas Ferramentas                       │
│     • weather_tool                          │
│     • currency_converter_tool               │
│     • translation_tool                      │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  3. Novos Serviços                          │
│     • CacheService                          │
│     • AnalyticsService                      │
│     • NotificationService                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│  4. API REST                                │
│     • FastAPI endpoints                     │
│     • Autenticação                          │
│     • Rate limiting                         │
└─────────────────────────────────────────────┘
```

## Conclusão

A nova arquitetura transforma o projeto de scripts isolados em uma **aplicação profissional, modular e escalável**, pronta para crescer e evoluir mantendo qualidade e manutenibilidade. 🚀
