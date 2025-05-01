import sqlite3

def check_pilotos():
    conn = sqlite3.connect('bolao_f1.db')
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

if __name__ == '__main__':
    check_pilotos() 