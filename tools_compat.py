"""
Wrapper de compatibilidade para código legado.

Este módulo mantém compatibilidade com o código antigo enquanto
redireciona para a nova estrutura.

AVISO: Este arquivo será removido em versões futuras.
        Migre seu código para usar a nova estrutura em src/agente_viagem/
"""

import warnings

# Importa da nova estrutura
from src.agente_viagem.tools import (
    buscar_conteudo_completo_site,
    search,
    add_trips,
)

# Emite aviso de depreciação
warnings.warn(
    "O arquivo tools.py na raiz está depreciado. "
    "Use: from src.agente_viagem.tools import buscar_conteudo_completo_site, search, add_trips",
    DeprecationWarning,
    stacklevel=2
)

__all__ = ["buscar_conteudo_completo_site", "search", "add_trips"]
