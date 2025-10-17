"""
Wrapper de compatibilidade para código legado.

Este módulo mantém compatibilidade com o código antigo enquanto
redireciona para a nova estrutura.

AVISO: Este arquivo será removido em versões futuras.
        Migre seu código para usar a nova estrutura em src/agente_viagem/
"""

import warnings

# Importa da nova estrutura
from src.agente_viagem.services.database import DatabaseService

# Emite aviso de depreciação
warnings.warn(
    "O arquivo banco_persistencia.py na raiz está depreciado. "
    "Use: from src.agente_viagem.services import DatabaseService",
    DeprecationWarning,
    stacklevel=2
)

# Mantém compatibilidade com código antigo
_db_service = DatabaseService()
memory_db = _db_service.checkpointer

__all__ = ["memory_db"]
