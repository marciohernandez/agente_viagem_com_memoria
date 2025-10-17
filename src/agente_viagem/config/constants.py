"""Constantes do sistema."""

# Configurações de Modelos
OPENAI_MODEL = "gpt-4o-mini"
EMBEDDING_MODEL = "text-embedding-3-small"

# Configurações de Memória
LIMITE_MENSAGENS_PARA_SUMARIZACAO = 10
QDRANT_COLLECTION_NAME = "minhas_memorias"

# Configurações Qdrant
DEFAULT_QDRANT_URL = "http://localhost:6333"
DEFAULT_QDRANT_REST_PORT = 6333
DEFAULT_QDRANT_GRPC_PORT = 6334

# Configurações de Embedding
EMBEDDING_VECTOR_SIZE = 1536

# Configurações de Busca
MAX_MEMORY_RETRIEVAL_LIMIT = 10
DEFAULT_MEMORY_RETRIEVAL_LIMIT = 5

# Timeout para requisições HTTP
HTTP_TIMEOUT_SECONDS = 10.0

# Configurações do SQLite
DEFAULT_SQLITE_DB_NAME = "memorias_agente.sqlite"
