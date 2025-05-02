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

def reset_admin_password():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verifica se a coluna primeiro_login existe
    c.execute("PRAGMA table_info(usuarios)")
    columns = [column[1] for column in c.fetchall()]
    
    if 'primeiro_login' not in columns:
        # Adiciona a coluna primeiro_login
        c.execute('ALTER TABLE usuarios ADD COLUMN primeiro_login BOOLEAN DEFAULT 0')
        print("Coluna 'primeiro_login' adicionada com sucesso!")
    
    # Verifica se o admin existe
    c.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',))
    admin = c.fetchone()
    
    if not admin:
        # Cria o admin se não existir
        c.execute('INSERT INTO usuarios (username, first_name, password, is_admin) VALUES (?, ?, ?, ?)',
                 ('admin', 'Administrador', generate_password_hash('admin8163'), 1))
        print("Admin criado com sucesso!")
    else:
        # Reseta a senha do admin
        c.execute('UPDATE usuarios SET password = ?, primeiro_login = 0 WHERE username = ?',
                 (generate_password_hash('admin8163'), 'admin'))
        print("Senha do admin resetada com sucesso!")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    reset_admin_password() 