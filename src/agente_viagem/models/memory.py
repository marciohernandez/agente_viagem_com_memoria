"""Modelo de memória do sistema."""

from typing import Literal
from pydantic import BaseModel


class Memory(BaseModel):
    """Representa uma memória de longo prazo.

    EPISODIC: Experiências pessoais e preferências específicas do usuário.
              Exemplo: "Usuário prefere companhias aéreas Delta", 
                       "Usuário visitou Paris ano passado"

    SEMANTIC: Conhecimento geral de domínio e fatos.
              Exemplo: "Singapura requer passaporte", 
                       "Tóquio tem excelente transporte público"
    
    Attributes:
        content: Conteúdo da memória
        memory_type: Tipo da memória (episodic ou semantic)
    """
    content: str
    memory_type: Literal["episodic", "semantic"]
