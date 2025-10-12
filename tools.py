from dotenv import  load_dotenv
load_dotenv()

from typing import Annotated, List
import httpx
from markdownify import markdownify

from state import Trip

from langchain_core.tools import tool, InjectedToolCallId
from langchain_core.messages import ToolMessage
from langchain_community.tools import DuckDuckGoSearchResults

from langgraph.types import Command


# =================================================================================================================
#                      TOOL RESPONSÁVEL POR PEGAR O CONTEÚDO DO SITE EM FORMATO MD
# =================================================================================================================

@tool
def buscar_conteudo_completo_site(url: Annotated[str, "url do site que deseja obter o conteúdo em formato markdown"]):
    """Extrai e converte o conteúdo completo de uma página web para o formato markdown.

    Esta ferramenta realiza uma requisição HTTP para obter o HTML de uma URL e converte
    todo o conteúdo para markdown, facilitando a leitura e processamento de textos de sites,
    artigos, documentações e outras páginas web.

    Args:
        url: URL completa da página web que deseja extrair o conteúdo (deve incluir http:// ou https://).

    Returns:
        String contendo o conteúdo da página convertido para markdown, ou mensagem de erro
        caso a requisição falhe (timeout, página não encontrada, erro de conexão, etc.).

    Note:
        - Utiliza um timeout de 10 segundos para evitar travamentos em sites lentos
        - Ideal para extrair conteúdo de artigos, blogs, documentações e páginas informativas
        - Não executa JavaScript, apenas extrai o HTML estático da página
    """
    try:
        with httpx.Client(timeout=10.0) as cli:
            response = cli.get(url)
            response.raise_for_status()
            return markdownify(response.text)
    except Exception as e:
        print(f"Aviso: Falha ao buscar o conteúdo completo da página para {url}: {str(e)}")
        return f"Aviso: Falha ao buscar o conteúdo completo da página para {url}: {str(e)}"


# =================================================================================================================
#                      TOOL RESPONSÁVEL POR PESQUISAR NA WEB
# =================================================================================================================

search = DuckDuckGoSearchResults(output_format="list")

# =================================================================================================================
#                      TOOL RESPONSÁVEL POR MONTAR UM ITINERÁRIO
# =================================================================================================================

@tool
def add_trips(trips: List[Trip], tool_call_id: Annotated[str, InjectedToolCallId]):
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
                ToolMessage(f"Lista de viagens atualizada: {trips}", tool_call_id=tool_call_id)
            ],
        }
    )

