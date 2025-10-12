from dotenv import load_dotenv
load_dotenv()

from banco_persistencia import memory_db
from state import AgenteViagemState

from tools import (
    buscar_conteudo_completo_site,
    search,
    add_trips
)

from memorias import (
    store_memory_tool,
    retrieve_memories_tool
)

from prompt import PROMPT_AGENTE_VIAGEM

from langchain_core.messages import RemoveMessage, SystemMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph, START, END

## Atenção se voce utilizar a versão de pré-lançamento (langgraph v 1.0) trocar 'create_react_agent' por 'create_agent'
## e importar de 'from langchain.agents import create_agent'


# LLM configurado para sumarização
summarizer = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)

# Número de mensagens após o qual faremos a sumarização da conversa
LIMITE_MENSAGENS_PARA_SUMARIZACAO = 10

# =================================================================================================================
#                      AGENTE QUE CRIA ITINERÁRIO DE VIAGEM
# =================================================================================================================

agente_viagem = create_react_agent(
    model="gpt-4o-mini",
    tools=[buscar_conteudo_completo_site, search, add_trips, store_memory_tool, retrieve_memories_tool],
    state_schema=AgenteViagemState,
    checkpointer=memory_db,
    prompt=PROMPT_AGENTE_VIAGEM
)


## Nó que é ativado quando precisamos sumarizar as mensagens ao atingir o limite definido.
def summarize_conversation(
        state: AgenteViagemState, config: RunnableConfig
) -> AgenteViagemState:
    """
    Sumariza uma lista de mensagens em um resumo conciso para reduzir o comprimento
    do contexto enquanto preserva informações importantes.
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

    message_content = "\n".join(
        [
            f"{'Usuário' if isinstance(msg, HumanMessage) else 'Assistente'}: {msg.content}"
            for msg in messages
        ]
    )

    summary_response = summarizer.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Por favor, resuma esta conversa:\n\n{message_content}")
    ])

    summary_message = SystemMessage(
        content=f"Resumo da conversa até agora:\n\n{summary_response.content}\n\nContinue a conversa baseado neste resumo."
    )

    # Remover todas as mensagens antigas e manter apenas o resumo + última mensagem do usuário
    remove_messages = [RemoveMessage(id=msg.id) for msg in messages if msg.id is not None]

    return {"messages": [
        *remove_messages,  # desempacotando uma lista dentro de outra
        summary_message,  # Ficará só o SystemMessage com resumo
        messages[-1],  # Última mensagem (sempre HumanMessage nesse fluxo)
    ]}


### Grafo principal:

grafo_principal = StateGraph(state_schema=AgenteViagemState)

grafo_principal.add_node("sumariza_memoria", summarize_conversation)
grafo_principal.add_node("agente_viagem", agente_viagem)

grafo_principal.add_edge(START, "sumariza_memoria")
grafo_principal.add_edge("sumariza_memoria", "agente_viagem")
grafo_principal.add_edge("agente_viagem", END)


workflow = grafo_principal.compile(checkpointer=memory_db)


# Imprimindo o mermaid do grafo:
print("Acessar e colar o código abaixo: https://mermaid.live/edit")
print(workflow.get_graph(xray=True).draw_mermaid())

# Função para formatar e imprimir o stream de forma legível
def print_stream_update(chunk):
    """Formata e imprime atualizações do stream de forma legível."""
    namespace, update_dict = chunk

    # Determinar qual nó está executando
    if namespace:
        if isinstance(namespace, tuple) and namespace:
            node_name = namespace[0].split(':')[0] if ':' in namespace[0] else namespace[0]
        else:
            node_name = "desconhecido"
    else:
        # Namespace vazio significa nó do grafo principal
        node_name = list(update_dict.keys())[0] if update_dict else "grafo_principal"

    print(f"\n{'='*80}")
    print(f"🔹 NÓ: {node_name}")
    print('='*80)

    # Processar mensagens se existirem
    for key, value in update_dict.items():
        if isinstance(value, dict) and "messages" in value:
            messages = value["messages"]

            for msg in messages:
                msg_type = type(msg).__name__

                if msg_type == "HumanMessage":
                    print(f"\n👤 USUÁRIO:")
                    print(f"   {msg.content}")

                elif msg_type == "AIMessage":
                    if msg.tool_calls:
                        print(f"\n🤖 ASSISTENTE (chamando ferramentas):")
                        for tool_call in msg.tool_calls:
                            print(f"   🔧 {tool_call['name']}")
                            print(f"      Args: {tool_call['args']}")
                    elif msg.content:
                        print(f"\n🤖 ASSISTENTE:")
                        # Truncar conteúdo muito longo
                        content = msg.content
                        print(f"   {content}")

                elif msg_type == "ToolMessage":
                    print(f"\n🔧 RESULTADO DA FERRAMENTA ({msg.name}):")
                    content = msg.content
                    print(f"   {content}")

                elif msg_type == "SystemMessage":
                    print(f"\n⚙️  SISTEMA:")
                    content = msg.content
                    print(f"   {content}")

        # Processar trips se existirem
        if key == "trips" or (isinstance(value, dict) and "trips" in value):
            trips = value.get("trips") if isinstance(value, dict) else value
            if trips:
                print(f"\n✈️  ITINERÁRIOS CRIADOS:")
                for trip in trips:
                    print(f"\n   📋 {trip.get('name', 'Sem nome')}")
                    print(f"   ID: {trip.get('id', 'N/A')}")
                    print(f"   Lugares ({len(trip.get('places', []))}):")

                    for idx, place in enumerate(trip.get('places', []), 1):
                        print(f"      {idx}. {place.get('name', 'Sem nome')}")
                        print(f"         📍 {place.get('address', 'Sem endereço')}")
                        print(f"         ⭐ {place.get('rating', 'N/A')}")
                        if place.get('description'):
                            desc = place['description']
                            print(f"         ℹ️  {desc}")


# Visualizar grafo
if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    configuracao = {"configurable": {"thread_id": "conversa_1", "user_id": "Gustavo"}}

    print("\n" + "=" * 40)
    print("INICIANDO AGENTE DE VIAGENS")
    print("🚀" * 40)
    pergunta = "Olá. Queria montar uma viagem para India. me ajude?"
    # pergunta = "21 dias. Gosto de museu, templos, parque e restaurante. Orçamento de até 2000 dolares.Nunca fui para a india"


    # pergunta = "O que te perguntei até agora?"
    # pergunta = "O que voce conhece de mim?"
    for chunk in workflow.stream(
            {"messages": [HumanMessage(content=pergunta)]},
            config = configuracao,
            subgraphs=True,
            stream_mode="updates",
    ):
        print_stream_update(chunk)

    print("\n" + "*" * 40)
    print("CONVERSA FINALIZADA")
    print("*" * 40 + "\n")
