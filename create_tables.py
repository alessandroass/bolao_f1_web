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
        # Cria a tabela de usuários
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      first_name TEXT NOT NULL,
                      password TEXT NOT NULL,
                      is_admin BOOLEAN DEFAULT 0,
                      primeiro_login BOOLEAN DEFAULT 1)''')
        
        # Cria a tabela de pilotos
        c.execute('''CREATE TABLE IF NOT EXISTS pilotos
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      nome TEXT UNIQUE NOT NULL)''')
        
        # Cria a tabela de palpites
        c.execute('''CREATE TABLE IF NOT EXISTS palpites
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
        
        # Cria a tabela de respostas
        c.execute('''CREATE TABLE IF NOT EXISTS respostas
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
        
        # Cria a tabela de pontuação
        c.execute('''CREATE TABLE IF NOT EXISTS pontuacao
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      posicao INTEGER UNIQUE NOT NULL,
                      pontos INTEGER NOT NULL)''')
        
        # Cria a tabela de configuração de votação
        c.execute('''CREATE TABLE IF NOT EXISTS config_votacao
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      gp_slug TEXT UNIQUE NOT NULL,
                      pole_habilitado BOOLEAN DEFAULT 1,
                      posicoes_habilitado BOOLEAN DEFAULT 1)''')
        
        # Cria a tabela de GPs
        c.execute('''CREATE TABLE IF NOT EXISTS gps
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      slug TEXT UNIQUE NOT NULL,
                      nome TEXT NOT NULL,
                      data_corrida TEXT NOT NULL,
                      hora_corrida TEXT NOT NULL,
                      data_classificacao TEXT NOT NULL,
                      hora_classificacao TEXT NOT NULL)''')
        
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"Erro ao criar tabelas: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_tables() 