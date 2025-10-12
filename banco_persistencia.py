import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver

conn = sqlite3.connect("memorias_agente.sqlite", check_same_thread=False)
memory_db = SqliteSaver(conn)
