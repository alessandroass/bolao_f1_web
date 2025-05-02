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

def make_admin(username):
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute("UPDATE usuarios SET is_admin = 1 WHERE username = ?", (username,))
        conn.commit()
        print(f"Usuário {username} agora é administrador!")
    except sqlite3.Error as e:
        print(f"Erro ao atualizar usuário: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python make_admin.py <username>")
        sys.exit(1)
    make_admin(sys.argv[1]) 