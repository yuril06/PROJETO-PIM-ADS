# conexao com o banco de dados MySQL
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar():
    # le as variaveis de ambiente para nao deixar senha no codigo
    host  = os.getenv('MYSQLHOST')     or os.getenv('DB_HOST', 'localhost')
    user  = os.getenv('MYSQLUSER')     or os.getenv('DB_USER', 'root')
    senha = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD', '')
    banco = os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME', 'cantina_escolar')
    porta = int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306))

    conexao = mysql.connector.connect(
        host=host,
        user=user,
        password=senha,
        database=banco,
        port=porta
    )
    return conexao
