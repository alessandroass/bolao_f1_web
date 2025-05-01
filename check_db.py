import sqlite3

def check_db():
    conn = sqlite3.connect('bolao_f1.db')
    c = conn.cursor()
    
    # Verifica a estrutura da tabela
    print("Estrutura da tabela usuarios:")
    c.execute("PRAGMA table_info(usuarios)")
    columns = c.fetchall()
    for col in columns:
        print(f"Coluna {col[0]}: {col[1]} ({col[2]})")
    
    # Verifica os dados existentes
    print("\nUsuários cadastrados:")
    c.execute("SELECT * FROM usuarios")
    users = c.fetchall()
    for user in users:
        print(f"ID: {user[0]}, Username: {user[1]}, Nome: {user[2]}, Is Admin: {user[4]}")
    
    conn.close()

if __name__ == '__main__':
    check_db() 