import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho do banco de dados
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

# Função auxiliar para gerenciar conexões com o banco de dados
def get_db_connection():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def create_admin():
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        # Verifica se o usuário admin já existe
        c.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',))
        if c.fetchone() is None:
            # Insere o usuário admin
            c.execute('''INSERT INTO usuarios 
                        (username, first_name, password, is_admin) 
                        VALUES (?, ?, ?, ?)''',
                     ('admin', 'Administrador', 
                      generate_password_hash('admin8163'), 
                      1))
            conn.commit()
            print("Usuário administrador criado com sucesso!")
        else:
            print("Usuário administrador já existe!")
    except Exception as e:
        print(f"Erro ao criar usuário administrador: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_admin() 