"""Ferramentas para gerenciamento de memórias de longo prazo."""

from typing import Annotated, List, Literal, Optional
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool

from ..models.memory import Memory
from ..services.memory_service import MemoryService
from ..config.constants import MAX_MEMORY_RETRIEVAL_LIMIT


# Instância global do serviço de memórias (lazy-loaded)
_memory_service: Optional[MemoryService] = None


def _get_memory_service() -> MemoryService:
    """Retorna a instância do serviço de memórias, criando-a se necessário."""
    global _memory_service
    if _memory_service is None:
        _memory_service = MemoryService()
    return _memory_service


@tool
def store_memory_tool(
    memories: Annotated[
        List[Memory],
        "Lista de memórias que serão registradas no banco de dados"
    ],
    config: RunnableConfig,
) -> str:
    """Armazena memórias de longo prazo no banco vetorial Qdrant.

    Esta ferramenta permite registrar informações importantes sobre o usuário ou contexto
    da conversa no banco de dados vetorial, categorizadas por tipo de memória.

    Args:
        memories: Lista de objetos Memory contendo o conteúdo e tipo de cada memória.
            Tipos disponíveis:
            - SEMANTIC: Conhecimento geral e fatos (ex: "Python é uma linguagem de programação")
            - EPISODIC: Experiências e preferências do usuário (ex: "Usuário prefere café da manhã")
        config: Configuração de execução contendo user_id e thread_id para identificação.

    Returns:
        String confirmando o sucesso do registro ou descrevendo o erro ocorrido.
    """
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    thread_id = configurable.get("thread_id")
    
    return _get_memory_service().store_memories(
        memories=memories,
        user_id=user_id,
        thread_id=thread_id
    )


@tool
def retrieve_memories_tool(
    query: Annotated[
        str,
        "Consulta necessária para recuperar as memórias mais similares registradas no banco vetorial."
    ],
    memory_type: Annotated[
        List[Literal["episodic", "semantic"]],
        "Lista de tipos de memórias que serão utilizadas como filtro do banco de dados."
    ],
    limit: Annotated[
        int,
        f"Quantidade de registros de memórias que serão recuperadas. Limite máximo {MAX_MEMORY_RETRIEVAL_LIMIT}."
    ],
    config: RunnableConfig,
) -> str:
    """Recupera memórias de longo prazo do banco vetorial usando busca por similaridade.

    Esta ferramenta busca memórias armazenadas previamente que são semanticamente similares
    à consulta fornecida. É possível filtrar por tipo de memória e limitar a quantidade de resultados.

    Args:
        query: Texto de consulta usado para encontrar memórias semanticamente similares.
        memory_type: Lista de tipos de memória para filtrar os resultados.
            Tipos disponíveis:
            - semantic: Conhecimento geral e fatos
            - episodic: Experiências e preferências do usuário
            Se vazio, busca em todos os tipos.
        limit: Número máximo de memórias a serem retornadas (máximo 10).
        config: Configuração de execução contendo user_id para filtrar memórias do usuário.

    Returns:
        String formatada contendo as memórias encontradas com seus tipos, ou mensagem
        indicando que nenhuma memória relevante foi encontrada.
    """
    configurable = config.get("configurable", {})
    user_id = configurable.get("user_id")
    
    return _get_memory_service().retrieve_memories(
        query=query,
        memory_type=memory_type,
        limit=limit,
        user_id=user_id
    )
