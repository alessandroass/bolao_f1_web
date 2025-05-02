from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import random
import string
from datetime import datetime, timedelta
import pytz
from reset_admin import reset_admin_password  # Importando a função de reset do admin
from create_tables import create_tables  # Importando a função de criação de tabelas

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_aqui'

# Cria as tabelas necessárias
create_tables()

# Reseta a senha do admin
reset_admin_password()

# Caminho do banco de dados
DB_PATH = os.path.join(os.getenv('RENDER_PROJECT_ROOT', ''), 'data', 'bolao_f1.db')

# Função auxiliar para gerenciar conexões com o banco de dados
def get_db_connection():
    # Garante que o diretório data existe
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

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
    ("paises-baixos", "🇳 Holanda (Zandvoort)", "31/08/2025", "10:00", "30/08/2025", "10:00"),
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

# Lista dos pilotos da F1 2025
grid_2025 = [
    "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
    "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
    "Fernando Alonso", "Lance Stroll", "Liam Lawson", "Isack Hadjar",
    "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg", "Gabriel Bortoleto",
    "Esteban Ocon", "Oliver Bearman", "Carlos Sainz", "Alexander Albon"
]

# Configuração do banco de dados
def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Tabela de usuários
    c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  first_name TEXT NOT NULL,
                  password TEXT NOT NULL,
                  is_admin BOOLEAN DEFAULT 0,
                  primeiro_login BOOLEAN DEFAULT 1)''')
    
    # Tabela de pilotos
    c.execute('''CREATE TABLE IF NOT EXISTS pilotos
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  nome TEXT UNIQUE NOT NULL)''')
    
    # Verifica se a tabela de pilotos está vazia
    c.execute('SELECT COUNT(*) FROM pilotos')
    if c.fetchone()[0] == 0:
        # Lista correta de pilotos
        pilotos_iniciais = [
            "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
            "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
            "Fernando Alonso", "Lance Stroll", "Liam Lawson", "Isack Hadjar",
            "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg", "Gabriel Bortoleto",
            "Esteban Ocon", "Oliver Bearman", "Carlos Sainz", "Alexander Albon"
        ]
        
        # Insere os pilotos iniciais
        for piloto in pilotos_iniciais:
            c.execute('INSERT INTO pilotos (nome) VALUES (?)', (piloto,))
    
    # Tabela de palpites
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
    
    # Tabela de respostas corretas
    c.execute('''CREATE TABLE IF NOT EXISTS respostas
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
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
                  UNIQUE(gp_slug))''')
    
    # Tabela de pontuação
    c.execute('''CREATE TABLE IF NOT EXISTS pontuacao
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  posicao INTEGER UNIQUE NOT NULL,
                  pontos INTEGER NOT NULL)''')
    
    # Tabela de configuração de votação
    c.execute('''CREATE TABLE IF NOT EXISTS config_votacao
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  gp_slug TEXT UNIQUE NOT NULL,
                  pole_habilitado BOOLEAN DEFAULT 1,
                  posicoes_habilitado BOOLEAN DEFAULT 1)''')
    
    # Tabela de GPs
    c.execute('''CREATE TABLE IF NOT EXISTS gps
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  slug TEXT UNIQUE NOT NULL,
                  nome TEXT NOT NULL,
                  data_corrida TEXT NOT NULL,
                  hora_corrida TEXT NOT NULL,
                  data_classificacao TEXT NOT NULL,
                  hora_classificacao TEXT NOT NULL)''')
    
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
    
    # Insere configurações padrão para cada GP se não existirem
    c.execute('SELECT COUNT(*) FROM config_votacao')
    if c.fetchone()[0] == 0:
        for gp in gps_2025:
            c.execute('INSERT INTO config_votacao (gp_slug, pole_habilitado, posicoes_habilitado) VALUES (?, 1, 1)',
                     (gp[0],))
    
    # Insere os GPs na tabela se não existirem
    c.execute('SELECT COUNT(*) FROM gps')
    if c.fetchone()[0] == 0:
        for gp in gps_2025:
            c.execute('''INSERT INTO gps (slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (gp[0], gp[1], gp[2], gp[3], gp[4], gp[5]))
    
    conn.commit()
    conn.close()

