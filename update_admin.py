import sqlite3
from werkzeug.security import generate_password_hash

def update_admin():
    conn = sqlite3.connect('bolao_f1.db')
    c = conn.cursor()
    
    try:
        # Atualiza a senha do usuário admin
        c.execute('''UPDATE usuarios 
                    SET password = ?, is_admin = 1
                    WHERE username = ?''',
                 (generate_password_hash('admin8163'), 'admin'))
        conn.commit()
        print("Senha do administrador atualizada com sucesso!")
    except Exception as e:
        print(f"Erro ao atualizar senha do administrador: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_admin() 