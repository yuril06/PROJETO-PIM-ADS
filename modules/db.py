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
    # Lê credenciais — compatível com Railway (MYSQLHOST) e .env local (DB_HOST)
    host     = os.getenv('MYSQLHOST')     or os.getenv('DB_HOST', 'localhost')
    usuario  = os.getenv('MYSQLUSER')     or os.getenv('DB_USER', 'root')
    senha    = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD', '')
    banco    = os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME', 'cantina_escolar')
    porta    = int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306))

    # Cria e retorna a conexão
    conexao = mysql.connector.connect(
        host=host,
        user=usuario,
        password=senha,
        database=banco,
        port=porta
    )

    return conexao
