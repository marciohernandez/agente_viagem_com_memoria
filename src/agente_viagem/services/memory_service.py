"""Serviço de gerenciamento de memórias no Qdrant."""

from typing import List, Literal, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams

from ..config.settings import Settings
from ..config.constants import (
    QDRANT_COLLECTION_NAME,
    EMBEDDING_MODEL,
    EMBEDDING_VECTOR_SIZE,
)
from ..models.memory import Memory


class MemoryService:
    """Gerencia memórias de longo prazo usando Qdrant."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Inicializa o serviço de memórias.
        
        Args:
            settings: Configurações da aplicação. Se None, usa configurações padrão.
        """
        self.settings = settings or Settings()
        self.collection_name = QDRANT_COLLECTION_NAME
        self._client: Optional[QdrantClient] = None
        self._doc_store: Optional[QdrantVectorStore] = None
        self._embedding = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        
        # Inicializa a coleção se não existir
        self._initialize_collection()
    
    @property
    def client(self) -> QdrantClient:
        """Retorna o cliente Qdrant, criando-o se necessário.
        
        Returns:
            Cliente Qdrant ativo.
        """
        if self._client is None:
            self._client = QdrantClient(
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key
            )
        return self._client
    
    @property
    def doc_store(self) -> QdrantVectorStore:
        """Retorna o vector store Qdrant, criando-o se necessário.
        
        Returns:
            QdrantVectorStore para busca de similaridade.
        """
        if self._doc_store is None:
            self._doc_store = QdrantVectorStore.from_existing_collection(
                embedding=self._embedding,
                collection_name=self.collection_name,
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
            )
        return self._doc_store
    
    def _initialize_collection(self) -> None:
        """Cria a coleção Qdrant se ela não existir."""
        if not self.client.collection_exists(self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=EMBEDDING_VECTOR_SIZE,
                    distance=Distance.COSINE
                ),
            )
    
    def store_memories(
        self,
        memories: List[Memory],
        user_id: Optional[str] = None,
        thread_id: Optional[str] = None
    ) -> str:
        """Armazena memórias no banco vetorial.
        
        Args:
            memories: Lista de memórias a serem armazenadas
            user_id: ID do usuário (opcional)
            thread_id: ID da thread/conversa (opcional)
            
        Returns:
            Mensagem de confirmação ou erro
        """
        try:
            documents = [
                Document(
                    page_content=mem.content,
                    metadata={
                        "memory_type": mem.memory_type,
                        "user_id": user_id,
                        "thread_id": thread_id
                    }
                )
                for mem in memories
            ]
            
            QdrantVectorStore.from_documents(
                documents=documents,
                embedding=self._embedding,
                collection_name=self.collection_name,
                url=self.settings.qdrant_url,
                api_key=self.settings.qdrant_api_key,
            )
            
            return f"Memórias registradas com sucesso: {memories}"
        except Exception as e:
            return f"Erro no armazenamento das memórias: {str(e)}"
    
    def retrieve_memories(
        self,
        query: str,
        memory_type: Optional[List[Literal["episodic", "semantic"]]] = None,
        limit: int = 5,
        user_id: Optional[str] = None
    ) -> str:
        """Recupera memórias por similaridade semântica.
        
        Args:
            query: Consulta para busca de similaridade
            memory_type: Tipos de memória para filtrar (opcional)
            limit: Número máximo de memórias a retornar
            user_id: ID do usuário para filtrar memórias (opcional)
            
        Returns:
            String formatada com memórias encontradas ou mensagem de não encontrado
        """
        try:
            # Construir condições de filtro
            filter_conditions = []
            
            if user_id:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.user_id",
                        match=models.MatchValue(value=user_id)
                    )
                )
            
            if memory_type:
                filter_conditions.append(
                    models.FieldCondition(
                        key="metadata.memory_type",
                        match=models.MatchAny(any=memory_type)
                    )
                )
            
            # Criar filtro Qdrant
            qdrant_filter = (
                models.Filter(must=filter_conditions) 
                if filter_conditions 
                else None
            )
            
            # Buscar memórias similares
            memorias_similares = self.doc_store.similarity_search(
                query=query,
                k=limit,
                filter=qdrant_filter
            )
            
            # Formatar resposta
            if memorias_similares:
                response = ["Memórias de longo prazo:"]
                for doc in memorias_similares:
                    tipo_memoria = doc.metadata.get("memory_type", "desconhecido")
                    response.append(f"- [{tipo_memoria}] {doc.page_content}")
                return "\n".join(response)
            
            return "Nenhuma memória relevante encontrada."
            
        except Exception as e:
            return f"Erro ao recuperar memórias: {str(e)}"
