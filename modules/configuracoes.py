# gerencia configuracoes do sistema salvas no banco
from modules.db import conectar
import os


def criar_tabela_configuracoes():
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS configuracoes (
                chave   VARCHAR(50) PRIMARY KEY,
                valor   VARCHAR(255) NOT NULL
            )
        """)
        conexao.commit()
        cursor.close()
        conexao.close()
    except Exception as erro:
        print(f"Erro ao criar tabela configuracoes: {erro}")


def get_config(chave, padrao=''):
    try:
        conexao = conectar()
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT valor FROM configuracoes WHERE chave = %s", (chave,))
        row = cursor.fetchone()
        cursor.close()
        conexao.close()
        return row['valor'] if row else padrao
    except Exception:
        return padrao


def set_config(chave, valor):
    try:
        conexao = conectar()
        cursor = conexao.cursor()
        cursor.execute("""
            INSERT INTO configuracoes (chave, valor) VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE valor = %s
        """, (chave, valor, valor))
        conexao.commit()
        cursor.close()
        conexao.close()
        return True
    except Exception as erro:
        print(f"Erro ao salvar configuracao: {erro}")
        return False


def get_email_destinatario():
    # le do banco, cai no env como fallback
    email = get_config('email_destinatario')
    if not email:
        email = os.getenv('EMAIL_DESTINATARIO', '')
    return email
