"""Serviço de banco de dados e persistência."""

import sqlite3
from typing import Optional
from langgraph.checkpoint.sqlite import SqliteSaver

from ..config.settings import Settings


class DatabaseService:
    """Gerencia a conexão e persistência do banco de dados SQLite."""
    
    def __init__(self, settings: Optional[Settings] = None):
        """Inicializa o serviço de banco de dados.
        
        Args:
            settings: Configurações da aplicação. Se None, usa configurações padrão.
        """
        self.settings = settings or Settings()
        self._connection: Optional[sqlite3.Connection] = None
        self._checkpointer: Optional[SqliteSaver] = None
    
    @property
    def connection(self) -> sqlite3.Connection:
        """Retorna a conexão SQLite, criando-a se necessário.
        
        Returns:
            Conexão SQLite ativa.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                self.settings.sqlite_db_name,
                check_same_thread=False
            )
        return self._connection
    
    @property
    def checkpointer(self) -> SqliteSaver:
        """Retorna o checkpointer do LangGraph.
        
        Returns:
            SqliteSaver para persistência de estado.
        """
        if self._checkpointer is None:
            self._checkpointer = SqliteSaver(self.connection)
        return self._checkpointer
    
    def close(self) -> None:
        """Fecha a conexão com o banco de dados."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            self._checkpointer = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