# Decorator para verificar se o usuário é admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT is_admin FROM usuarios WHERE username = ?', (session['username'],))
        is_admin = c.fetchone()[0]
        conn.close()
        if not is_admin:
            flash('Acesso negado. Apenas administradores podem acessar esta página.', 'error')
            return redirect(url_for('tela_gps'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

# Rota principal - redireciona para login
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('tela_gps'))
    return redirect(url_for('login'))

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and check_password_hash(user[3], password):  # Índice 3 para password
            session['user_id'] = user[0]      # ID
            session['username'] = user[1]      # Username
            session['is_admin'] = user[4]      # is_admin
            
            # Verifica se é o primeiro login após reset de senha
            if user[5] == 1:  # primeiro_login
                return redirect(url_for('redefinir_senha'))
            
            return redirect(url_for('tela_gps'))
        else:
            flash('Usuário ou senha incorretos!', 'error')
    
    return render_template('login.html')

# Rota de registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        username = request.form['username']
        first_name = request.form['first_name']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        if password != confirm_password:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('registro'))
        
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            c.execute('INSERT INTO usuarios (username, first_name, password, is_admin, primeiro_login) VALUES (?, ?, ?, ?, ?)',
                     (username, first_name, generate_password_hash(password), 0, 0))
            conn.commit()
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Nome de usuário já existe!', 'error')
        finally:
            conn.close()
    
    return render_template('registro.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

# Rota da tela de GPs
@app.route('/tela_gps')
def tela_gps():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Definir o fuso horário de Brasília
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    
    # Data atual no fuso horário de Brasília
    hoje = datetime.now(tz_brasilia).date()
    
    # Buscar a posição e pontuação do usuário
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        WITH pontos_por_gp AS (
            SELECT 
                p.usuario_id,
                p.gp_slug,
                CASE WHEN p.pole = r.pole THEN 5 ELSE 0 END +
                CASE WHEN p.pos_1 = r.pos_1 THEN 25 ELSE 0 END +
                CASE WHEN p.pos_2 = r.pos_2 THEN 18 ELSE 0 END +
                CASE WHEN p.pos_3 = r.pos_3 THEN 15 ELSE 0 END +
                CASE WHEN p.pos_4 = r.pos_4 THEN 12 ELSE 0 END +
                CASE WHEN p.pos_5 = r.pos_5 THEN 10 ELSE 0 END +
                CASE WHEN p.pos_6 = r.pos_6 THEN 8 ELSE 0 END +
                CASE WHEN p.pos_7 = r.pos_7 THEN 6 ELSE 0 END +
                CASE WHEN p.pos_8 = r.pos_8 THEN 4 ELSE 0 END +
                CASE WHEN p.pos_9 = r.pos_9 THEN 2 ELSE 0 END +
                CASE WHEN p.pos_10 = r.pos_10 THEN 1 ELSE 0 END as pontos_gp
            FROM palpites p
            JOIN respostas r ON p.gp_slug = r.gp_slug
        )
        SELECT 
            u.id,
            u.first_name,
            COALESCE(SUM(ppg.pontos_gp), 0) as total_pontos
        FROM usuarios u
        LEFT JOIN pontos_por_gp ppg ON u.id = ppg.usuario_id
        WHERE u.username != 'admin'
        GROUP BY u.id, u.first_name
        ORDER BY total_pontos DESC
    ''')
    classificacao = cursor.fetchall()
    
    # Encontrar a posição e pontuação do usuário atual
    posicao = 0
    pontos = 0
    for i, (user_id, _, total) in enumerate(classificacao, 1):
        if user_id == session['user_id']:
            posicao = i
            pontos = total or 0
            break
    
    # Buscar palpites do usuário
    cursor.execute('''
        SELECT gp_slug FROM palpites 
        WHERE usuario_id = ?
    ''', (session['user_id'],))
    palpites_existentes = [row[0] for row in cursor.fetchall()]
    
    # Criar lista de GPs com informação de palpite existente
    gps_com_palpites = []
    for slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao in gps_2025:
        # Converter a data da corrida para date
        data_corrida_dt = datetime.strptime(data_corrida, '%d/%m/%Y').date()
        
        # Verificar se o GP está próximo (3 dias antes da corrida)
        dias_para_corrida = (data_corrida_dt - hoje).days
        esta_proximo = 0 <= dias_para_corrida <= 3
        
        gps_com_palpites.append({
            'slug': slug,
            'nome': nome,
            'tem_palpite': slug in palpites_existentes,
            'data_corrida': data_corrida_dt,  # Agora enviamos o objeto date
            'hora_corrida': hora_corrida,
            'data_classificacao': data_classificacao,
            'hora_classificacao': hora_classificacao,
            'esta_proximo': esta_proximo
        })
    
    conn.close()
    return render_template('tela_gps.html', 
                         gps=gps_com_palpites, 
                         is_admin=session.get('is_admin', False), 
                         posicao=posicao, 
                         pontos=pontos,
                         date_now=hoje)

# Rota da tela de palpites para cada GP
@app.route('/gp/<nome_gp>', methods=['GET', 'POST'])
def tela_palpite_gp(nome_gp):
    if 'username' not in session:
        return redirect(url_for('login'))

    mensagem = None
    tipo_mensagem = None

    # Busca informações do GP
    gp_info = next((gp for gp in gps_2025 if gp[0] == nome_gp), None)
    if not gp_info:
        flash('GP não encontrado!', 'error')
        return redirect(url_for('tela_gps'))

    # Verifica horário dos palpites
    pole_habilitado, posicoes_habilitado = verificar_horario_palpites(
        gp_info[4],  # data_classificacao
        gp_info[5],  # hora_classificacao
        gp_info[2],  # data_corrida
        gp_info[3]   # hora_corrida
    )

    if request.method == "POST":
        conn = get_db_connection()
        c = conn.cursor()
        
        # Debug: Imprimir dados recebidos do formulário
        print("Dados do formulário recebidos:")
        for key, value in request.form.items():
            print(f"{key}: {value}")
        
        # Verifica se já existe um palpite para este GP
        c.execute('SELECT id, pole, pos_1 FROM palpites WHERE usuario_id = ? AND gp_slug = ?',
                 (session['user_id'], nome_gp))
        palpite_existente = c.fetchone()
        
        # Debug: Imprimir palpite existente
        print("Palpite existente:", palpite_existente)
        
        # Verifica se está tentando votar apenas na pole position
        pole = request.form.get('pole')
        posicoes = [request.form.get(f'pos_{i}') for i in range(1, 11)]
        tem_pole = bool(pole)
        tem_posicoes = any(posicoes)
        
        # Debug: Imprimir valores processados
        print("Pole:", pole)
        print("Posições:", posicoes)
        print("Tem pole:", tem_pole)
        print("Tem posições:", tem_posicoes)
        
        if palpite_existente:
            # Se já tem palpite completo, não permite alteração
            if palpite_existente[1] and palpite_existente[2]:
                mensagem = 'Você já fez seu palpite completo para este GP!'
                tipo_mensagem = 'error'
            # Se tem apenas pole position, permite adicionar posições
            elif palpite_existente[1] and not palpite_existente[2]:
                if tem_pole:
                    mensagem = 'Você já votou na pole position!'
                    tipo_mensagem = 'error'
                elif not posicoes_habilitado:
                    mensagem = 'A votação para as posições está desabilitada!'
                    tipo_mensagem = 'error'
                else:
                    try:
                        # Atualiza apenas as posições
                        c.execute('''UPDATE palpites
                                    SET pos_1 = ?, pos_2 = ?, pos_3 = ?, pos_4 = ?, pos_5 = ?,
                                        pos_6 = ?, pos_7 = ?, pos_8 = ?, pos_9 = ?, pos_10 = ?
                                    WHERE id = ?''',
                                 (posicoes[0], posicoes[1], posicoes[2], posicoes[3], posicoes[4],
                                  posicoes[5], posicoes[6], posicoes[7], posicoes[8], posicoes[9],
                                  palpite_existente[0]))
                        conn.commit()
                        mensagem = 'Posições salvas com sucesso!'
                        tipo_mensagem = 'success'
                        print("Posições atualizadas com sucesso")
                    except Exception as e:
                        print("Erro ao atualizar posições:", str(e))
                        mensagem = 'Erro ao salvar as posições!'
                        tipo_mensagem = 'error'
            # Se não tem pole position, permite apenas votar nas posições
            else:
                if tem_posicoes and not posicoes_habilitado:
                    mensagem = 'A votação para as posições está desabilitada!'
                    tipo_mensagem = 'error'
                elif tem_pole and not pole_habilitado:
                    mensagem = 'A votação para pole position está desabilitada!'
                    tipo_mensagem = 'error'
                else:
                    try:
                        # Atualiza apenas as posições
                        c.execute('''UPDATE palpites
                                    SET pos_1 = ?, pos_2 = ?, pos_3 = ?, pos_4 = ?, pos_5 = ?,
                                        pos_6 = ?, pos_7 = ?, pos_8 = ?, pos_9 = ?, pos_10 = ?
                                    WHERE id = ?''',
                                 (posicoes[0], posicoes[1], posicoes[2], posicoes[3], posicoes[4],
                                  posicoes[5], posicoes[6], posicoes[7], posicoes[8], posicoes[9],
                                  palpite_existente[0]))
                        conn.commit()
                        mensagem = 'Posições salvas com sucesso!'
                        tipo_mensagem = 'success'
                        print("Posições atualizadas com sucesso")
                    except Exception as e:
                        print("Erro ao atualizar posições:", str(e))
                        mensagem = 'Erro ao salvar as posições!'
                        tipo_mensagem = 'error'
        else:
            # Insere novo palpite
            if tem_posicoes and not posicoes_habilitado:
                mensagem = 'A votação para as posições está desabilitada!'
                tipo_mensagem = 'error'
            elif tem_pole and not pole_habilitado:
                mensagem = 'A votação para pole position está desabilitada!'
                tipo_mensagem = 'error'
            else:
                try:
                    c.execute('''INSERT INTO palpites
                                (usuario_id, gp_slug, pos_1, pos_2, pos_3, pos_4, pos_5,
                                 pos_6, pos_7, pos_8, pos_9, pos_10, pole)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                             (session['user_id'], nome_gp, posicoes[0], posicoes[1], posicoes[2],
                              posicoes[3], posicoes[4], posicoes[5], posicoes[6], posicoes[7],
                              posicoes[8], posicoes[9], pole))
                    conn.commit()
                    mensagem = 'Palpite salvo com sucesso!'
                    tipo_mensagem = 'success'
                    print("Novo palpite inserido com sucesso")
                except Exception as e:
                    print("Erro ao inserir novo palpite:", str(e))
                    mensagem = 'Erro ao salvar o palpite!'
                    tipo_mensagem = 'error'
        
        conn.close()

    # Busca palpite existente
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT pos_1, pos_2, pos_3, pos_4, pos_5, pos_6, pos_7, pos_8,
                pos_9, pos_10, pole FROM palpites
                WHERE usuario_id = ? AND gp_slug = ?''',
             (session['user_id'], nome_gp))
    palpite = c.fetchone()
    conn.close()

    nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
    data_corrida = next((data for slug, _, data, _, _, _ in gps_2025 if slug == nome_gp), "Data não disponível")
    hora_corrida = next((hora for slug, _, _, hora, _, _ in gps_2025 if slug == nome_gp), "Hora não disponível")
    data_classificacao = next((data for slug, _, _, _, data, _ in gps_2025 if slug == nome_gp), "Data não disponível")
    hora_classificacao = next((hora for slug, _, _, _, _, hora in gps_2025 if slug == nome_gp), "Hora não disponível")
    
    return render_template('tela_palpite.html',
                         nome_gp=nome_gp,
                         nome_gp_exibicao=nome_gp_exibicao,
                         data_corrida=data_corrida,
                         hora_corrida=hora_corrida,
                         data_classificacao=data_classificacao,
                         hora_classificacao=hora_classificacao,
                         grid_2025=grid_2025,
                         palpite=palpite,
                         pole_habilitado=pole_habilitado,
                         posicoes_habilitado=posicoes_habilitado,
                         mensagem=mensagem,
                         tipo_mensagem=tipo_mensagem)

# Função para calcular pontos
def calcular_pontos(palpite, resposta):
    pontos = 0
    
    # Se não houver resposta, retorna 0 pontos
    if not resposta or len(resposta) < 12:  # Verifica se a resposta existe e tem pelo menos 12 elementos (pos_1 a pos_10 + pole)
        return pontos
    
    # Verifica pole position
    if palpite[13] and resposta[11] and palpite[13] == resposta[11]:  # palpite.pole == resposta.pole
        pontos += 5  # Pontos da pole position
    
    # Verifica posições
    for i in range(1, 11):
        if palpite[i+2] and resposta[i-1] and palpite[i+2] == resposta[i-1]:  # palpite.pos_X == resposta.pos_X
            if i == 1:
                pontos += 25
            elif i == 2:
                pontos += 18
            elif i == 3:
                pontos += 15
            elif i == 4:
                pontos += 12
            elif i == 5:
                pontos += 10
            elif i == 6:
                pontos += 8
            elif i == 7:
                pontos += 6
            elif i == 8:
                pontos += 4
            elif i == 9:
                pontos += 2
            elif i == 10:
                pontos += 1
    
    return pontos

# Rota para Meus Resultados
@app.route('/meus_resultados')
def meus_resultados():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Busca todos os palpites do usuário com as respostas correspondentes
    c.execute('''SELECT p.id, p.usuario_id, p.gp_slug, p.pos_1, p.pos_2, p.pos_3, p.pos_4, p.pos_5, 
                p.pos_6, p.pos_7, p.pos_8, p.pos_9, p.pos_10, p.pole,
                r.pos_1, r.pos_2, r.pos_3, r.pos_4, r.pos_5, r.pos_6, r.pos_7, r.pos_8, r.pos_9, r.pos_10, r.pole
                FROM palpites p
                LEFT JOIN respostas r ON p.gp_slug = r.gp_slug
                WHERE p.usuario_id = ?
                ORDER BY p.gp_slug''', (session['user_id'],))
    
    palpites = c.fetchall()
    resultados = []
    total_geral = 0
    
    # Busca os valores de pontuação da tabela pontuacao
    c.execute('SELECT posicao, pontos FROM pontuacao')
    valores_pontuacao = dict(c.fetchall())
    
    for palpite in palpites:
        # Encontra o nome do GP
        gp_nome = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == palpite[2]), palpite[2])
        
        # Calcula os pontos
        pontos_gp = 0
        
        # Verifica se o GP já tem respostas
        if palpite[14] is not None:  # Se r.pos_1 existe, significa que o GP tem respostas
            # Verifica pole position
            if palpite[13] == palpite[24] and palpite[24] is not None:
                pontos_gp += valores_pontuacao.get(0, 5)  # Usa 5 como valor padrão se não encontrar na tabela
            
            # Verifica posições
            for i in range(1, 11):
                if palpite[i+2] == palpite[i+13] and palpite[i+13] is not None:
                    pontos_gp += valores_pontuacao.get(i, 0)  # Usa 0 como valor padrão se não encontrar na tabela
        
        total_geral += pontos_gp
        
        resultados.append({
            'gp': gp_nome,
            'palpite': palpite,
            'pontos': pontos_gp
        })
    
    conn.close()
    return render_template('meus_resultados.html', 
                         resultados=resultados, 
                         gps_2025=gps_2025, 
                         total_geral=total_geral,
                         pontuacao=valores_pontuacao)

# Rota para Classificação Geral
@app.route('/classificacao')
def classificacao():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Busca todos os usuários (exceto admin) e seus palpites
    c.execute('''SELECT u.id, u.username, u.first_name, p.gp_slug, p.pos_1, p.pos_2, p.pos_3, p.pos_4, p.pos_5, 
                p.pos_6, p.pos_7, p.pos_8, p.pos_9, p.pos_10, p.pole,
                r.pos_1, r.pos_2, r.pos_3, r.pos_4, r.pos_5, r.pos_6, r.pos_7, r.pos_8, r.pos_9, r.pos_10, r.pole
                FROM usuarios u
                LEFT JOIN palpites p ON u.id = p.usuario_id
                LEFT JOIN respostas r ON p.gp_slug = r.gp_slug
                WHERE u.username != 'admin'
                ORDER BY u.username, p.gp_slug''')
    
    dados = c.fetchall()
    classificacao = {}
    
    # Busca os valores de pontuação da tabela pontuacao
    c.execute('SELECT posicao, pontos FROM pontuacao')
    valores_pontuacao = dict(c.fetchall())
    
    # Processa os dados para calcular a pontuação de cada usuário
    for linha in dados:
        usuario_id = linha[0]
        username = linha[1]
        first_name = linha[2]
        
        if usuario_id not in classificacao:
            classificacao[usuario_id] = {
                'username': username,
                'first_name': first_name,
                'total_pontos': 0
            }
        
        # Se houver palpite e resposta para este GP
        if linha[3] is not None:  # gp_slug
            pontos_gp = 0
            
            # Verifica pole position (posição 0 na tabela pontuacao)
            if linha[14] == linha[25] and linha[25] is not None:  # pole
                pontos_gp += valores_pontuacao.get(0, 5)  # Usa 5 como valor padrão se não encontrar na tabela
            
            # Verifica posições 1 a 10
            for i in range(1, 11):
                if linha[i+3] == linha[i+14] and linha[i+14] is not None:  # pos_1 a pos_10
                    pontos_gp += valores_pontuacao.get(i, 0)  # Usa 0 como valor padrão se não encontrar na tabela
            
            classificacao[usuario_id]['total_pontos'] += pontos_gp
    
    # Ordena a classificação por total de pontos
    classificacao_ordenada = sorted(classificacao.values(), key=lambda x: x['total_pontos'], reverse=True)
    
    conn.close()
    return render_template('classificacao.html', classificacao=classificacao_ordenada)

# Rota da área administrativa
@app.route('/admin')
@admin_required
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Busca todos os usuários
    c.execute('SELECT id, username, first_name, is_admin FROM usuarios')
    usuarios = [{'id': row[0], 'username': row[1], 'first_name': row[2], 'is_admin': row[3]} for row in c.fetchall()]
    
    # Busca todos os pilotos
    c.execute('SELECT nome FROM pilotos')
    pilotos = [row[0] for row in c.fetchall()]
    
    # Busca configurações de votação
    c.execute('SELECT gp_slug, pole_habilitado, posicoes_habilitado FROM config_votacao')
    configs = {row[0]: {'pole': row[1], 'posicoes': row[2]} for row in c.fetchall()}
    
    # Prepara lista de GPs com suas configurações
    gps_com_config = []
    for gp in gps_2025:
        slug = gp[0]
        config = configs.get(slug, {'pole': False, 'posicoes': False})
        gps_com_config.append({
            'slug': slug,
            'nome': gp[1],
            'pole_habilitado': config['pole'],
            'posicoes_habilitado': config['posicoes']
        })
    
    conn.close()
    
    return render_template('admin.html', gps=gps_com_config, usuarios=usuarios, pilotos=pilotos)

# Rota para editar respostas de um GP
@app.route('/admin/respostas/<nome_gp>', methods=['GET', 'POST'])
@admin_required
def admin_respostas(nome_gp):
    if request.method == 'POST':
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verifica se já existe resposta para este GP
        c.execute('SELECT id FROM respostas WHERE gp_slug = ?', (nome_gp,))
        resposta_existente = c.fetchone()
        
        # Prepara os dados
        pole = request.form.get('pole_position')
        posicoes = [request.form.get(f'pos{i}') for i in range(1, 11)]
        
        # Validação no servidor
        if not pole or not all(posicoes):
            flash('Todos os campos devem ser preenchidos!', 'error')
            # Cria uma resposta temporária com os valores submetidos
            resposta_temp = posicoes + [pole]
            nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
            return render_template('admin_respostas.html',
                                nome_gp=nome_gp,
                                nome_gp_exibicao=nome_gp_exibicao,
                                grid_2025=grid_2025,
                                resposta=resposta_temp)
        
        # Verifica duplicação de pilotos apenas entre as posições
        if len(posicoes) != len(set(posicoes)):
            flash('Não é permitido selecionar o mesmo piloto mais de uma vez nas posições!', 'error')
            # Cria uma resposta temporária com os valores submetidos
            resposta_temp = posicoes + [pole]
            nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
            return render_template('admin_respostas.html',
                                nome_gp=nome_gp,
                                nome_gp_exibicao=nome_gp_exibicao,
                                grid_2025=grid_2025,
                                resposta=resposta_temp)
        
        if resposta_existente:
            # Atualiza resposta existente
            c.execute('''UPDATE respostas SET
                        pos_1 = ?, pos_2 = ?, pos_3 = ?, pos_4 = ?, pos_5 = ?,
                        pos_6 = ?, pos_7 = ?, pos_8 = ?, pos_9 = ?, pos_10 = ?,
                        pole = ?
                        WHERE gp_slug = ?''',
                     (posicoes[0], posicoes[1], posicoes[2], posicoes[3], posicoes[4],
                      posicoes[5], posicoes[6], posicoes[7], posicoes[8], posicoes[9],
                      pole, nome_gp))
        else:
            # Insere nova resposta
            c.execute('''INSERT INTO respostas
                        (gp_slug, pos_1, pos_2, pos_3, pos_4, pos_5,
                         pos_6, pos_7, pos_8, pos_9, pos_10, pole)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (nome_gp, posicoes[0], posicoes[1], posicoes[2], posicoes[3],
                      posicoes[4], posicoes[5], posicoes[6], posicoes[7], posicoes[8],
                      posicoes[9], pole))
        
        conn.commit()
        conn.close()
        flash('Respostas salvas com sucesso!', 'success')
        
        # Busca a resposta atualizada para exibir na página
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('''SELECT pos_1, pos_2, pos_3, pos_4, pos_5, pos_6, pos_7, pos_8,
                    pos_9, pos_10, pole FROM respostas
                    WHERE gp_slug = ?''',
                 (nome_gp,))
        resposta = c.fetchone()
        conn.close()
        
        nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
        
        return render_template('admin_respostas.html',
                             nome_gp=nome_gp,
                             nome_gp_exibicao=nome_gp_exibicao,
                             grid_2025=grid_2025,
                             resposta=resposta)
    
    # Busca resposta existente
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''SELECT pos_1, pos_2, pos_3, pos_4, pos_5, pos_6, pos_7, pos_8,
                pos_9, pos_10, pole FROM respostas
                WHERE gp_slug = ?''',
             (nome_gp,))
    resposta = c.fetchone()
    conn.close()
    
    nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
    
    return render_template('admin_respostas.html',
                         nome_gp=nome_gp,
                         nome_gp_exibicao=nome_gp_exibicao,
                         grid_2025=grid_2025,
                         resposta=resposta)

# Rota para editar pontuação
@app.route('/admin/pontuacao', methods=['GET', 'POST'])
@admin_required
def admin_pontuacao():
    if request.method == 'POST':
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            # Atualiza os valores de pontuação
            for posicao in range(11):  # 0 a 10 (pole + 10 posições)
                pontos = request.form.get(f'pontos_{posicao}')
                if pontos:
                    c.execute('UPDATE pontuacao SET pontos = ? WHERE posicao = ?',
                             (int(pontos), posicao))
            
            conn.commit()
            flash('Pontuação atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar pontuação: {str(e)}', 'error')
        finally:
            conn.close()
    
    # Busca os valores atuais
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT posicao, pontos FROM pontuacao ORDER BY posicao')
    pontuacao = dict(c.fetchall())
    conn.close()
    
    return render_template('admin_pontuacao.html', pontuacao=pontuacao)

@app.route('/admin/gerenciar-pilotos', methods=['GET', 'POST'])
@admin_required
def admin_gerenciar_pilotos():
    if request.method == 'POST':
        novo_piloto = request.form.get('novo_piloto')
        piloto = request.form.get('piloto')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        if novo_piloto:
            try:
                c.execute('INSERT INTO pilotos (nome) VALUES (?)', (novo_piloto,))
                conn.commit()
                flash('Piloto adicionado com sucesso!', 'success')
            except sqlite3.IntegrityError:
                flash('Este piloto já está cadastrado!', 'error')
        
        elif piloto:
            try:
                c.execute('DELETE FROM pilotos WHERE nome = ?', (piloto,))
                conn.commit()
                flash('Piloto excluído com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao excluir piloto: {str(e)}', 'error')
        
        conn.close()
    
    # Busca todos os pilotos
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT nome FROM pilotos ORDER BY nome')
    pilotos = [row[0] for row in c.fetchall()]
    conn.close()
    
    return render_template('admin_gerenciar_pilotos.html', pilotos=pilotos)

@app.route('/admin/gerenciar-usuarios', methods=['GET', 'POST'])
@admin_required
def admin_gerenciar_usuarios():
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        action = request.form.get('action')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        if action == 'reset_password':
            # Busca o username do usuário
            c.execute('SELECT username FROM usuarios WHERE id = ?', (usuario_id,))
            username = c.fetchone()[0]
            
            # Define a nova senha como o username
            c.execute('UPDATE usuarios SET password = ?, primeiro_login = 1 WHERE id = ?',
                     (generate_password_hash(username), usuario_id))
            conn.commit()
            flash('Senha resetada com sucesso! A nova senha é igual ao login.', 'success')
        
        elif action == 'delete':
            c.execute('DELETE FROM usuarios WHERE id = ?', (usuario_id,))
            conn.commit()
            flash('Usuário excluído com sucesso!', 'success')
        
        conn.close()
    
    # Busca todos os usuários
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT id, username, first_name, is_admin FROM usuarios')
    usuarios = [{'id': row[0], 'username': row[1], 'first_name': row[2], 'is_admin': row[3]} for row in c.fetchall()]
    conn.close()
    
    return render_template('admin_gerenciar_usuarios.html', usuarios=usuarios)

@app.route('/redefinir-senha', methods=['GET', 'POST'])
def redefinir_senha():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('redefinir_senha'))
        
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('UPDATE usuarios SET password = ?, primeiro_login = 0 WHERE id = ?',
                 (generate_password_hash(nova_senha), session['user_id']))
        conn.commit()
        conn.close()
        
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('tela_gps'))
    
    return render_template('redefinir_senha.html')

def reset_admin_password():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Define a senha do admin como 'admin8163'
    c.execute('UPDATE usuarios SET password = ?, primeiro_login = 0 WHERE username = ?',
             (generate_password_hash('admin8163'), 'admin'))
    conn.commit()
    conn.close()
    
    print("Senha do admin resetada com sucesso!")

@app.route('/admin/resetar-senha/<int:user_id>', methods=['POST'])
@admin_required
def resetar_senha(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    
    # Gera uma senha aleatória
    nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    senha_hash = generate_password_hash(nova_senha)
    
    # Atualiza a senha e define primeiro_login como 1
    c.execute('UPDATE usuarios SET password = ?, primeiro_login = 1 WHERE id = ?', 
              (senha_hash, user_id))
    
    conn.commit()
    conn.close()
    
    flash(f'Senha resetada com sucesso! Nova senha: {nova_senha}', 'success')
    return redirect(url_for('admin_gerenciar_usuarios'))

@app.route('/alterar-senha', methods=['GET', 'POST'])
def alterar_senha():
    if 'username' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        senha_atual = request.form['senha_atual']
        nova_senha = request.form['nova_senha']
        confirmar_senha = request.form['confirmar_senha']
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Verifica a senha atual
        c.execute('SELECT password FROM usuarios WHERE id = ?', (session['user_id'],))
        senha_hash = c.fetchone()[0]
        
        if not check_password_hash(senha_hash, senha_atual):
            flash('Senha atual incorreta!', 'error')
            return redirect(url_for('alterar_senha'))
            
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('alterar_senha'))
            
        # Atualiza a senha e define primeiro_login como 0
        nova_senha_hash = generate_password_hash(nova_senha)
        c.execute('UPDATE usuarios SET password = ?, primeiro_login = 0 WHERE id = ?', 
                  (nova_senha_hash, session['user_id']))
        
        conn.commit()
        conn.close()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('alterar_senha.html')

# Rota para Resultados Parciais por Corrida
@app.route('/resultados-parciais')
def resultados_parciais():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Busca todos os usuários (exceto admin)
    c.execute('SELECT id, first_name FROM usuarios WHERE username != "admin"')
    usuarios = c.fetchall()
    
    # Usa a lista gps_2025 definida no início do arquivo
    gps = gps_2025
    
    # Busca todos os palpites com as respostas correspondentes
    c.execute('''
        SELECT p.id, p.usuario_id, p.gp_slug, p.pos_1, p.pos_2, p.pos_3, p.pos_4, p.pos_5, 
               p.pos_6, p.pos_7, p.pos_8, p.pos_9, p.pos_10, p.pole,
               r.pos_1, r.pos_2, r.pos_3, r.pos_4, r.pos_5, r.pos_6, r.pos_7, r.pos_8, r.pos_9, r.pos_10, r.pole
        FROM palpites p
        LEFT JOIN respostas r ON p.gp_slug = r.gp_slug
        ORDER BY p.usuario_id, p.gp_slug
    ''')
    
    palpites = c.fetchall()
    classificacao = []
    
    for usuario_id, first_name in usuarios:
        usuario = {
            'first_name': first_name,
            'total_pontos': 0,
            'pontos_por_gp': {}
        }
        
        # Inicializa pontos por GP
        for gp_slug, _, _, _, _, _ in gps:
            usuario['pontos_por_gp'][gp_slug] = 0
        
        # Calcula pontos para cada GP
        for palpite in palpites:
            if palpite[1] == usuario_id:  # usuario_id
                pontos_gp = 0
                
                # Verifica pole position
                if palpite[13] == palpite[24] and palpite[24] is not None:
                    pontos_gp += 5
                
                # Verifica posições
                for i in range(1, 11):
                    if palpite[i+2] == palpite[i+13] and palpite[i+13] is not None:
                        if i == 1:
                            pontos_gp += 25
                        elif i == 2:
                            pontos_gp += 18
                        elif i == 3:
                            pontos_gp += 15
                        elif i == 4:
                            pontos_gp += 12
                        elif i == 5:
                            pontos_gp += 10
                        elif i == 6:
                            pontos_gp += 8
                        elif i == 7:
                            pontos_gp += 6
                        elif i == 8:
                            pontos_gp += 4
                        elif i == 9:
                            pontos_gp += 2
                        elif i == 10:
                            pontos_gp += 1
                
                usuario['pontos_por_gp'][palpite[2]] = pontos_gp  # gp_slug
                usuario['total_pontos'] += pontos_gp
        
        classificacao.append(usuario)
    
    # Ordena por total de pontos
    classificacao.sort(key=lambda x: x['total_pontos'], reverse=True)
    
    conn.close()
    return render_template('resultados_parciais.html', classificacao=classificacao, gps=gps)

# Rota para Configurações do Sistema
@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@admin_required
def admin_configuracoes():
    if request.method == 'POST':
        for gp in gps_2025:
            slug = gp[0]
            pole_habilitado = request.form.get(f'pole_{slug}') == 'on'
            posicoes_habilitado = request.form.get(f'posicoes_{slug}') == 'on'
            
            # Atualizar configurações no banco de dados
            conn = get_db_connection()
            c = conn.cursor()
            c.execute('''UPDATE config_votacao 
                        SET pole_habilitado = ?, posicoes_habilitado = ?
                        WHERE gp_slug = ?''',
                     (pole_habilitado, posicoes_habilitado, slug))
            conn.commit()
            conn.close()
        
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('admin_configuracoes'))
    
    # Buscar configurações atuais
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT gp_slug, pole_habilitado, posicoes_habilitado FROM config_votacao')
    configs_db = {row[0]: {'pole': row[1], 'posicoes': row[2]} for row in c.fetchall()}
    conn.close()
    
    # Preparar lista de GPs com suas configurações
    gps = []
    for gp in gps_2025:
        slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao = gp
        config = configs_db.get(slug, {'pole': False, 'posicoes': False})
        
        # Verificar status atual baseado no horário
        pole_habilitado, posicoes_habilitado = verificar_horario_palpites(
            data_classificacao,
            hora_classificacao,
            data_corrida,
            hora_corrida
        )
        
        # Se a corrida já aconteceu, desabilita automaticamente
        # mas permite que o admin sobrescreva manualmente
        if not pole_habilitado and not posicoes_habilitado:
            # Desabilita automaticamente
            pole_habilitado = False
            posicoes_habilitado = False
            
            # Se o admin configurou manualmente, sobrescreve
            if config['pole']:
                pole_habilitado = True
            if config['posicoes']:
                posicoes_habilitado = True
        
        gps.append({
            'slug': slug,
            'nome': nome,
            'data_corrida': data_corrida,
            'hora_corrida': hora_corrida,
            'data_classificacao': data_classificacao,
            'hora_classificacao': hora_classificacao,
            'pole_habilitado': pole_habilitado,
            'posicoes_habilitado': posicoes_habilitado
        })
    
    return render_template('admin_configuracoes.html', gps=gps)

def verificar_horario_palpites(data_classificacao, hora_classificacao, data_corrida, hora_corrida):
    """Verifica se os palpites estão habilitados baseado no horário da classificação e corrida"""
    # Definir o fuso horário de Brasília
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    
    # Data e hora atual no fuso horário de Brasília
    agora = datetime.now(tz_brasilia)
    
    # Converter data e hora da classificação para datetime
    data_classificacao_dt = datetime.strptime(f"{data_classificacao} {hora_classificacao}", "%d/%m/%Y %H:%M")
    data_classificacao_dt = tz_brasilia.localize(data_classificacao_dt)
    
    # Converter data e hora da corrida para datetime
    data_corrida_dt = datetime.strptime(f"{data_corrida} {hora_corrida}", "%d/%m/%Y %H:%M")
    data_corrida_dt = tz_brasilia.localize(data_corrida_dt)
    
    # Calcular a diferença em horas para a classificação
    diferenca_classificacao = (data_classificacao_dt - agora).total_seconds() / 3600
    
    # Calcular a diferença em horas para a corrida
    diferenca_corrida = (data_corrida_dt - agora).total_seconds() / 3600
    
    # Se o GP já aconteceu, desabilita tudo
    if diferenca_corrida < 0:
        return False, False
    
    # Se faltar menos de 1 hora para a classificação, desabilita pole position
    pole_habilitado = diferenca_classificacao >= 1
    
    # Se faltar menos de 1 hora para a classificação e mais de 20 minutos para a corrida, habilita posições
    posicoes_habilitado = diferenca_classificacao < 1 and diferenca_corrida > (20/60)
    
    return pole_habilitado, posicoes_habilitado

@app.route('/tela_palpite/<gp_slug>')
def tela_palpite(gp_slug):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    # Busca informações do GP
    gp_info = next((gp for gp in gps_2025 if gp[0] == gp_slug), None)
    if not gp_info:
        return redirect(url_for('tela_gps'))
    
    # Verifica horário dos palpites
    pole_habilitado, posicoes_habilitado = verificar_horario_palpites(
        gp_info[4],  # data_classificacao
        gp_info[5],  # hora_classificacao
        gp_info[2],  # data_corrida
        gp_info[3]   # hora_corrida
    )
    
    # Busca configurações do banco de dados
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT pole_habilitado, posicoes_habilitado FROM config_votacao WHERE gp_slug = ?', (gp_slug,))
    config = c.fetchone()
    conn.close()
    
    # Se a corrida já aconteceu, desabilita automaticamente
    # mas permite que o admin sobrescreva manualmente
    if not pole_habilitado and not posicoes_habilitado:
        # Desabilita automaticamente
        pole_habilitado = False
        posicoes_habilitado = False
        
        # Se o admin configurou manualmente, sobrescreve
        if config and config[0]:  # pole_habilitado
            pole_habilitado = True
        if config and config[1]:  # posicoes_habilitado
            posicoes_habilitado = True
    
    # Busca o palpite do usuário para este GP
    cursor = conn.cursor()
    cursor.execute('''
        SELECT pole, posicoes 
        FROM palpites 
        WHERE usuario_id = %s AND gp_slug = %s
    ''', (session['usuario_id'], gp_slug))
    palpite = cursor.fetchone()
    cursor.close()
    
    return render_template('tela_palpite.html', 
                         gp_slug=gp_slug,
                         gp_nome=gp_info[1],
                         data_corrida=gp_info[2],
                         hora_corrida=gp_info[3],
                         data_classificacao=gp_info[4],
                         hora_classificacao=gp_info[5],
                         palpite=palpite,
                         pole_habilitado=pole_habilitado,
                         posicoes_habilitado=posicoes_habilitado)

@app.route('/admin/datas-gps', methods=['GET', 'POST'])
@admin_required
def admin_datas_gps():
    if request.method == 'POST':
        conn = get_db_connection()
        c = conn.cursor()
        
        try:
            gp_slug = request.form.get('gp_slug')
            data_corrida = request.form.get(f'data_corrida_{gp_slug}')
            hora_corrida = request.form.get(f'hora_corrida_{gp_slug}')
            data_classificacao = request.form.get(f'data_classificacao_{gp_slug}')
            hora_classificacao = request.form.get(f'hora_classificacao_{gp_slug}')
            
            # Atualiza as datas no banco de dados
            c.execute('''
                UPDATE gps 
                SET data_corrida = ?, hora_corrida = ?, 
                    data_classificacao = ?, hora_classificacao = ?
                WHERE slug = ?
            ''', (data_corrida, hora_corrida, data_classificacao, hora_classificacao, gp_slug))
            
            conn.commit()
            
            # Se for uma requisição AJAX, retorna JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': 'Datas atualizadas com sucesso!',
                    'category': 'success'
                })
            
            flash('Datas atualizadas com sucesso!', 'success')
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': False,
                    'message': f'Erro ao atualizar datas: {str(e)}',
                    'category': 'error'
                })
            flash(f'Erro ao atualizar datas: {str(e)}', 'error')
        finally:
            conn.close()
    
    # Busca as datas atuais dos GPs
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT slug, data_corrida, hora_corrida, data_classificacao, hora_classificacao FROM gps')
    gps_datas = {row[0]: {
        'data_corrida': row[1],
        'hora_corrida': row[2],
        'data_classificacao': row[3],
        'hora_classificacao': row[4]
    } for row in c.fetchall()}
    conn.close()
    
    # Prepara lista de GPs com suas datas
    gps_com_datas = []
    for gp in gps_2025:
        slug = gp[0]
        datas = gps_datas.get(slug, {})
        gps_com_datas.append({
            'slug': slug,
            'nome': gp[1],
            'data_corrida': datas.get('data_corrida', ''),
            'hora_corrida': datas.get('hora_corrida', ''),
            'data_classificacao': datas.get('data_classificacao', ''),
            'hora_classificacao': datas.get('hora_classificacao', '')
        })
    
    return render_template('admin_datas_gps.html', gps=gps_com_datas)

def criar_admin():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Verifica se já existe um usuário admin
    c.execute('SELECT COUNT(*) FROM usuarios WHERE username = ?', ('admin',))
    if c.fetchone()[0] == 0:
        # Cria o usuário admin com senha 'admin8163'
        senha_hash = generate_password_hash('admin8163')
        c.execute('INSERT INTO usuarios (username, first_name, password, is_admin, primeiro_login) VALUES (?, ?, ?, ?, ?)',
                 ('admin', 'Administrador', senha_hash, 1, 0))
        conn.commit()
        print("Usuário admin criado com sucesso!")
        print("Login: admin")
        print("Senha: admin8163")
    else:
        print("Usuário admin já existe!")
    
    conn.close()

if __name__ == "__main__":
    criar_admin()  # Cria o usuário admin se não existir
    app.run(debug=True, host='0.0.0.0', port=5000)
