import sqlite3

def add_admin_column():
    conn = sqlite3.connect('bolao_f1.db')
    c = conn.cursor()
    
    try:
        # Adiciona a coluna is_admin se ela não existir
        c.execute("ALTER TABLE usuarios ADD COLUMN is_admin BOOLEAN DEFAULT 0")
        conn.commit()
        print("Coluna is_admin adicionada com sucesso!")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print("A coluna is_admin já existe!")
        else:
            print(f"Erro ao adicionar coluna: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_admin_column() 