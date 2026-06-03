import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def conectar():
    host  = os.getenv('MYSQLHOST')     or os.getenv('DB_HOST', 'localhost')
    user  = os.getenv('MYSQLUSER')     or os.getenv('DB_USER', 'root')
    senha = os.getenv('MYSQLPASSWORD') or os.getenv('DB_PASSWORD', '')
    banco = os.getenv('MYSQLDATABASE') or os.getenv('DB_NAME', 'cantina_escolar')
    porta = int(os.getenv('MYSQLPORT') or os.getenv('DB_PORT', 3306))

    return mysql.connector.connect(
        host=host, user=user, password=senha, database=banco, port=porta
    )
