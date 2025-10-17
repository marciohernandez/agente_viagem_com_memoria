"""
Wrapper de compatibilidade para código legado.

Este módulo mantém compatibilidade com o código antigo enquanto
redireciona para a nova estrutura.

AVISO: Este arquivo será removido em versões futuras.
        Migre seu código para usar a nova estrutura em src/agente_viagem/
"""

import warnings

# Importa da nova estrutura
from src.agente_viagem.models.state import Place, Trip, AgenteViagemState

# Emite aviso de depreciação
warnings.warn(
    "O arquivo state.py na raiz está depreciado. "
    "Use: from src.agente_viagem.models import Place, Trip, AgenteViagemState",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["Place", "Trip", "AgenteViagemState"]
