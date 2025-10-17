"""Ferramentas para busca e extração de conteúdo web."""

from typing import Annotated
import httpx
from markdownify import markdownify
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

from ..config.constants import HTTP_TIMEOUT_SECONDS


@tool
def buscar_conteudo_completo_site(
    url: Annotated[str, "URL do site que deseja obter o conteúdo em formato markdown"]
):
    """Extrai e converte o conteúdo completo de uma página web para o formato markdown.

    Esta ferramenta realiza uma requisição HTTP para obter o HTML de uma URL e converte
    todo o conteúdo para markdown, facilitando a leitura e processamento de textos de sites,
    artigos, documentações e outras páginas web.

    Args:
        url: URL completa da página web que deseja extrair o conteúdo 
             (deve incluir http:// ou https://).

    Returns:
        String contendo o conteúdo da página convertido para markdown, ou mensagem de erro
        caso a requisição falhe (timeout, página não encontrada, erro de conexão, etc.).

    Note:
        - Utiliza um timeout de 10 segundos para evitar travamentos em sites lentos
        - Ideal para extrair conteúdo de artigos, blogs, documentações e páginas informativas
        - Não executa JavaScript, apenas extrai o HTML estático da página
    """
    try:
        with httpx.Client(timeout=HTTP_TIMEOUT_SECONDS) as cli:
            response = cli.get(url)
            response.raise_for_status()
            return markdownify(response.text)
    except Exception as e:
        error_msg = f"Aviso: Falha ao buscar o conteúdo completo da página para {url}: {str(e)}"
        print(error_msg)
        return error_msg


# Ferramenta de busca na web usando DuckDuckGo
search = DuckDuckGoSearchResults(output_format="list")
