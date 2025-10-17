# 🔄 Guia de Migração - Código Antigo para Nova Estrutura

Este guia ajuda você a migrar código que usa a estrutura antiga para a nova estrutura modular.

## 📌 Visão Geral das Mudanças

| Aspecto | Antes | Depois |
|---------|-------|--------|
| Estrutura | Arquivos na raiz | Pacote `src/agente_viagem/` |
| Configuração | Valores hardcoded | Classe `Settings` |
| Imports | `from worflow import ...` | `from src.agente_viagem.agents import ...` |
| Execução | `python worflow.py` | `python main.py` |

## 🗂️ Mapeamento de Arquivos

### Código Antigo → Código Novo

```
worflow.py                → src/agente_viagem/agents/travel_agent.py + main.py
state.py                  → src/agente_viagem/models/state.py
tools.py                  → src/agente_viagem/tools/web_tools.py + trip_tools.py
memorias.py               → src/agente_viagem/services/memory_service.py + tools/memory_tools.py
prompt.py                 → src/agente_viagem/agents/prompts.py
banco_persistencia.py     → src/agente_viagem/services/database.py
```

## 📝 Exemplos de Migração

### 1. Importação de Modelos

**Antes:**
```python
from state import Place, Trip, AgenteViagemState
```

**Depois:**
```python
from src.agente_viagem.models import Place, Trip, AgenteViagemState
```

**Ou use o wrapper de compatibilidade (temporário):**
```python
from state_compat import Place, Trip, AgenteViagemState
# ⚠️ Isto emitirá um aviso de depreciação
```

### 2. Importação de Ferramentas

**Antes:**
```python
from tools import search, buscar_conteudo_completo_site, add_trips
from memorias import store_memory_tool, retrieve_memories_tool
```

**Depois:**
```python
from src.agente_viagem.tools import (
    search,
    buscar_conteudo_completo_site,
    add_trips,
    store_memory_tool,
    retrieve_memories_tool
)
```

### 3. Banco de Dados

**Antes:**
```python
from banco_persistencia import memory_db

# Usar diretamente
workflow = create_react_agent(..., checkpointer=memory_db)
```

**Depois:**
```python
from src.agente_viagem.services import DatabaseService

# Criar serviço
db_service = DatabaseService()

# Usar checkpointer
workflow = create_react_agent(..., checkpointer=db_service.checkpointer)
```

### 4. Configurações

**Antes:**
```python
# Valores hardcoded no código
LIMITE_MENSAGENS_PARA_SUMARIZACAO = 10
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
```

**Depois:**
```python
from src.agente_viagem.config import (
    Settings,
    LIMITE_MENSAGENS_PARA_SUMARIZACAO,
    OPENAI_MODEL
)

settings = Settings()
settings.validate()

summarizer = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
```

### 5. Criação do Agente

**Antes:**
```python
from worflow import workflow, print_stream_update
from langchain_core.messages import HumanMessage

configuracao = {
    "configurable": {
        "thread_id": "conversa_1",
        "user_id": "Gustavo"
    }
}

for chunk in workflow.stream(
    {"messages": [HumanMessage(content="Olá")]},
    config=configuracao,
    stream_mode="updates"
):
    print_stream_update(chunk)
```

**Depois:**
```python
from src.agente_viagem.agents import TravelAgent
from src.agente_viagem.config import Settings
from src.agente_viagem.utils import print_stream_update
from langchain_core.messages import HumanMessage

# Inicializa configurações
settings = Settings()
settings.validate()

# Cria agente com context manager
with TravelAgent(settings) as agent:
    configuracao = {
        "configurable": {
            "thread_id": "conversa_1",
            "user_id": "Gustavo"
        }
    }
    
    for chunk in agent.workflow.stream(
        {"messages": [HumanMessage(content="Olá")]},
        config=configuracao,
        stream_mode="updates"
    ):
        print_stream_update(chunk)
```

### 6. Uso de Memórias

**Antes:**
```python
from memorias import Memory, store_memory_tool, retrieve_memories_tool

# Criar memória
memoria = Memory(
    content="Usuário prefere hotéis boutique",
    memory_type="episodic"
)
```

**Depois:**
```python
from src.agente_viagem.models import Memory
from src.agente_viagem.tools import store_memory_tool, retrieve_memories_tool

# Criar memória (mesma sintaxe)
memoria = Memory(
    content="Usuário prefere hotéis boutique",
    memory_type="episodic"
)
```

## 🔧 Script de Migração Automática

Para facilitar a migração, você pode usar este script:

