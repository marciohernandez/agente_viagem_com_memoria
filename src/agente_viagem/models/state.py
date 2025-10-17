"""Definições de estado para o agente de viagem."""

from typing import TypedDict, List, Optional, NotRequired
from langgraph.prebuilt.chat_agent_executor import AgentState


class Place(TypedDict):
    """Representa um lugar de interesse turístico.
    
    Attributes:
        id: Identificador único do lugar
        name: Nome do lugar
        address: Endereço completo
        rating: Avaliação (0-5)
        description: Descrição opcional do lugar
    """
    id: str
    name: str
    address: str
    rating: float
    description: Optional[str]


class Trip(TypedDict):
    """Representa um itinerário de viagem.
    
    Attributes:
        id: Identificador único da viagem
        name: Nome/título da viagem
        places: Lista de lugares a visitar
    """
    id: str
    name: str
    places: List[Place]


class AgenteViagemState(AgentState):
    """Estado do agente de viagem.
    
    Attributes:
        trips: Lista opcional de viagens planejadas
    """
    trips: NotRequired[List[Trip]]
