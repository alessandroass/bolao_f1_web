import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho do banco de dados no Render
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

def create_tables():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Verifica se a tabela usuarios existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='usuarios'")
        if not c.fetchone():
            # Cria a tabela de usuários
            c.execute('''CREATE TABLE usuarios
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          username TEXT UNIQUE NOT NULL,
                          first_name TEXT NOT NULL,
                          password TEXT NOT NULL,
                          is_admin BOOLEAN DEFAULT 0,
                          primeiro_login BOOLEAN DEFAULT 1)''')
            print("Tabela usuarios criada")
        
        # Verifica se a tabela pilotos existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pilotos'")
        if not c.fetchone():
            # Cria a tabela de pilotos
            c.execute('''CREATE TABLE pilotos
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          nome TEXT UNIQUE NOT NULL)''')
            print("Tabela pilotos criada")
            
            # Insere os pilotos iniciais
            pilotos_iniciais = [
                "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
                "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
                "Fernando Alonso", "Lance Stroll", "Liam Lawson", "Isack Hadjar",
                "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg", "Gabriel Bortoleto",
                "Esteban Ocon", "Oliver Bearman", "Carlos Sainz", "Alexander Albon"
            ]
            for piloto in pilotos_iniciais:
                c.execute('INSERT OR IGNORE INTO pilotos (nome) VALUES (?)', (piloto,))
        
        # Verifica se a tabela palpites existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='palpites'")
        if not c.fetchone():
            # Cria a tabela de palpites
            c.execute('''CREATE TABLE palpites
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          usuario_id INTEGER NOT NULL,
                          gp_slug TEXT NOT NULL,
                          pos_1 TEXT,
                          pos_2 TEXT,
                          pos_3 TEXT,
                          pos_4 TEXT,
                          pos_5 TEXT,
                          pos_6 TEXT,
                          pos_7 TEXT,
                          pos_8 TEXT,
                          pos_9 TEXT,
                          pos_10 TEXT,
                          pole TEXT,
                          FOREIGN KEY (usuario_id) REFERENCES usuarios (id),
                          UNIQUE(usuario_id, gp_slug))''')
            print("Tabela palpites criada")
        
        # Verifica se a tabela respostas existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='respostas'")
        if not c.fetchone():
            # Cria a tabela de respostas
            c.execute('''CREATE TABLE respostas
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          gp_slug TEXT UNIQUE NOT NULL,
                          pos_1 TEXT,
                          pos_2 TEXT,
                          pos_3 TEXT,
                          pos_4 TEXT,
                          pos_5 TEXT,
                          pos_6 TEXT,
                          pos_7 TEXT,
                          pos_8 TEXT,
                          pos_9 TEXT,
                          pos_10 TEXT,
                          pole TEXT)''')
            print("Tabela respostas criada")
        
        # Verifica se a tabela pontuacao existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pontuacao'")
        if not c.fetchone():
            # Cria a tabela de pontuação
            c.execute('''CREATE TABLE pontuacao
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          posicao INTEGER UNIQUE NOT NULL,
                          pontos INTEGER NOT NULL)''')
            print("Tabela pontuacao criada")
            
            # Insere valores padrão de pontuação
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
            c.executemany('INSERT OR IGNORE INTO pontuacao (posicao, pontos) VALUES (?, ?)', valores_padrao)
        
        # Verifica se a tabela config_votacao existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='config_votacao'")
        if not c.fetchone():
            # Cria a tabela de configuração de votação
            c.execute('''CREATE TABLE config_votacao
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          gp_slug TEXT UNIQUE NOT NULL,
                          pole_habilitado BOOLEAN DEFAULT 1,
                          posicoes_habilitado BOOLEAN DEFAULT 1)''')
            print("Tabela config_votacao criada")
        
        # Verifica se a tabela gps existe
        c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gps'")
        if not c.fetchone():
            # Cria a tabela de GPs
            c.execute('''CREATE TABLE gps
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          slug TEXT UNIQUE NOT NULL,
                          nome TEXT NOT NULL,
                          data_corrida TEXT NOT NULL,
                          hora_corrida TEXT NOT NULL,
                          data_classificacao TEXT NOT NULL,
                          hora_classificacao TEXT NOT NULL)''')
            print("Tabela gps criada")
        
        conn.commit()
        print("Tabelas verificadas com sucesso!")
    except Exception as e:
        print(f"Erro ao verificar/criar tabelas: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables() 