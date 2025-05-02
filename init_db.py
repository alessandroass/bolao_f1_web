import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho do banco de dados no Render
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

def init_database():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Cria a tabela de usuários se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      first_name TEXT NOT NULL,
                      password TEXT NOT NULL,
                      is_admin BOOLEAN DEFAULT 0,
                      primeiro_login BOOLEAN DEFAULT 1)''')
        
        # Verifica se o admin existe
        c.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',))
        if c.fetchone() is None:
            # Cria o usuário admin
            c.execute('''INSERT INTO usuarios 
                        (username, first_name, password, is_admin, primeiro_login) 
                        VALUES (?, ?, ?, ?, ?)''',
                     ('admin', 'Administrador', 
                      generate_password_hash('admin8163'), 
                      1, 0))
            print("Usuário administrador criado com sucesso!")
        else:
            print("Usuário administrador já existe!")
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 