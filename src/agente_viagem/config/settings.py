"""Configurações da aplicação carregadas de variáveis de ambiente."""

import os
from typing import Optional
from dotenv import load_dotenv

from .constants import (
    DEFAULT_QDRANT_URL,
    DEFAULT_QDRANT_REST_PORT,
    DEFAULT_QDRANT_GRPC_PORT,
    DEFAULT_SQLITE_DB_NAME,
)


class Settings:
    """Classe de configuração centralizada."""

    def __init__(self, env_file: str = ".env"):
        """Inicializa as configurações carregando variáveis de ambiente.
        
        Args:
            env_file: Caminho para o arquivo .env (padrão: ".env")
        """
        load_dotenv(env_file)
        
        # API Keys
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        self.qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
        
        # Qdrant Configuration
        self.qdrant_url: str = os.getenv("QDRANT_URL", DEFAULT_QDRANT_URL)
        self.qdrant_rest_port: int = int(
            os.getenv("QDRANT_REST_PORT", str(DEFAULT_QDRANT_REST_PORT))
        )
        self.qdrant_grpc_port: int = int(
            os.getenv("QDRANT_GRPC_PORT", str(DEFAULT_QDRANT_GRPC_PORT))
        )
        
        # Database Configuration
        self.sqlite_db_name: str = os.getenv("SQLITE_DB_NAME", DEFAULT_SQLITE_DB_NAME)
        
    def validate(self) -> None:
        """Valida se as configurações obrigatórias estão presentes.
        
        Raises:
            ValueError: Se alguma configuração obrigatória estiver ausente.
        """
        if not self.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY não encontrada. "
                "Configure no arquivo .env ou como variável de ambiente."
            )
    
    @property
    def is_valid(self) -> bool:
        """Verifica se as configurações são válidas.
        
        Returns:
            bool: True se as configurações são válidas, False caso contrário.
        """
        try:
            self.validate()
            return True
        except ValueError:
            return False
