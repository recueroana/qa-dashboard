import sqlite3
import pandas as pd

DB_NAME = "data.db"


def conectar():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        squad TEXT,
        produto TEXT,
        modulos_necessitam_automacao INTEGER DEFAULT 0
    )
    """)
    # in case the table was created previously without the new column, add it
    try:
        cursor.execute("ALTER TABLE produtos ADD COLUMN modulos_necessitam_automacao INTEGER DEFAULT 0")
    except Exception:
        # column already exists, ignore
        pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS modulos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        modulo TEXT,
        testes_necessarios INTEGER,
        testes_automatizados INTEGER,
        FOREIGN KEY(produto_id) REFERENCES produtos(id)
    )
    """)

    conn.commit()
    conn.close()


def inserir_produto(squad, produto, modulos_necessitam_automacao=0):
    conn = conectar()
    cursor = conn.cursor()

    # ensure the quantity is an integer
    try:
        modulos_necessitam_automacao = int(modulos_necessitam_automacao)
    except Exception:
        modulos_necessitam_automacao = 0

    cursor.execute("""
    INSERT INTO produtos (squad, produto, modulos_necessitam_automacao)
    VALUES (?,?,?)
    """, (squad, produto, modulos_necessitam_automacao))

    conn.commit()
    conn.close()


def inserir_modulo(produto_id, modulo, testes_necessarios, testes_automatizados):
    try:
        produto_id = int(produto_id)
    except Exception:
    
        pass

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO modulos (produto_id, modulo, testes_necessarios, testes_automatizados)
    VALUES (?,?,?,?)
    """, (produto_id, modulo, testes_necessarios, testes_automatizados))

    conn.commit()
    conn.close()


def listar_produtos():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM produtos", conn)
    conn.close()
    return df


def listar_modulos():
    conn = conectar()
    df = pd.read_sql("SELECT * FROM modulos", conn)
    conn.close()
    return df