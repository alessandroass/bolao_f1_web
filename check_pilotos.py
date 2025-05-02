import sqlite3
import os

# Caminho do banco de dados
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

# Função auxiliar para gerenciar conexões com o banco de dados
def get_db_connection():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_pilotos():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verifica se a tabela existe
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pilotos'")
    if not c.fetchone():
        # Cria a tabela se não existir
        c.execute('''
            CREATE TABLE pilotos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT UNIQUE NOT NULL
            )
        ''')
        print("Tabela 'pilotos' criada com sucesso!")
    
    # Verifica se existem pilotos
    c.execute('SELECT COUNT(*) FROM pilotos')
    count = c.fetchone()[0]
    if count == 0:
        # Insere os pilotos padrão
        pilotos = [
            "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell", "Charles Leclerc",
            "Lewis Hamilton", "Lando Norris", "Oscar Piastri", "Fernando Alonso", "Lance Stroll",
            "Liam Lawson", "Isack Hadjar", "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg",
            "Gabriel Bortoleto", "Esteban Ocon", "Oliver Bearman", "Carloz Sainz", "Alexander Albon"
        ]
        for piloto in pilotos:
            try:
                c.execute('INSERT INTO pilotos (nome) VALUES (?)', (piloto,))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        print(f"{len(pilotos)} pilotos inseridos com sucesso!")
    
    # Lista os pilotos atuais
    c.execute('SELECT nome FROM pilotos ORDER BY nome')
    pilotos = c.fetchall()
    print("\nPilotos cadastrados:")
    for piloto in pilotos:
        print(f"- {piloto[0]}")
    
    conn.close()

if __name__ == "__main__":
    check_pilotos() 