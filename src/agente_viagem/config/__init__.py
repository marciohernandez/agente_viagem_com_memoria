"""Configurações do sistema."""

from .settings import Settings
from .constants import (
    LIMITE_MENSAGENS_PARA_SUMARIZACAO,
    OPENAI_MODEL,
    EMBEDDING_MODEL,
    QDRANT_COLLECTION_NAME,
)

__all__ = [
    "Settings",
    "LIMITE_MENSAGENS_PARA_SUMARIZACAO",
    "OPENAI_MODEL",
    "EMBEDDING_MODEL",
    "QDRANT_COLLECTION_NAME",
]
