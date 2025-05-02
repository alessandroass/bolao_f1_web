import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho do banco de dados no Render
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

def reset_admin_password():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Verifica se o admin existe
        c.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',))
        admin = c.fetchone()
        
        if not admin:
            # Cria o admin se não existir
            c.execute('''INSERT INTO usuarios 
                        (username, first_name, password, is_admin, primeiro_login) 
                        VALUES (?, ?, ?, ?, ?)''',
                     ('admin', 'Administrador', 
                      generate_password_hash('admin8163'), 
                      1, 0))
            print("Admin criado com sucesso!")
        else:
            # Reseta a senha do admin sem afetar outros dados
            c.execute('''UPDATE usuarios 
                        SET password = ?, primeiro_login = 0 
                        WHERE username = ? AND id = ?''',
                     (generate_password_hash('admin8163'), 'admin', admin[0]))
            print("Senha do admin resetada com sucesso!")
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao resetar senha do admin: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    reset_admin_password() 