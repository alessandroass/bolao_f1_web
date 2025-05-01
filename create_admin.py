import sqlite3
from werkzeug.security import generate_password_hash

def create_admin():
    conn = sqlite3.connect('bolao_f1.db')
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