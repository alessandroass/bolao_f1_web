import sqlite3

def make_admin(username):
    conn = sqlite3.connect('bolao_f1.db')
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
    username = input("Digite o nome de usuário que deseja tornar administrador: ")
    make_admin(username) 