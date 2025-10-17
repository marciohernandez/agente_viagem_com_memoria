"""Ferramentas para gerenciamento de itinerários de viagem."""

from typing import Annotated, List
from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langgraph.types import Command

from ..models.state import Trip


@tool
def add_trips(
    trips: List[Trip],
    tool_call_id: Annotated[str, InjectedToolCallId]
):
    """Adiciona um ou mais itinerários de viagem ao estado do agente.

    Esta ferramenta permite criar e armazenar roteiros de viagem completos, incluindo
    informações sobre destinos, lugares para visitar, endereços e avaliações. Ideal para
    quando o usuário solicita planejamento de viagens ou criação de roteiros turísticos.

    Args:
        trips: Lista de objetos Trip contendo os itinerários de viagem. Cada Trip deve incluir:
            - id: Identificador único da viagem
            - name: Nome ou título da viagem
            - places: Lista de lugares (Place) incluindo nome, endereço, avaliação e descrição
        tool_call_id: ID da chamada da ferramenta (injetado automaticamente pelo sistema).

    Returns:
        Command que atualiza o estado do agente com a nova lista de viagens e envia
        uma mensagem confirmando a atualização.

    Note:
        - Esta ferramenta substitui completamente a lista de viagens anterior
        - Use quando precisar criar roteiros turísticos, planos de viagem ou itinerários
        - Cada lugar pode incluir informações detalhadas como avaliações e descrições
    """
    return Command(
        update={
            "trips": trips,
            "messages": [
                ToolMessage(
                    f"Lista de viagens atualizada: {trips}",
                    tool_call_id=tool_call_id
                )
            ],
        }
    )
