import sqlite3
import os
from werkzeug.security import generate_password_hash

# Caminho do banco de dados no Render
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

# Lista dos GPs (nome da rota, nome para exibição, data da corrida, hora da corrida, data da classificação, hora da classificação)
gps_2025 = [
    ("australia", "🇦🇺 Austrália (Melbourne)", "16/03/2025", "01:00", "15/03/2025", "02:00"),
    ("china", "🇨🇳 China (Xangai)", "23/03/2025", "04:00", "22/03/2025", "04:00"),
    ("japao", "🇯🇵 Japão (Suzuka)", "06/04/2025", "02:00", "05/04/2025", "03:00"),
    ("bahrein", "🇧🇭 Bahrein (Sakhir)", "13/04/2025", "12:00", "12/04/2025", "13:00"),
    ("arabia-saudita", "🇸🇦 Arábia Saudita (Jeddah)", "20/04/2025", "14:00", "19/04/2025", "14:00"),
    ("miami", "🇺🇸 Miami (EUA)", "04/05/2025", "17:00", "03/05/2025", "17:00"),
    ("emilia-romagna", "🇮🇹 Emilia-Romagna (Imola)", "18/05/2025", "10:00", "17/05/2025", "11:00"),
    ("monaco", "🇲🇨 Mônaco (Monte Carlo)", "25/05/2025", "10:00", "24/05/2025", "11:00"),
    ("espanha", "🇪🇸 Espanha (Barcelona)", "22/06/2025", "10:00", "21/06/2025", "11:00"),
    ("canada", "🇨🇦 Canadá (Montreal)", "15/06/2025", "15:00", "14/06/2025", "17:00"),
    ("austria", "🇦🇹 Áustria (Spielberg)", "29/06/2025", "10:00", "28/06/2025", "11:00"),
    ("reino-unido", "🇬🇧 Reino Unido (Silverstone)", "06/07/2025", "11:00", "05/07/2025", "11:00"),
    ("belgica", "🇧🇪 Bélgica (Spa-Francorchamps)", "27/07/2025", "10:00", "26/07/2025", "11:00"),
    ("hungria", "🇭🇺 Hungria (Budapeste)", "03/08/2025", "10:00", "02/08/2025", "11:00"),
    ("paises-baixos", "🇳🇱 Holanda (Zandvoort)", "31/08/2025", "10:00", "30/08/2025", "10:00"),
    ("monza", "🇮🇹 Itália (Monza)", "07/09/2025", "10:00", "06/09/2025", "11:00"),
    ("azerbaijao", "🇦🇿 Azerbaijão (Baku)", "21/09/2025", "08:00", "20/09/2025", "09:00"),
    ("singapura", "🇸🇬 Singapura (Marina Bay)", "05/10/2025", "09:00", "04/10/2025", "10:00"),
    ("austin", "🇺🇸 EUA (Austin)", "19/10/2025", "16:00", "18/10/2025", "15:00"),
    ("mexico", "🇲🇽 México (Cidade do México)", "26/10/2025", "17:00", "25/10/2025", "18:00"),
    ("brasil", "🇧🇷 São Paulo (Interlagos)", "02/11/2025", "12:30", "02/11/2025", "07:30"),
    ("las-vegas", "🇺🇸 Las Vegas (EUA)", "23/11/2025", "03:00", "22/11/2025", "03:00"),
    ("catar", "🇶🇦 Catar (Lusail)", "30/11/2025", "13:00", "29/11/2025", "15:00"),
    ("abu-dhabi", "🇦🇪 Abu Dhabi (Yas Marina)", "07/12/2025", "10:00", "06/12/2025", "11:00")
]

def init_database():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Cria a tabela de usuários se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      username TEXT UNIQUE NOT NULL,
                      first_name TEXT NOT NULL,
                      password TEXT NOT NULL,
                      is_admin BOOLEAN DEFAULT 0,
                      primeiro_login BOOLEAN DEFAULT 1)''')
        
        # Cria a tabela de palpites se não existir
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
        
        # Cria a tabela de respostas se não existir
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
        
        # Cria a tabela de pontuação se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS pontuacao
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      posicao INTEGER UNIQUE NOT NULL,
                      pontos INTEGER NOT NULL)''')
        
        # Insere valores padrão de pontuação se a tabela estiver vazia
        c.execute('SELECT COUNT(*) FROM pontuacao')
        if c.fetchone()[0] == 0:
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
            c.executemany('INSERT INTO pontuacao (posicao, pontos) VALUES (?, ?)', valores_padrao)
        
        # Cria a tabela de configuração de votação se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS config_votacao
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      gp_slug TEXT UNIQUE NOT NULL,
                      pole_habilitado BOOLEAN DEFAULT 1,
                      posicoes_habilitado BOOLEAN DEFAULT 1)''')
        
        # Cria a tabela de GPs se não existir
        c.execute('''CREATE TABLE IF NOT EXISTS gps
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      slug TEXT UNIQUE NOT NULL,
                      nome TEXT NOT NULL,
                      data_corrida TEXT NOT NULL,
                      hora_corrida TEXT NOT NULL,
                      data_classificacao TEXT NOT NULL,
                      hora_classificacao TEXT NOT NULL)''')
        
        # Insere os GPs se a tabela estiver vazia
        c.execute('SELECT COUNT(*) FROM gps')
        if c.fetchone()[0] == 0:
            for gp in gps_2025:
                c.execute('''INSERT INTO gps 
                            (slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao)
                            VALUES (?, ?, ?, ?, ?, ?)''',
                         (gp[0], gp[1], gp[2], gp[3], gp[4], gp[5]))
            
            # Insere configurações padrão para cada GP
            for gp in gps_2025:
                c.execute('''INSERT INTO config_votacao 
                            (gp_slug, pole_habilitado, posicoes_habilitado)
                            VALUES (?, ?, ?)''',
                         (gp[0], True, True))
        
        # Verifica se o admin existe
        c.execute('SELECT id FROM usuarios WHERE username = ?', ('admin',))
        if c.fetchone() is None:
            # Cria o usuário admin
            c.execute('''INSERT INTO usuarios 
                        (username, first_name, password, is_admin, primeiro_login) 
                        VALUES (?, ?, ?, ?, ?)''',
                     ('admin', 'Administrador', 
                      generate_password_hash('admin8163'), 
                      1, 0))
            print("Usuário administrador criado com sucesso!")
        else:
            print("Usuário administrador já existe!")
        
        conn.commit()
    except Exception as e:
        print(f"Erro ao inicializar banco de dados: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    init_database() 