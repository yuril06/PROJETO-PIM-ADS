# ============================================================
# Módulo: db.py
# Responsabilidade: Conexão com o banco de dados MySQL
# ============================================================

import mysql.connector   # Biblioteca para conectar ao MySQL
import os                # Biblioteca para ler variáveis de ambiente
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()


def conectar():
    """
    Cria e retorna uma conexão com o banco de dados MySQL.

    As credenciais são lidas das variáveis de ambiente (.env),
    o que evita expor senhas diretamente no código.

    Retorna:
        conexao: objeto de conexão com o banco MySQL
    """
    # Variáveis com os dados de acesso ao banco
    host     = os.getenv('DB_HOST', 'localhost')
    usuario  = os.getenv('DB_USER', 'root')
    senha    = os.getenv('DB_PASSWORD', '')
    banco    = os.getenv('DB_NAME', 'cantina_escolar')

    # Cria e retorna a conexão
    conexao = mysql.connector.connect(
        host=host,
        user=usuario,
        password=senha,
        database=banco
    )

    return conexao
