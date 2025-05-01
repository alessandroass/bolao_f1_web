import sqlite3
from werkzeug.security import check_password_hash

def test_admin_login():
    conn = sqlite3.connect('bolao_f1.db')
    c = conn.cursor()
    
    # Busca o admin
    c.execute('SELECT * FROM usuarios WHERE username = ?', ('admin',))
    admin = c.fetchone()
    
    if admin:
        print(f"Admin encontrado:")
        print(f"ID: {admin[0]}")
        print(f"Username: {admin[1]}")
        print(f"Nome: {admin[2]}")
        print(f"Is Admin: {admin[4]}")
        print(f"Primeiro Login: {admin[5]}")
        
        # Testa a senha
        senha_teste = 'admin8163'
        if check_password_hash(admin[3], senha_teste):
            print("\nSenha está correta!")
        else:
            print("\nSenha está incorreta!")
    else:
        print("Admin não encontrado!")
    
    conn.close()

if __name__ == '__main__':
    test_admin_login() 