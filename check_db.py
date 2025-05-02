import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

# Função auxiliar para gerenciar conexões com o banco de dados
def get_db_connection():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verifica a estrutura da tabela
    print("Estrutura da tabela usuarios:")
    c.execute("PRAGMA table_info(usuarios)")
    columns = c.fetchall()
    for col in columns:
        print(f"Coluna {col[0]}: {col[1]} ({col[2]})")
    
    # Verifica os dados existentes
    print("\nUsuários cadastrados:")
    c.execute("SELECT * FROM usuarios")
    users = c.fetchall()
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Nome: {user[2]}, Is Admin: {user[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_db() 