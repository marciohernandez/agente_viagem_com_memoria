"""Agente de viagem com memória e planejamento de itinerários."""

from typing import Optional
from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END, CompiledGraph

from ..config.settings import Settings
from ..config.constants import LIMITE_MENSAGENS_PARA_SUMARIZACAO, OPENAI_MODEL
from ..models.state import AgenteViagemState
from ..services.database import DatabaseService
from ..tools import (
    buscar_conteudo_completo_site,
    search,
    add_trips,
    store_memory_tool,
    retrieve_memories_tool,
)
from .prompts import PROMPT_AGENTE_VIAGEM


class TravelAgent:
    """Agente de viagem com capacidade de memória e planejamento."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Inicializa o agente de viagem.
        
        Args:
            settings: Configurações da aplicação. Se None, usa configurações padrão.
        """
        self.settings = settings or Settings()
        self.settings.validate()
        
        # Inicializa serviços
        self.db_service = DatabaseService(self.settings)
        
        # LLM para sumarização
        self.summarizer = ChatOpenAI(model=OPENAI_MODEL, temperature=0.3)
        
        # Cria o workflow
        self._workflow: Optional[CompiledGraph] = None
    
    def _create_react_agent(self):
        """Cria o agente ReACT com ferramentas.
        
        Returns:
            Agente ReACT configurado.
        """
        return create_react_agent(
            model=OPENAI_MODEL,
            tools=[
                buscar_conteudo_completo_site,
                search,
                add_trips,
                store_memory_tool,
                retrieve_memories_tool
            ],
            state_schema=AgenteViagemState,
            checkpointer=self.db_service.checkpointer,
            prompt=PROMPT_AGENTE_VIAGEM
        )
    
    def _summarize_conversation(
        self,
        state: AgenteViagemState,
        config: RunnableConfig
    ) -> AgenteViagemState:
        """Sumariza a conversa quando atinge o limite de mensagens.
        
        Args:
            state: Estado atual do agente
            config: Configuração de execução
            
        Returns:
            Estado atualizado com conversa sumarizada
        """
        messages = state["messages"]
        
        if len(messages) < LIMITE_MENSAGENS_PARA_SUMARIZACAO:
            return state
        
        print(">>>> Nó de sumarização ativado!")
        
        system_prompt = """
        Você é um sumarizador de conversas. Crie um resumo conciso da conversa anterior
        entre o usuário e o assistente.

        O resumo deve:
        1. Destacar tópicos principais, preferências e decisões tomadas
        2. Incluir quaisquer detalhes específicos mencionados
        3. Anotar quaisquer perguntas pendentes ou tópicos que precisam de acompanhamento
        4. Ser conciso mas informativo

        Formate seu resumo como um parágrafo narrativo breve.
        """
        
        message_content = "\n".join([
            f"{'Usuário' if isinstance(msg, HumanMessage) else 'Assistente'}: {msg.content}"
            for msg in messages
        ])
        
        summary_response = self.summarizer.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=f"Por favor, resuma esta conversa:\n\n{message_content}"
            )
        ])
        
        summary_message = SystemMessage(
            content=(
                f"Resumo da conversa até agora:\n\n{summary_response.content}\n\n"
                "Continue a conversa baseado neste resumo."
            )
        )
        
        # Remover mensagens antigas e manter apenas resumo + última mensagem
        remove_messages = [
            RemoveMessage(id=msg.id)
            for msg in messages
            if msg.id is not None
        ]
        
        return {
            "messages": [
                *remove_messages,
                summary_message,
                messages[-1],  # Última mensagem do usuário
            ]
        }
    
    def build_workflow(self) -> CompiledGraph:
        """Constrói o workflow do agente.
        
        Returns:
            Workflow compilado pronto para uso.
        """
        # Cria o agente ReACT
        agente_viagem = self._create_react_agent()
        
        # Cria o grafo principal
        grafo_principal = StateGraph(state_schema=AgenteViagemState)
        
        # Adiciona nós
        grafo_principal.add_node("sumariza_memoria", self._summarize_conversation)
        grafo_principal.add_node("agente_viagem", agente_viagem)
        
        # Define arestas
        grafo_principal.add_edge(START, "sumariza_memoria")
        grafo_principal.add_edge("sumariza_memoria", "agente_viagem")
        grafo_principal.add_edge("agente_viagem", END)
        
        # Compila o workflow
        self._workflow = grafo_principal.compile(
            checkpointer=self.db_service.checkpointer
        )
        
        return self._workflow
    
    @property
    def workflow(self) -> CompiledGraph:
        """Retorna o workflow, construindo-o se necessário.
        
        Returns:
            Workflow compilado.
        """
        if self._workflow is None:
            self._workflow = self.build_workflow()
        return self._workflow
    
    def get_graph_mermaid(self) -> str:
        """Retorna o diagrama Mermaid do grafo.
        
        Returns:
            String com o código Mermaid do grafo.
        """
        return self.workflow.get_graph(xray=True).draw_mermaid()
    
    def close(self) -> None:
        """Fecha recursos do agente."""
        self.db_service.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
