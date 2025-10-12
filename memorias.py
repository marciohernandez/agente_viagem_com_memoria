from pydantic import BaseModel

import os
from typing import Annotated, List, Literal

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

from langchain_qdrant import QdrantVectorStore

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

class Memory(BaseModel):
    """Representa uma única memória de longo prazo.

    EPISODIC: Experiências pessoais e preferências específicas do usuário
              (ex: "Usuário prefere companhias aéreas Delta", "Usuário visitou Paris ano passado")

    SEMANTIC: Conhecimento geral de domínio e fatos
              (ex: "Singapura requer passaporte", "Tóquio tem excelente transporte público")
              """

    content: str
    memory_type: Literal["episodic", "semantic"]



## Executando a criação pela primeira vez da coleção vazia.
client = QdrantClient(url="http://localhost:6333", api_key=os.getenv("QDRANT_API_KEY"))

if not client.collection_exists("minhas_memorias"):
    client.create_collection(
        collection_name="minhas_memorias",
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )


## Criando uma conexão para leitura com banco de dados Qdrant:
doc_store = QdrantVectorStore.from_existing_collection(
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    collection_name="minhas_memorias",
    url="http://localhost:6333",
    api_key=os.getenv("QDRANT_API_KEY"),
)


# =================================================================================================================
#                      TOOL RESPONSÁVEL POR SALVAR MEMÓRIA DE LONGO PRAZO
# =================================================================================================================

@tool
def store_memory_tool(
        memories: Annotated[List[Memory], "Lista de memórias que serão registradas no banco de dados"],
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
    user_id = configurable.get("user_id", None)
    thread_id = configurable.get("thread_id", None)

    try:
        list_memories_to_list_documents = []
        for mem in memories:
            list_memories_to_list_documents.append(Document(page_content=mem.content,
                                                            metadata={"memory_type": mem.memory_type,
                                                                      "user_id": user_id,
                                                                      "thread_id": thread_id}))
        ## Registrando as memórias no banco Qdrant:
        QdrantVectorStore.from_documents(
            documents=list_memories_to_list_documents,
            embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
            collection_name="minhas_memorias",
            url="http://localhost:6333",
            api_key=os.getenv("QDRANT_API_KEY"),
        )

        return f"Memórias registradas com sucesso: {memories}"
    except Exception as e:
        return f"Erro no armazenamento das memórias: {str(e)}"


# =================================================================================================================
#                      TOOL RESPONSÁVEL POR RECUPERAR MEMÓRIA DE LONGO PRAZO
# =================================================================================================================

@tool
def retrieve_memories_tool(
        query: Annotated[str, "Consulta necessária para recuperar as memórias mais similares registradas no banco vetorial."],
        memory_type: Annotated[List[Literal["episodic", "semantic"]], "Lista de tipos de memórias que serão utilizadas como filtro do banco de dados."],
        limit: Annotated[int, "Quantidade de registros de memórias que serão recuperadas. Limite máximo 10."],
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

    try:
        # Construir condições de filtro
        filter_conditions = []

        # Adicionar filtro de user_id se fornecido
        if user_id:
            filter_conditions.append(
                models.FieldCondition(
                    key="metadata.user_id",
                    match=models.MatchValue(value=user_id)
                )
            )

        # Adicionar filtro de memory_type se fornecido
        if memory_type:
            filter_conditions.append(
                models.FieldCondition(
                    key="metadata.memory_type",
                    match=models.MatchAny(any=memory_type)
                )
            )

        # Criar filtro Qdrant (se houver condições)
        qdrant_filter = models.Filter(must=filter_conditions) if filter_conditions else None

        # Buscar memórias similares
        memorias_similares = doc_store.similarity_search(
            query=query,
            k=limit,
            filter=qdrant_filter
        )

        # Formatar a resposta
        response = []

        if memorias_similares:
            response.append("Memórias de longo prazo:")
            for doc in memorias_similares:
                tipo_memoria = doc.metadata.get("memory_type", "desconhecido")
                response.append(f"- [{tipo_memoria}] {doc.page_content}")

        return "\n".join(response) if response else "Nenhuma memória relevante encontrada."

    except Exception as e:
        return f"Erro ao recuperar memórias: {str(e)}"