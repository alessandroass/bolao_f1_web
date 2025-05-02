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

def add_admin_column():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Adiciona a coluna is_admin se ela não existir
        c.execute("ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("Coluna is_admin adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("A coluna is_admin já existe!")
        else:
            print(f"Erro ao adicionar coluna: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_admin_column() 