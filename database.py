import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "qa.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def criar_tabela():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS squads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            squad TEXT,
            produto TEXT,
            testes_necessarios INTEGER,
            testes_automatizados INTEGER,
            data_registro TEXT
        )
    """)

    conn.commit()
    conn.close()


def inserir_dado(squad, produto, necessarios, automatizados):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO squads
        (squad, produto, testes_necessarios, testes_automatizados, data_registro)
        VALUES (?, ?, ?, ?, ?)
    """, (
        squad,
        produto,
        necessarios,
        automatizados,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()


def carregar_dados():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM squads", conn)
    conn.close()
    return df