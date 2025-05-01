import sqlite3

def add_pontuacao_table():
    conn = sqlite3.connect('bolao_f1.db')
    c = conn.cursor()
    
    try:
        # Cria a tabela de pontuação
        c.execute('''CREATE TABLE IF NOT EXISTS pontuacao
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     posicao INTEGER UNIQUE NOT NULL,
                     pontos INTEGER NOT NULL)''')
        
        # Insere os valores padrão
        valores_padrao = [
            (0, 5),   # Pole Position
            (1, 25),  # 1º lugar
            (2, 18),  # 2º lugar
            (3, 15),  # 3º lugar
            (4, 12),  # 4º lugar
            (5, 10),  # 5º lugar
            (6, 8),   # 6º lugar
            (7, 6),   # 7º lugar
            (8, 4),   # 8º lugar
            (9, 2),   # 9º lugar
            (10, 1)   # 10º lugar
        ]
        
        c.execute('SELECT COUNT(*) FROM pontuacao')
        if c.fetchone()[0] == 0:
            c.executemany('INSERT INTO pontuacao (posicao, pontos) VALUES (?, ?)', valores_padrao)
            print("Tabela de pontuação criada e valores padrão inseridos!")
        else:
            print("Tabela de pontuação já existe!")
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela de pontuação: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_pontuacao_table() 