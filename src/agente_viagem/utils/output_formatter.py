"""Formatadores de saída para o console."""


def print_stream_update(chunk):
    """Formata e imprime atualizações do stream de forma legível.
    
    Args:
        chunk: Tupla (namespace, update_dict) do stream do workflow
    """
    namespace, update_dict = chunk
    
    # Determinar qual nó está executando
    if namespace:
        if isinstance(namespace, tuple) and namespace:
            node_name = (
                namespace[0].split(':')[0] 
                if ':' in namespace[0] 
                else namespace[0]
            )
        else:
            node_name = "desconhecido"
    else:
        # Namespace vazio significa nó do grafo principal
        node_name = (
            list(update_dict.keys())[0] 
            if update_dict 
            else "grafo_principal"
        )
    
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
                        print(f"   {msg.content}")
                
                elif msg_type == "ToolMessage":
                    print(f"\n🔧 RESULTADO DA FERRAMENTA ({msg.name}):")
                    print(f"   {msg.content}")
                
                elif msg_type == "SystemMessage":
                    print(f"\n⚙️  SISTEMA:")
                    print(f"   {msg.content}")
        
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
