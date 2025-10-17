"""Ponto de entrada principal da aplicação."""

from langchain_core.messages import HumanMessage

from src.agente_viagem.agents import TravelAgent
from src.agente_viagem.config import Settings
from src.agente_viagem.utils import print_stream_update


def main():
    """Função principal da aplicação."""
    # Inicializa configurações
    settings = Settings()
    
    try:
        settings.validate()
    except ValueError as e:
        print(f"❌ Erro de configuração: {e}")
        print("Por favor, configure as variáveis de ambiente no arquivo .env")
        return
    
    # Cria o agente
    with TravelAgent(settings) as agent:
        # Imprime diagrama do grafo
        print("\n" + "="*80)
        print("DIAGRAMA DO WORKFLOW")
        print("="*80)
        print("Acessar e colar o código abaixo: https://mermaid.live/edit")
        print(agent.get_graph_mermaid())
        print("="*80 + "\n")
        
        # Configuração da conversa
        configuracao = {
            "configurable": {
                "thread_id": "conversa_1",  # ID da thread (persiste conversa)
                "user_id": "Gustavo"         # ID do usuário (filtra memórias)
            }
        }
        
        print("\n" + "=" * 80)
        print("INICIANDO AGENTE DE VIAGENS")
        print("=" * 80)
        
        # Pergunta do usuário
        pergunta = "Olá. Queria montar uma viagem para India. me ajude?"
        
        print(f"\n📝 Pergunta: {pergunta}\n")
        
        # Executa o workflow
        for chunk in agent.workflow.stream(
            {"messages": [HumanMessage(content=pergunta)]},
            config=configuracao,
            subgraphs=True,
            stream_mode="updates",
        ):
            print_stream_update(chunk)
        
        print("\n" + "*" * 80)
        print("CONVERSA FINALIZADA")
        print("*" * 80 + "\n")


if __name__ == "__main__":
    main()