```python
#!/usr/bin/env python
"""
Script para atualizar imports do código antigo para novo.
Uso: python migrate_imports.py <arquivo.py>
"""

import sys
import re

REPLACEMENTS = {
    r'from state import': 'from src.agente_viagem.models import',
    r'from tools import': 'from src.agente_viagem.tools import',
    r'from memorias import': 'from src.agente_viagem.tools import',
    r'from banco_persistencia import memory_db': 
        'from src.agente_viagem.services import DatabaseService',
    r'from prompt import': 'from src.agente_viagem.agents.prompts import',
    r'from worflow import': 'from src.agente_viagem.agents import TravelAgent',
}

def migrate_file(filename):
    """Migra imports em um arquivo Python."""
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    for old, new in REPLACEMENTS.items():
        content = re.sub(old, new, content)
    
    if content != original:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename} migrado com sucesso")
    else:
        print(f"ℹ️  {filename} não precisa de migração")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python migrate_imports.py <arquivo.py>")
        sys.exit(1)
    
    migrate_file(sys.argv[1])
```

## ⚠️ Avisos Importantes

### 1. Wrappers de Compatibilidade São Temporários

Os arquivos `*_compat.py` existem apenas para facilitar a transição:

```python
# ⚠️ Este código emite avisos de depreciação
from state_compat import Place
# UserWarning: O arquivo state.py na raiz está depreciado...
```

**Ação Requerida:** Migre para os imports novos o quanto antes.

### 2. Mudança no Ponto de Entrada

**Antes:**
```bash
python worflow.py
```

**Depois:**
```bash
python main.py
```

### 3. Configurações no .env

Certifique-se de ter o arquivo `.env` configurado:

```env
OPENAI_API_KEY=sua-chave-aqui
QDRANT_API_KEY=sua-chave-aqui  # Opcional para Qdrant local
```

### 4. Validação de Configurações

A nova estrutura valida configurações:

```python
settings = Settings()
settings.validate()  # Lança ValueError se OPENAI_API_KEY não existir
```

## 📋 Checklist de Migração

Use este checklist para garantir uma migração completa:

- [ ] Atualizei imports de `state.py` → `src.agente_viagem.models`
- [ ] Atualizei imports de `tools.py` → `src.agente_viagem.tools`
- [ ] Atualizei imports de `memorias.py` → `src.agente_viagem.tools`
- [ ] Atualizei imports de `banco_persistencia.py` → `src.agente_viagem.services`
- [ ] Atualizei imports de `prompt.py` → `src.agente_viagem.agents.prompts`
- [ ] Atualizei imports de `worflow.py` → `src.agente_viagem.agents`
- [ ] Criei classe `Settings` para configurações
- [ ] Adicionei validação de configurações
- [ ] Atualizei ponto de entrada para `main.py`
- [ ] Testei o código migrado
- [ ] Removi dependências dos arquivos antigos

## 🐛 Problemas Comuns e Soluções

### Problema 1: ModuleNotFoundError

**Erro:**
```
ModuleNotFoundError: No module named 'src'
```

**Solução:**
Execute o Python do diretório raiz do projeto:
```bash
cd /caminho/para/agente_viagem_com_memoria
python main.py
```

### Problema 2: OPENAI_API_KEY não encontrada

**Erro:**
```
ValueError: OPENAI_API_KEY não encontrada
```

**Solução:**
Crie um arquivo `.env` na raiz do projeto:
```env
OPENAI_API_KEY=sua-chave-aqui
```

### Problema 3: Qdrant Connection Refused

**Erro:**
```
httpx.ConnectError: [Errno 111] Connection refused
```

**Solução:**
Inicie o Qdrant antes de executar:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Problema 4: Imports Antigos Ainda Funcionam

**Situação:**
Código antigo ainda funciona mas com warnings.

**Explicação:**
Os wrappers de compatibilidade (`*_compat.py`) permitem que código antigo funcione temporariamente.

**Ação:**
Migre para os imports novos para evitar problemas futuros.

## 🎓 Recursos Adicionais

- [ESTRUTURA.md](ESTRUTURA.md) - Documentação da nova estrutura
- [MELHORES_PRATICAS.md](MELHORES_PRATICAS.md) - Guia de melhores práticas
- [README.md](README.md) - Documentação principal do projeto

## 💬 Dúvidas?

Se encontrar problemas durante a migração:

1. Consulte a documentação em `ESTRUTURA.md`
2. Verifique os exemplos em `main.py`
3. Abra uma issue no repositório

---

**Nota:** Os arquivos antigos (`worflow.py`, `state.py`, etc.) serão removidos em uma versão futura. Migre seu código o quanto antes!
