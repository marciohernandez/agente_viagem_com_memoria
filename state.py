from typing import TypedDict, List, Optional, NotRequired
from langgraph.prebuilt.chat_agent_executor import AgentState

class Place(TypedDict):
    """Um lugar."""
    id: str
    name: str
    address: str
    rating: float
    description: Optional[str]

class Trip(TypedDict):
    """Uma viagem."""
    id: str
    name: str
    places: List[Place]

class AgenteViagemState(AgentState):
    """O estado do agente."""
    trips: NotRequired[List[Trip]]
