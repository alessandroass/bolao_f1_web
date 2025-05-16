from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import random
import string
from datetime import datetime, timedelta
import pytz
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP, PontuacaoSprint
from config import Config
from config_local import ConfigLocal
from reset_admin import reset_admin_password  # Importando a função de reset do admin
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import sqlite3

app = Flask(__name__)

# Verifica se está rodando localmente (desenvolvimento) ou no Render (produção)
if os.getenv('FLASK_ENV') == 'development':
    app.config.from_object(ConfigLocal)
    print("Rodando em modo de desenvolvimento local")
else:
    app.config.from_object(Config)
    print("Rodando em modo de produção (Render)")

# Configurações adicionais do SQLAlchemy
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {
        'options': '-c client_encoding=utf8'
    }
}

db.init_app(app)

def create_tables():
    with app.app_context():
        # Cria todas as tabelas definidas nos modelos
        db.create_all()
        
        # Inicializa a tabela de pontuação se estiver vazia
        if Pontuacao.query.count() == 0:
            pontos = [
                (1, 25), (2, 18), (3, 15), (4, 12), (5, 10),
                (6, 8), (7, 6), (8, 4), (9, 2), (10, 1)
            ]
            for posicao, pontos in pontos:
                pontuacao = Pontuacao(posicao=posicao, pontos=pontos)
                db.session.add(pontuacao)
            
            db.session.commit()
            print("Tabela de pontuação inicializada com sucesso!")

def sincronizar_gps_banco():
    """Sincroniza a lista gps_2025 com o banco de dados."""
    try:
        for slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao in gps_2025:
            gp = GP.query.filter_by(slug=slug).first()
            if not gp:
                gp = GP(
                    slug=slug,
                    nome=nome,
                    data_corrida=data_corrida,
                    hora_corrida=hora_corrida,
                    data_classificacao=data_classificacao,
                    hora_classificacao=hora_classificacao
                )
                db.session.add(gp)
            else:
                gp.nome = nome
                gp.data_corrida = data_corrida
                gp.hora_corrida = hora_corrida
                gp.data_classificacao = data_classificacao
                gp.hora_classificacao = hora_classificacao
        
        db.session.commit()
        print("GPs sincronizados com sucesso!")
    except Exception as e:
        print(f"Erro ao sincronizar GPs: {str(e)}")
        db.session.rollback()

def verificar_banco_existe():
    with app.app_context():
        # Cria as tabelas se não existirem
        db.create_all()
        
        # Verifica se o admin existe
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            reset_admin_password()
            print("Usuário admin criado com sucesso!")
        else:
            print("Banco de dados já existe, apenas verificando admin...")
        
        # Sincroniza os GPs com o banco de dados
        sincronizar_gps_banco()

# Verifica e inicializa o banco de dados
verificar_banco_existe()

# Lista dos GPs (nome da rota, nome para exibição, data da corrida, hora da corrida, data da classificação, hora da classificação)
gps_2025 = [
    ("australia", "🇦🇺 Austrália (Melbourne)", "16/03/2025", "01:00", "15/03/2025", "02:00"),
    ("sprint-china", "🇨🇳 Sprint - China (Xangai)", "22/03/2025", "00:00", "21/03/2025", "04:30"),
    ("china", "🇨🇳 China (Xangai)", "23/03/2025", "04:00", "22/03/2025", "04:00"),
    ("japao", "🇯🇵 Japão (Suzuka)", "06/04/2025", "02:00", "05/04/2025", "03:00"),
    ("bahrein", "🇧🇭 Bahrein (Sakhir)", "13/04/2025", "12:00", "12/04/2025", "13:00"),
    ("arabia-saudita", "🇸🇦 Arábia Saudita (Jeddah)", "20/04/2025", "14:00", "19/04/2025", "14:00"),
    ("sprint-miami", "🇺🇸 Sprint - Miami (EUA)", "03/05/2025", "13:00", "02/05/2025", "17:30"),
    ("miami", "🇺🇸 Miami (EUA)", "04/05/2025", "17:00", "03/05/2025", "17:00"),
    ("emilia-romagna", "🇮🇹 Emilia-Romagna (Imola)", "18/05/2025", "10:00", "17/05/2025", "11:00"),
    ("monaco", "🇲🇨 Mônaco (Monte Carlo)", "25/05/2025", "10:00", "24/05/2025", "11:00"),
    ("espanha", "🇪🇸 Espanha (Barcelona)", "22/06/2025", "10:00", "21/06/2025", "11:00"),
    ("canada", "🇨🇦 Canadá (Montreal)", "15/06/2025", "15:00", "14/06/2025", "17:00"),
    ("sprint-austria", "🇦🇹 Sprint - Áustria (Spielberg)", "28/06/2025", "07:00", "27/06/2025", "11:30"),
    ("austria", "🇦🇹 Áustria (Spielberg)", "29/06/2025", "10:00", "28/06/2025", "11:00"),
    ("reino-unido", "🇬🇧 Reino Unido (Silverstone)", "06/07/2025", "11:00", "05/07/2025", "11:00"),
    ("belgica", "🇧🇪 Bélgica (Spa-Francorchamps)", "27/07/2025", "10:00", "26/07/2025", "11:00"),
    ("hungria", "🇭🇺 Hungria (Budapeste)", "03/08/2025", "10:00", "02/08/2025", "11:00"),
    ("paises-baixos", "🇳 Holanda (Zandvoort)", "31/08/2025", "10:00", "30/08/2025", "10:00"),
    ("monza", "🇮🇹 Itália (Monza)", "07/09/2025", "10:00", "06/09/2025", "11:00"),
    ("azerbaijao", "🇦🇿 Azerbaijão (Baku)", "21/09/2025", "08:00", "20/09/2025", "09:00"),
    ("singapura", "🇸🇬 Singapura (Marina Bay)", "05/10/2025", "09:00", "04/10/2025", "10:00"),
    ("sprint-austin", "🇺🇸 Sprint - EUA (Austin)", "18/10/2025", "15:00", "17/10/2025", "18:30"),
    ("austin", "🇺🇸 EUA (Austin)", "19/10/2025", "16:00", "18/10/2025", "15:00"),
    ("mexico", "🇲🇽 México (Cidade do México)", "26/10/2025", "17:00", "25/10/2025", "18:00"),
    ("sprint-brasil", "🇧🇷 Sprint - São Paulo (Interlagos)", "01/11/2025", "11:00", "31/10/2025", "15:30"),
    ("brasil", "🇧🇷 São Paulo (Interlagos)", "02/11/2025", "12:30", "07/04/2025", "07:30"),
    ("las-vegas", "🇺🇸 Las Vegas (EUA)", "23/11/2025", "03:00", "22/11/2025", "03:00"),
    ("sprint-catar", "🇶🇦 Sprint - Catar (Lusail)", "29/11/2025", "11:00", "28/11/2025", "14:30"),
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

# Decorator para verificar se o usuário é admin
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        usuario = Usuario.query.filter_by(username=session['username']).first()
        if not usuario or not usuario.is_admin:
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
        
        usuario = Usuario.query.filter_by(username=username).first()
        
        if usuario and usuario.check_password(password):
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            session['is_admin'] = usuario.is_admin
            
            # Verifica se é o primeiro login após reset de senha
            if usuario.primeiro_login:
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
        
        try:
            usuario = Usuario(
                username=username,
                first_name=first_name,
                is_admin=False,
                primeiro_login=False
            )
            usuario.set_password(password)
            db.session.add(usuario)
            db.session.commit()
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Nome de usuário já existe!', 'error')
    
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
    
    # Buscar o usuário
    usuario = Usuario.query.get(session['user_id'])
    
    # Buscar todos os palpites do usuário
    palpites_existentes = [p.gp_slug for p in usuario.palpites]
    
    # Buscar todos os palpites e respostas para calcular a pontuação
    palpites = Palpite.query.filter_by(usuario_id=usuario.id).all()
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    # Calcular pontuação total do usuário
    pontos_total = 0
    for palpite in palpites:
        resposta = respostas.get(palpite.gp_slug)
        if resposta:
            # Verifica pole position
            if palpite.pole == resposta.pole and resposta.pole is not None:
                if palpite.gp_slug.startswith('sprint'):
                    pontos_total += pontuacao_sprint.get(0, 1)
                else:
                    pontos_total += pontuacao.get(0, 5)
            
            # Verifica posições
            for i in range(1, 11):
                palpite_pos = getattr(palpite, f'pos_{i}')
                resposta_pos = getattr(resposta, f'pos_{i}')
                if palpite_pos == resposta_pos and resposta_pos is not None:
                    if palpite.gp_slug.startswith('sprint'):
                        pontos_total += pontuacao_sprint.get(i, 0)
                    else:
                        pontos_total += pontuacao.get(i, 0)
    
    # Buscar todos os usuários para calcular a posição
    usuarios = Usuario.query.filter(Usuario.username != 'admin').all()
    classificacao = []
    
    for user in usuarios:
        pontos_user = 0
        palpites_user = Palpite.query.filter_by(usuario_id=user.id).all()
        
        for palpite in palpites_user:
            resposta = respostas.get(palpite.gp_slug)
            if resposta:
                # Verifica pole position
                if palpite.pole == resposta.pole and resposta.pole is not None:
                    if palpite.gp_slug.startswith('sprint'):
                        pontos_user += pontuacao_sprint.get(0, 1)
                    else:
                        pontos_user += pontuacao.get(0, 5)
                
                # Verifica posições
                for i in range(1, 11):
                    palpite_pos = getattr(palpite, f'pos_{i}')
                    resposta_pos = getattr(resposta, f'pos_{i}')
                    if palpite_pos == resposta_pos and resposta_pos is not None:
                        if palpite.gp_slug.startswith('sprint'):
                            pontos_user += pontuacao_sprint.get(i, 0)
                        else:
                            pontos_user += pontuacao.get(i, 0)
        
        classificacao.append({
            'username': user.username,
            'pontos': pontos_user
        })
    
    # Ordenar por pontuação
    classificacao.sort(key=lambda x: x['pontos'], reverse=True)
    
    # Encontrar posição do usuário
    posicao = 1
    for i, user in enumerate(classificacao):
        if user['username'] == usuario.username:
            posicao = i + 1
            break
    
    # Criar lista de eventos (GPs) com informação de palpite existente
    eventos = []
    for slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao in gps_2025:
        data_corrida_dt = datetime.strptime(data_corrida, '%d/%m/%Y').date()
        dias_para_corrida = (data_corrida_dt - hoje).days
        esta_proximo = 0 <= dias_para_corrida <= 3
        eventos.append({
            'tipo': 'gp',
            'slug': slug,
            'nome': nome,
            'tem_palpite': slug in palpites_existentes,
            'data_corrida': data_corrida_dt,
            'hora_corrida': hora_corrida,
            'data_classificacao': data_classificacao,
            'hora_classificacao': hora_classificacao,
            'esta_proximo': esta_proximo
        })
    
    # Ordenar todos por data
    eventos.sort(key=lambda x: x['data_corrida'])

    return render_template('tela_gps.html', 
                         eventos=eventos,
                         is_admin=session.get('is_admin', False),
                         date_now=hoje,
                         pontos=pontos_total,
                         posicao=posicao)

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
        # Debug: Imprimir dados recebidos do formulário
        print("Dados do formulário recebidos:")
        for key, value in request.form.items():
            print(f"{key}: {value}")
        
        # Verifica se já existe um palpite para este GP
        palpite_existente = Palpite.query.filter_by(
            usuario_id=session['user_id'],
            gp_slug=nome_gp
        ).first()
        
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
            if palpite_existente.pole and palpite_existente.pos_1:
                mensagem = 'Você já fez seu palpite completo para este GP!'
                tipo_mensagem = 'error'
            # Se tem apenas pole position, permite adicionar posições
            elif palpite_existente.pole and not palpite_existente.pos_1:
                if tem_pole:
                    mensagem = 'Você já votou na pole position!'
                    tipo_mensagem = 'error'
                elif not posicoes_habilitado:
                    mensagem = 'A votação para as posições está desabilitada!'
                    tipo_mensagem = 'error'
                else:
                    try:
                        # Atualiza apenas as posições
                        palpite_existente.pos_1 = posicoes[0]
                        palpite_existente.pos_2 = posicoes[1]
                        palpite_existente.pos_3 = posicoes[2]
                        palpite_existente.pos_4 = posicoes[3]
                        palpite_existente.pos_5 = posicoes[4]
                        palpite_existente.pos_6 = posicoes[5]
                        palpite_existente.pos_7 = posicoes[6]
                        palpite_existente.pos_8 = posicoes[7]
                        palpite_existente.pos_9 = posicoes[8]
                        palpite_existente.pos_10 = posicoes[9]
                        db.session.commit()
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
                        palpite_existente.pos_1 = posicoes[0]
                        palpite_existente.pos_2 = posicoes[1]
                        palpite_existente.pos_3 = posicoes[2]
                        palpite_existente.pos_4 = posicoes[3]
                        palpite_existente.pos_5 = posicoes[4]
                        palpite_existente.pos_6 = posicoes[5]
                        palpite_existente.pos_7 = posicoes[6]
                        palpite_existente.pos_8 = posicoes[7]
                        palpite_existente.pos_9 = posicoes[8]
                        palpite_existente.pos_10 = posicoes[9]
                        db.session.commit()
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
                    novo_palpite = Palpite(
                        usuario_id=session['user_id'],
                        gp_slug=nome_gp,
                        pos_1=posicoes[0],
                        pos_2=posicoes[1],
                        pos_3=posicoes[2],
                        pos_4=posicoes[3],
                        pos_5=posicoes[4],
                        pos_6=posicoes[5],
                        pos_7=posicoes[6],
                        pos_8=posicoes[7],
                        pos_9=posicoes[8],
                        pos_10=posicoes[9],
                        pole=pole
                    )
                    db.session.add(novo_palpite)
                    db.session.commit()
                    mensagem = 'Palpite salvo com sucesso!'
                    tipo_mensagem = 'success'
                    print("Novo palpite inserido com sucesso")
                except Exception as e:
                    print("Erro ao inserir novo palpite:", str(e))
                    mensagem = 'Erro ao salvar o palpite!'
                    tipo_mensagem = 'error'

    # Busca palpite existente
    palpite = Palpite.query.filter_by(
        usuario_id=session['user_id'],
        gp_slug=nome_gp
    ).first()

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
    
    # Busca a pontuação da tabela
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    
    # Verifica pole position
    if palpite[13] and resposta[11] and palpite[13] == resposta[11]:  # palpite.pole == resposta.pole
        pontos += pontuacao.get(0, 5)  # Usa 5 como valor padrão se não encontrar na tabela
    
    # Verifica posições
    for i in range(1, 11):
        if palpite[i+2] and resposta[i-1] and palpite[i+2] == resposta[i-1]:  # palpite.pos_X == resposta.pos_X
            pontos += pontuacao.get(i, 0)  # Usa 0 como valor padrão se não encontrar na tabela
    
    return pontos

def is_postgresql():
    return 'postgresql' in app.config['SQLALCHEMY_DATABASE_URI']

def get_db_connection():
    if is_postgresql():
        return psycopg2.connect(app.config['SQLALCHEMY_DATABASE_URI'], client_encoding='utf8')
    else:
        return sqlite3.connect('data/bolao_f1.db')

@app.route('/meus_resultados')
def meus_resultados():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca todos os palpites do usuário com as respostas correspondentes
    palpites = Palpite.query.filter_by(usuario_id=session['user_id']).all()
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    resultados = []
    total_geral = 0
    
    # Processa palpites das corridas principais
    for palpite in palpites:
        # Encontra o nome do GP
        gp_slug = palpite.gp_slug
        gp_nome = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == gp_slug), palpite.gp_slug)
        
        # Calcula os pontos
        pontos_gp = 0
        resposta = respostas.get(palpite.gp_slug)
        
        # Verifica se o GP já tem respostas
        if resposta:
            # Verifica pole position
            if palpite.pole == resposta.pole and resposta.pole is not None:
                if gp_slug.startswith('sprint'):
                    pontos_gp += pontuacao_sprint.get(0, 1)
                else:
                    pontos_gp += pontuacao.get(0, 5)
            
            # Verifica posições
            for i in range(1, 11):
                palpite_pos = getattr(palpite, f'pos_{i}')
                resposta_pos = getattr(resposta, f'pos_{i}')
                if palpite_pos == resposta_pos and resposta_pos is not None:
                    if gp_slug.startswith('sprint'):
                        pontos_gp += pontuacao_sprint.get(i, 0)
                    else:
                        pontos_gp += pontuacao.get(i, 0)
        
        total_geral += pontos_gp
        
        # Adiciona a resposta ao objeto palpite
        palpite.resposta = resposta
        
        resultados.append({
            'gp': gp_nome,
            'palpite': palpite,
            'pontos': pontos_gp,
            'tipo': 'corrida'
        })
    
    # Ordena os resultados por data do GP
    def get_gp_index(resultado):
        return next((i for i, gp in enumerate(gps_2025) if gp[0] == resultado['palpite'].gp_slug), float('inf'))
    
    resultados.sort(key=get_gp_index)
    
    return render_template('meus_resultados.html', 
                         resultados=resultados, 
                         gps_2025=gps_2025,
                         total_geral=total_geral,
                         pontuacao=pontuacao,
                         pontuacao_sprint=pontuacao_sprint)

@app.route('/classificacao')
def classificacao():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca todos os usuários (exceto admin)
    usuarios = Usuario.query.filter(Usuario.username != 'admin').all()
    
    # Busca todos os palpites e respostas
    palpites = Palpite.query.all()
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    classificacao = []
    
    for usuario in usuarios:
        palpites_usuario = [p for p in palpites if p.usuario_id == usuario.id]
        total_pontos = 0
        
        for palpite in palpites_usuario:
            resposta = respostas.get(palpite.gp_slug)
            if resposta:
                # Verifica pole position
                if palpite.pole == resposta.pole and resposta.pole is not None:
                    if palpite.gp_slug.startswith('sprint'):
                        total_pontos += pontuacao_sprint.get(0, 1)
                    else:
                        total_pontos += pontuacao.get(0, 5)
                
                # Verifica posições
                for i in range(1, 11):
                    palpite_pos = getattr(palpite, f'pos_{i}')
                    resposta_pos = getattr(resposta, f'pos_{i}')
                    if palpite_pos == resposta_pos and resposta_pos is not None:
                        if palpite.gp_slug.startswith('sprint'):
                            total_pontos += pontuacao_sprint.get(i, 0)
                        else:
                            total_pontos += pontuacao.get(i, 0)
        
        classificacao.append({
            'username': usuario.username,
            'first_name': usuario.first_name,
            'total_pontos': total_pontos
        })
    
    # Ordena por total de pontos
    classificacao.sort(key=lambda x: x['total_pontos'], reverse=True)
    
    return render_template('classificacao.html', classificacao=classificacao)

# Rota da área administrativa
@app.route('/admin')
@admin_required
def admin():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca todos os usuários
    usuarios = Usuario.query.all()
    
    # Busca todos os pilotos
    pilotos = Piloto.query.order_by(Piloto.nome).all()
    
    # Busca configurações de votação
    configs = {c.gp_slug: {'pole': c.pole_habilitado, 'posicoes': c.posicoes_habilitado} 
              for c in ConfigVotacao.query.all()}
    
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
    
    return render_template('admin.html', gps=gps_com_config, usuarios=usuarios, pilotos=pilotos)

# Rota para editar respostas de um GP
@app.route('/admin/respostas/<nome_gp>', methods=['GET', 'POST'])
@admin_required
def admin_respostas(nome_gp):
    if request.method == 'POST':
        # Verifica se já existe resposta para este GP
        resposta_existente = Resposta.query.filter_by(gp_slug=nome_gp).first()
        
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
            resposta_existente.pos_1 = posicoes[0]
            resposta_existente.pos_2 = posicoes[1]
            resposta_existente.pos_3 = posicoes[2]
            resposta_existente.pos_4 = posicoes[3]
            resposta_existente.pos_5 = posicoes[4]
            resposta_existente.pos_6 = posicoes[5]
            resposta_existente.pos_7 = posicoes[6]
            resposta_existente.pos_8 = posicoes[7]
            resposta_existente.pos_9 = posicoes[8]
            resposta_existente.pos_10 = posicoes[9]
            resposta_existente.pole = pole
        else:
            # Insere nova resposta
            nova_resposta = Resposta(
                gp_slug=nome_gp,
                pos_1=posicoes[0],
                pos_2=posicoes[1],
                pos_3=posicoes[2],
                pos_4=posicoes[3],
                pos_5=posicoes[4],
                pos_6=posicoes[5],
                pos_7=posicoes[6],
                pos_8=posicoes[7],
                pos_9=posicoes[8],
                pos_10=posicoes[9],
                pole=pole
            )
            db.session.add(nova_resposta)
        
        db.session.commit()
        flash('Respostas salvas com sucesso!', 'success')
        
        # Cria uma resposta temporária com os valores salvos
        resposta_temp = posicoes + [pole]
        nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
        
        return render_template('admin_respostas.html',
                             nome_gp=nome_gp,
                             nome_gp_exibicao=nome_gp_exibicao,
                             grid_2025=grid_2025,
                             resposta=resposta_temp)
    
    # Busca resposta existente
    resposta = Resposta.query.filter_by(gp_slug=nome_gp).first()
    
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
        try:
            # Atualiza os valores de pontuação
            for posicao in range(11):  # 0 a 10 (pole + 10 posições)
                pontos = request.form.get(f'pontos_{posicao}')
                if pontos:
                    pontuacao = Pontuacao.query.filter_by(posicao=posicao).first()
                    if pontuacao:
                        pontuacao.pontos = int(pontos)
                    else:
                        nova_pontuacao = Pontuacao(posicao=posicao, pontos=int(pontos))
                        db.session.add(nova_pontuacao)
            
            db.session.commit()
            flash('Pontuação atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar pontuação: {str(e)}', 'error')
    
    # Busca os valores atuais
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    return render_template('admin_pontuacao.html', pontuacao=pontuacao, pontuacao_sprint=pontuacao_sprint)

@app.route('/admin/gerenciar-pilotos', methods=['GET', 'POST'])
@admin_required
def admin_gerenciar_pilotos():
    if request.method == 'POST':
        novo_piloto = request.form.get('novo_piloto')
        piloto = request.form.get('piloto')
        
        if novo_piloto:
            try:
                # Verifica se o piloto já existe na lista grid_2025
                if novo_piloto not in grid_2025:
                    # Adiciona o piloto à lista grid_2025
                    grid_2025.append(novo_piloto)
                    # Adiciona o piloto ao banco de dados
                    piloto = Piloto(nome=novo_piloto)
                    db.session.add(piloto)
                    db.session.commit()
                    flash('Piloto adicionado com sucesso!', 'success')
                else:
                    flash('Este piloto já está cadastrado!', 'error')
            except Exception as e:
                flash(f'Erro ao adicionar piloto: {str(e)}', 'error')
        
        elif piloto:
            try:
                # Remove o piloto da lista grid_2025
                if piloto in grid_2025:
                    grid_2025.remove(piloto)
                # Remove o piloto do banco de dados
                piloto_obj = Piloto.query.filter_by(nome=piloto).first()
                if piloto_obj:
                    db.session.delete(piloto_obj)
                    db.session.commit()
                    flash('Piloto excluído com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao excluir piloto: {str(e)}', 'error')
    
    # Busca todos os pilotos do banco de dados
    pilotos = Piloto.query.order_by(Piloto.nome).all()
    
    # Garante que todos os pilotos da lista grid_2025 estejam no banco de dados
    for piloto_nome in grid_2025:
        piloto = Piloto.query.filter_by(nome=piloto_nome).first()
        if not piloto:
            piloto = Piloto(nome=piloto_nome)
            db.session.add(piloto)
    db.session.commit()
    
    return render_template('admin_gerenciar_pilotos.html', pilotos=pilotos)

@app.route('/admin/gerenciar-usuarios', methods=['GET', 'POST'])
@admin_required
def admin_gerenciar_usuarios():
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        action = request.form.get('action')
        
        if action == 'reset_password':
            # Busca o usuário
            usuario = Usuario.query.get(usuario_id)
            if usuario:
                # Define a nova senha como o username
                usuario.set_password(usuario.username)
                usuario.primeiro_login = True
                db.session.commit()
                flash('Senha resetada com sucesso! A nova senha é igual ao login.', 'success')
        
        elif action == 'delete':
            try:
                usuario = Usuario.query.get(usuario_id)
                if usuario:
                    db.session.delete(usuario)
                    db.session.commit()
                    flash('Usuário excluído com sucesso!', 'success')
            except Exception as e:
                flash(f'Erro ao excluir usuário: {str(e)}', 'error')
    
    # Busca todos os usuários
    usuarios = Usuario.query.all()
    
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
        
        # Busca o usuário
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            flash('Usuário não encontrado!', 'error')
            return redirect(url_for('login'))
        
        # Atualiza a senha e define primeiro_login como False
        usuario.set_password(nova_senha)
        usuario.primeiro_login = False
        db.session.commit()
        
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('tela_gps'))
    
    return render_template('redefinir_senha.html')

def reset_admin_password():
    with app.app_context():
        # Verifica se o admin já existe
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            # Se existir, apenas reseta a senha
            admin.set_password('admin123')
            admin.primeiro_login = True
        else:
            # Se não existir, cria um novo admin
            admin = Usuario(
                username='admin',
                first_name='Administrador',
                is_admin=True,
                primeiro_login=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print("Senha do admin resetada com sucesso!")

@app.route('/admin/resetar-senha/<int:user_id>', methods=['POST'])
@admin_required
def resetar_senha(user_id):
    # Busca o usuário
    usuario = Usuario.query.get(user_id)
    if not usuario:
        flash('Usuário não encontrado!', 'error')
        return redirect(url_for('admin_gerenciar_usuarios'))
    
    # Gera uma senha aleatória
    nova_senha = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    
    # Atualiza a senha e define primeiro_login como True
    usuario.set_password(nova_senha)
    usuario.primeiro_login = True
    db.session.commit()
    
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
        
        # Busca o usuário
        usuario = Usuario.query.get(session['user_id'])
        if not usuario:
            flash('Usuário não encontrado!', 'error')
            return redirect(url_for('login'))
        
        # Verifica a senha atual
        if not usuario.check_password(senha_atual):
            flash('Senha atual incorreta!', 'error')
            return redirect(url_for('alterar_senha'))
            
        if nova_senha != confirmar_senha:
            flash('As senhas não coincidem!', 'error')
            return redirect(url_for('alterar_senha'))
            
        # Atualiza a senha e define primeiro_login como False
        usuario.set_password(nova_senha)
        usuario.primeiro_login = False
        db.session.commit()
        
        flash('Senha alterada com sucesso!', 'success')
        return redirect(url_for('index'))
        
    return render_template('alterar_senha.html')

# Rota para Resultados Parciais por Corrida
@app.route('/resultados-parciais')
def resultados_parciais():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca todos os usuários (exceto admin)
    usuarios = Usuario.query.filter(Usuario.username != 'admin').all()
    
    # Busca todos os palpites e respostas
    palpites = Palpite.query.all()
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    classificacao = []
    
    for usuario in usuarios:
        usuario_info = {
            'first_name': usuario.first_name,
            'total_pontos': 0,
            'pontos_por_gp': {}
        }
        
        # Inicializa pontos por GP
        for gp_slug, _, _, _, _, _ in gps_2025:
            usuario_info['pontos_por_gp'][gp_slug] = 0
        
        # Calcula pontos para cada GP
        palpites_usuario = [p for p in palpites if p.usuario_id == usuario.id]
        for palpite in palpites_usuario:
            pontos_gp = 0
            resposta = respostas.get(palpite.gp_slug)
            
            if resposta:
                # Verifica pole position
                if palpite.pole == resposta.pole and resposta.pole is not None:
                    if palpite.gp_slug.startswith('sprint'):
                        pontos_gp += pontuacao_sprint.get(0, 1)
                    else:
                        pontos_gp += pontuacao.get(0, 5)
                
                # Verifica posições
                for i in range(1, 11):
                    palpite_pos = getattr(palpite, f'pos_{i}')
                    resposta_pos = getattr(resposta, f'pos_{i}')
                    if palpite_pos == resposta_pos and resposta_pos is not None:
                        if palpite.gp_slug.startswith('sprint'):
                            pontos_gp += pontuacao_sprint.get(i, 0)
                        else:
                            pontos_gp += pontuacao.get(i, 0)
            
            usuario_info['pontos_por_gp'][palpite.gp_slug] = pontos_gp
            usuario_info['total_pontos'] += pontos_gp
        
        classificacao.append(usuario_info)
    
    # Ordena por total de pontos
    classificacao.sort(key=lambda x: x['total_pontos'], reverse=True)
    
    return render_template('resultados_parciais.html', 
                         classificacao=classificacao, 
                         gps=gps_2025)

# Rota para Configurações do Sistema
@app.route('/admin/configuracoes', methods=['GET', 'POST'])
@admin_required
def admin_configuracoes():
    if request.method == 'POST':
        for gp in gps_2025:
            slug = gp[0]
            pole_habilitado = request.form.get(f'pole_{slug}') == 'on'
            posicoes_habilitado = request.form.get(f'posicoes_{slug}') == 'on'
            
            # Busca ou cria configuração para o GP
            config = ConfigVotacao.query.filter_by(gp_slug=slug).first()
            if not config:
                config = ConfigVotacao(gp_slug=slug)
                db.session.add(config)
            
            config.pole_habilitado = pole_habilitado
            config.posicoes_habilitado = posicoes_habilitado
        
        db.session.commit()
        flash('Configurações salvas com sucesso!', 'success')
        return redirect(url_for('admin_configuracoes'))
    
    # Buscar configurações atuais
    configs = {c.gp_slug: {'pole': c.pole_habilitado, 'posicoes': c.posicoes_habilitado} 
              for c in ConfigVotacao.query.all()}
    
    # Preparar lista de GPs com suas configurações
    gps = []
    for gp in gps_2025:
        slug, nome, data_corrida, hora_corrida, data_classificacao, hora_classificacao = gp
        config = configs.get(slug, {'pole': False, 'posicoes': False})
        
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
        # Se for uma requisição de sincronização
        if request.form.get('action') == 'sincronizar':
            sincronizar_gps_banco()
            flash('GPs sincronizados com sucesso!', 'success')
            return redirect(url_for('admin_datas_gps'))
            
        # Processamento normal do formulário
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
        
        # Converte as datas do formato DD/MM/YYYY para YYYY-MM-DD
        data_corrida = datas.get('data_corrida', '')
        if data_corrida:
            try:
                data_corrida = datetime.strptime(data_corrida, '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                data_corrida = ''
        
        data_classificacao = datas.get('data_classificacao', '')
        if data_classificacao:
            try:
                data_classificacao = datetime.strptime(data_classificacao, '%d/%m/%Y').strftime('%Y-%m-%d')
            except:
                data_classificacao = ''
        
        gps_com_datas.append({
            'slug': slug,
            'nome': gp[1],
            'data_corrida': data_corrida,
            'hora_corrida': datas.get('hora_corrida', ''),
            'data_classificacao': data_classificacao,
            'hora_classificacao': datas.get('hora_classificacao', '')
        })
    
    return render_template('admin_datas_gps.html', gps=gps_com_datas)

def criar_admin():
    # Verifica se o admin já existe
    admin = Usuario.query.filter_by(username='admin').first()
    
    if not admin:
        # Cria o usuário admin com senha 'admin8163'
        admin = Usuario(
            username='admin',
            first_name='Administrador',
            is_admin=True,
            primeiro_login=True
        )
        admin.set_password('admin8163')
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
        print("Login: admin")
        print("Senha: admin8163")
    else:
        print("Usuário admin já existe!")

# Rota para exibir resultados de um GP
@app.route('/resultados/<nome_gp>')
def resultados(nome_gp):
    # Busca a resposta correta
    resposta = Resposta.query.filter_by(gp_slug=nome_gp).first()
    if not resposta:
        flash('Resultados ainda não disponíveis para este GP!', 'error')
        return redirect(url_for('tela_gps'))
    
    # Busca todos os palpites para este GP
    palpites = Palpite.query.filter_by(gp_slug=nome_gp).all()
    
    # Busca a pontuação
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    
    # Calcula pontuação para cada palpite
    resultados = []
    for palpite in palpites:
        pontos = 0
        
        # Verifica pole position
        if palpite.pole == resposta.pole:
            pontos += pontuacao.get(0, 0)
        
        # Verifica posições
        for i in range(1, 11):
            palpite_pos = getattr(palpite, f'pos_{i}')
            resposta_pos = getattr(resposta, f'pos_{i}')
            if palpite_pos == resposta_pos:
                pontos += pontuacao.get(i, 0)
        
        resultados.append({
            'usuario': palpite.usuario.username,
            'palpite': palpite,
            'pontos': pontos
        })
    
    # Ordena por pontuação (maior para menor)
    resultados.sort(key=lambda x: x['pontos'], reverse=True)
    
    nome_gp_exibicao = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == nome_gp), "GP Desconhecido")
    
    return render_template('resultados.html',
                         nome_gp=nome_gp,
                         nome_gp_exibicao=nome_gp_exibicao,
                         resposta=resposta,
                         resultados=resultados)

@app.route('/ranking')
def ranking():
    # Busca todos os GPs com respostas
    gps_com_respostas = [gp[0] for gp in gps_2025 
                        if Resposta.query.filter_by(gp_slug=gp[0]).first()]
    
    # Busca todos os usuários
    usuarios = Usuario.query.filter(Usuario.username != 'admin').all()
    
    # Busca todos os palpites
    palpites = Palpite.query.all()
    
    # Busca todas as respostas
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    
    # Busca a pontuação
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    
    # Calcula pontuação total para cada usuário
    ranking = []
    for usuario in usuarios:
        pontos_total = 0
        palpites_usuario = [p for p in palpites if p.usuario_id == usuario.id]
        
        for palpite in palpites_usuario:
            resposta = respostas.get(palpite.gp_slug)
            if not resposta:
                continue
            
            # Verifica pole position
            if palpite.pole == resposta.pole:
                pontos_total += pontuacao.get(0, 0)
            
            # Verifica posições
            for i in range(1, 11):
                palpite_pos = getattr(palpite, f'pos_{i}')
                resposta_pos = getattr(resposta, f'pos_{i}')
                if palpite_pos == resposta_pos:
                    pontos_total += pontuacao.get(i, 0)
        
        ranking.append({
            'usuario': usuario.username,
            'pontos': pontos_total,
            'palpites': len(palpites_usuario)
        })
    
    # Ordena por pontuação (maior para menor)
    ranking.sort(key=lambda x: x['pontos'], reverse=True)
    
    return render_template('ranking.html',
                         ranking=ranking,
                         total_gps=len(gps_com_respostas))

@app.route('/admin/gerenciar-gps', methods=['GET', 'POST'])
@admin_required
def admin_gerenciar_gps():
    if request.method == 'POST':
        # Se for uma requisição de sincronização
        if request.form.get('action') == 'sincronizar':
            sincronizar_gps_banco()
            flash('GPs sincronizados com sucesso!', 'success')
            return redirect(url_for('admin_gerenciar_gps'))
            
        # Se for uma requisição de adicionar GP
        if request.form.get('action') == 'add':
            nome = request.form.get('nome')
            data = request.form.get('data')
            
            if nome and data:
                try:
                    # Cria o slug a partir do nome
                    slug = nome.lower().replace(' ', '-')
                    
                    # Verifica se o GP já existe
                    gp = GP.query.filter_by(slug=slug).first()
                    if not gp:
                        gp = GP(
                            slug=slug,
                            nome=nome,
                            data_corrida=data,
                            hora_corrida="12:00",
                            data_classificacao=data,
                            hora_classificacao="12:00"
                        )
                        db.session.add(gp)
                        db.session.commit()
                        flash('GP adicionado com sucesso!', 'success')
                    else:
                        flash('Este GP já está cadastrado!', 'error')
                except Exception as e:
                    flash(f'Erro ao adicionar GP: {str(e)}', 'error')
            
        # Se for uma requisição de excluir GP
        if request.form.get('action') == 'delete':
            gp_id = request.form.get('gp_id')
            if gp_id:
                try:
                    gp = GP.query.get(gp_id)
                    if gp:
                        db.session.delete(gp)
                        db.session.commit()
                        flash('GP excluído com sucesso!', 'success')
                except Exception as e:
                    flash(f'Erro ao excluir GP: {str(e)}', 'error')
    
    # Busca todos os GPs
    gps = GP.query.all()
    
    return render_template('admin_gerenciar_gps.html', gps=gps)

@app.route('/calendario')
def calendario():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Buscar todos os GPs do banco de dados
    gps = GP.query.order_by(GP.data_corrida).all()
    
    # Definir o fuso horário de Brasília
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    
    # Data atual no fuso horário de Brasília
    hoje = datetime.now(tz_brasilia).date()
    
    # Converter as datas dos GPs para objetos datetime.date
    for gp in gps:
        try:
            # Converter data_corrida
            if isinstance(gp.data_corrida, str):
                gp.data_corrida = datetime.strptime(gp.data_corrida, '%d/%m/%Y').date()
            
            # Converter data_classificacao
            if isinstance(gp.data_classificacao, str):
                gp.data_classificacao = datetime.strptime(gp.data_classificacao, '%d/%m/%Y').date()
            
            # Calcular se o GP está próximo (3 dias antes)
            dias_para_corrida = (gp.data_corrida - hoje).days
            gp.esta_proximo = 0 <= dias_para_corrida <= 3
            
        except (ValueError, TypeError) as e:
            print(f"Erro ao converter data do GP {gp.nome}: {str(e)}")
            gp.data_corrida = hoje
            gp.data_classificacao = hoje
            gp.esta_proximo = False
    
    # Ordenar os GPs por data da corrida
    gps_ordenados = sorted(gps, key=lambda x: x.data_corrida)
    
    return render_template('calendario.html', gps=gps_ordenados, date_now=hoje)

@app.route('/sprint/<nome_gp>', methods=['GET', 'POST'])
def tela_palpite_sprint(nome_gp):
    if 'username' not in session:
        return redirect(url_for('login'))

    mensagem = None
    tipo_mensagem = None

    # Buscar informações do sprint
    sprint_info = next((s for s in sprints_2025 if s[0] == nome_gp), None)
    if not sprint_info:
        flash('Sprint não encontrado!', 'error')
        return redirect(url_for('tela_gps'))

    # Verifica horário dos palpites
    pole_habilitado, posicoes_habilitado = verificar_horario_palpites(
        sprint_info[4],  # data_classificacao
        sprint_info[5],  # hora_classificacao
        sprint_info[2],  # data_corrida
        sprint_info[3]   # hora_corrida
    )

    if request.method == "POST":
        print(f"Processando POST para Sprint {nome_gp}")
        print(f"Dados do formulário: {request.form}")
        
        # Verifica se já existe um palpite para este Sprint
        palpite_existente = PalpiteSprint.query.filter_by(
            usuario_id=session['user_id'],
            gp_slug=nome_gp
        ).first()
        
        print(f"Palpite existente: {palpite_existente}")
        
        # Verifica se está tentando votar apenas na pole position
        pole = request.form.get('pole')
        posicoes = [request.form.get(f'pos_{i}') for i in range(1, 11)]
        tem_pole = bool(pole)
        tem_posicoes = any(posicoes)
        
        print(f"Pole: {pole}")
        print(f"Posições: {posicoes}")
        print(f"Tem pole: {tem_pole}")
        print(f"Tem posições: {tem_posicoes}")
        
        if palpite_existente:
            # Se já tem palpite completo, não permite alteração
            if palpite_existente.pole and palpite_existente.pos_1:
                mensagem = 'Você já fez seu palpite completo para este Sprint!'
                tipo_mensagem = 'error'
            # Se tem apenas pole position, permite adicionar posições
            elif palpite_existente.pole and not palpite_existente.pos_1:
                if tem_pole:
                    mensagem = 'Você já votou na pole position!'
                    tipo_mensagem = 'error'
                elif not posicoes_habilitado:
                    mensagem = 'A votação para as posições está desabilitada!'
                    tipo_mensagem = 'error'
                else:
                    try:
                        # Atualiza apenas as posições
                        palpite_existente.pos_1 = posicoes[0]
                        palpite_existente.pos_2 = posicoes[1]
                        palpite_existente.pos_3 = posicoes[2]
                        palpite_existente.pos_4 = posicoes[3]
                        palpite_existente.pos_5 = posicoes[4]
                        palpite_existente.pos_6 = posicoes[5]
                        palpite_existente.pos_7 = posicoes[6]
                        palpite_existente.pos_8 = posicoes[7]
                        palpite_existente.pos_9 = posicoes[8]
                        palpite_existente.pos_10 = posicoes[9]
                        db.session.commit()
                        mensagem = 'Posições salvas com sucesso!'
                        tipo_mensagem = 'success'
                        print("Posições atualizadas com sucesso")
                    except Exception as e:
                        print(f"Erro ao atualizar posições: {str(e)}")
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
                        palpite_existente.pos_1 = posicoes[0]
                        palpite_existente.pos_2 = posicoes[1]
                        palpite_existente.pos_3 = posicoes[2]
                        palpite_existente.pos_4 = posicoes[3]
                        palpite_existente.pos_5 = posicoes[4]
                        palpite_existente.pos_6 = posicoes[5]
                        palpite_existente.pos_7 = posicoes[6]
                        palpite_existente.pos_8 = posicoes[7]
                        palpite_existente.pos_9 = posicoes[8]
                        palpite_existente.pos_10 = posicoes[9]
                        db.session.commit()
                        mensagem = 'Posições salvas com sucesso!'
                        tipo_mensagem = 'success'
                        print("Posições atualizadas com sucesso")
                    except Exception as e:
                        print(f"Erro ao atualizar posições: {str(e)}")
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
                    novo_palpite = PalpiteSprint(
                        usuario_id=session['user_id'],
                        gp_slug=nome_gp,
                        pos_1=posicoes[0],
                        pos_2=posicoes[1],
                        pos_3=posicoes[2],
                        pos_4=posicoes[3],
                        pos_5=posicoes[4],
                        pos_6=posicoes[5],
                        pos_7=posicoes[6],
                        pos_8=posicoes[7],
                        pos_9=posicoes[8],
                        pos_10=posicoes[9],
                        pole=pole
                    )
                    db.session.add(novo_palpite)
                    db.session.commit()
                    mensagem = 'Palpite salvo com sucesso!'
                    tipo_mensagem = 'success'
                    print("Novo palpite inserido com sucesso")
                except Exception as e:
                    print(f"Erro ao inserir novo palpite: {str(e)}")
                    mensagem = 'Erro ao salvar o palpite!'
                    tipo_mensagem = 'error'

    # Busca palpite existente
    palpite = PalpiteSprint.query.filter_by(
        usuario_id=session['user_id'],
        gp_slug=nome_gp
    ).first()

    print(f"Palpite encontrado para exibição: {palpite}")

    return render_template(
        'tela_palpite_sprint.html',
        nome_gp=nome_gp,
        nome_gp_exibicao=sprint_info[1],
        data_corrida=sprint_info[2],
        hora_corrida=sprint_info[3],
        data_classificacao=sprint_info[4],
        hora_classificacao=sprint_info[5],
        grid_2025=grid_2025,
        palpite=palpite,
        pole_habilitado=pole_habilitado,
        posicoes_habilitado=posicoes_habilitado,
        mensagem=mensagem,
        tipo_mensagem=tipo_mensagem
    )

@app.route('/meus-resultados-sprint')
def meus_resultados_sprint():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca todos os palpites do usuário da tabela palpites_sprint
    palpites = PalpiteSprint.query.filter_by(usuario_id=session['user_id']).all()
    
    # Busca todas as respostas da tabela respostas_sprint
    respostas = {r.gp_slug: r for r in RespostaSprint.query.all()}
    pontuacao = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    resultados = []
    total_geral = 0
    
    for palpite in palpites:
        # Encontra o nome do GP
        gp_slug = palpite.gp_slug
        gp_nome = next((nome for slug, nome, _, _, _, _ in sprints_2025 if slug == gp_slug), palpite.gp_slug)
        
        # Calcula os pontos
        pontos_gp = 0
        resposta = respostas.get(gp_slug)
        
        # Verifica se o GP já tem respostas
        if resposta:
            # Verifica pole position
            if palpite.pole == resposta.pole and resposta.pole is not None:
                pontos_gp += pontuacao.get(0, 1)  # 1 ponto para pole position
            
            # Verifica posições (apenas até 8º lugar para sprints)
            for i in range(1, 9):
                palpite_pos = getattr(palpite, f'pos_{i}')
                resposta_pos = getattr(resposta, f'pos_{i}')
                if palpite_pos == resposta_pos and resposta_pos is not None:
                    pontos_gp += pontuacao.get(i, 0)
        
        total_geral += pontos_gp
        
        # Adiciona a resposta ao objeto palpite
        palpite.resposta = resposta
        
        resultados.append({
            'gp': f"Sprint - {gp_nome}",
            'palpite': palpite,
            'pontos': pontos_gp
        })
    
    # Ordena os resultados por data do GP (usando a ordem definida em sprints_2025)
    resultados.sort(key=lambda x: next((i for i, gp in enumerate(sprints_2025) if gp[0] == x['palpite'].gp_slug), float('inf')))
    
    return render_template('meus_resultados_sprint.html', 
                         resultados=resultados, 
                         gps_2025=sprints_2025, 
                         total_geral=total_geral,
                         pontuacao=pontuacao)

@app.route('/salvar_palpite_sprint/<nome_gp>', methods=['POST'])
def salvar_palpite_sprint(nome_gp):
    if 'username' not in session:
        return redirect(url_for('login'))

    mensagem = None
    tipo_mensagem = None

    # Buscar informações do sprint
    sprint_info = next((s for s in sprints_2025 if s[0] == nome_gp), None)
    if not sprint_info:
        flash('Sprint não encontrado!', 'error')
        return redirect(url_for('tela_gps'))

    # Verifica horário dos palpites
    pole_habilitado, posicoes_habilitado = verificar_horario_palpites(
        sprint_info[4],  # data_classificacao
        sprint_info[5],  # hora_classificacao
        sprint_info[2],  # data_corrida
        sprint_info[3]   # hora_corrida
    )

    # Verifica se já existe um palpite para este Sprint
    palpite_existente = PalpiteSprint.query.filter_by(
        usuario_id=session['user_id'],
        gp_slug=nome_gp  # Removido o prefixo sprint_
    ).first()
    
    # Verifica se está tentando votar apenas na pole position
    pole = request.form.get('pole')
    posicoes = [request.form.get(f'pos_{i}') for i in range(1, 11)]
    tem_pole = bool(pole)
    tem_posicoes = any(posicoes)
    
    if palpite_existente:
        # Se já tem palpite completo, não permite alteração
        if palpite_existente.pole and palpite_existente.pos_1:
            flash('Você já fez seu palpite completo para este Sprint!', 'error')
            return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))
        # Se tem apenas pole position, permite adicionar posições
        elif palpite_existente.pole and not palpite_existente.pos_1:
            if tem_pole:
                flash('Você já votou na pole position!', 'error')
                return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))
            elif not posicoes_habilitado:
                flash('A votação para as posições está desabilitada!', 'error')
                return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))
            else:
                try:
                    # Atualiza apenas as posições
                    palpite_existente.pos_1 = posicoes[0]
                    palpite_existente.pos_2 = posicoes[1]
                    palpite_existente.pos_3 = posicoes[2]
                    palpite_existente.pos_4 = posicoes[3]
                    palpite_existente.pos_5 = posicoes[4]
                    palpite_existente.pos_6 = posicoes[5]
                    palpite_existente.pos_7 = posicoes[6]
                    palpite_existente.pos_8 = posicoes[7]
                    palpite_existente.pos_9 = posicoes[8]
                    palpite_existente.pos_10 = posicoes[9]
                    db.session.commit()
                    flash('Posições salvas com sucesso!', 'success')
                except Exception as e:
                    flash('Erro ao salvar as posições!', 'error')
    else:
        # Insere novo palpite
        if tem_posicoes and not posicoes_habilitado:
            flash('A votação para as posições está desabilitada!', 'error')
            return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))
        elif tem_pole and not pole_habilitado:
            flash('A votação para pole position está desabilitada!', 'error')
            return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))
        else:
            try:
                novo_palpite = PalpiteSprint(
                    usuario_id=session['user_id'],
                    gp_slug=nome_gp,  # Removido o prefixo sprint_
                    pos_1=posicoes[0],
                    pos_2=posicoes[1],
                    pos_3=posicoes[2],
                    pos_4=posicoes[3],
                    pos_5=posicoes[4],
                    pos_6=posicoes[5],
                    pos_7=posicoes[6],
                    pos_8=posicoes[7],
                    pos_9=posicoes[8],
                    pos_10=posicoes[9],
                    pole=pole
                )
                db.session.add(novo_palpite)
                db.session.commit()
                flash('Palpite salvo com sucesso!', 'success')
            except Exception as e:
                flash('Erro ao salvar o palpite!', 'error')

    return redirect(url_for('tela_palpite_sprint', nome_gp=nome_gp))

@app.route('/admin/pontuacao-sprint', methods=['GET', 'POST'])
@admin_required
def admin_pontuacao_sprint():
    if request.method == 'POST':
        try:
            # Atualiza os valores de pontuação
            for posicao in range(9):  # 0 a 8 (pole + 8 posições)
                pontos = request.form.get(f'pontos_{posicao}')
                if pontos:
                    pontuacao = PontuacaoSprint.query.filter_by(posicao=posicao).first()
                    if pontuacao:
                        pontuacao.pontos = int(pontos)
                    else:
                        nova_pontuacao = PontuacaoSprint(posicao=posicao, pontos=int(pontos))
                        db.session.add(nova_pontuacao)
            
            db.session.commit()
            flash('Pontuação das sprints atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f'Erro ao atualizar pontuação das sprints: {str(e)}', 'error')
    
    # Busca os valores atuais
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    return render_template('admin_pontuacao.html', pontuacao=pontuacao, pontuacao_sprint=pontuacao_sprint)

@app.route('/resultados_usuario/<username>')
def resultados_usuario(username):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    # Busca o usuário pelo username
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        flash('Usuário não encontrado!', 'error')
        return redirect(url_for('classificacao'))
    
    # Busca todos os palpites do usuário com as respostas correspondentes
    palpites = Palpite.query.filter_by(usuario_id=usuario.id).all()
    respostas = {r.gp_slug: r for r in Resposta.query.all()}
    pontuacao = {p.posicao: p.pontos for p in Pontuacao.query.all()}
    pontuacao_sprint = {p.posicao: p.pontos for p in PontuacaoSprint.query.all()}
    
    resultados = []
    total_geral = 0
    
    # Processa palpites das corridas principais
    for palpite in palpites:
        # Encontra o nome do GP
        gp_slug = palpite.gp_slug
        gp_nome = next((nome for slug, nome, _, _, _, _ in gps_2025 if slug == gp_slug), palpite.gp_slug)
        
        # Calcula os pontos
        pontos_gp = 0
        resposta = respostas.get(palpite.gp_slug)
        
        # Verifica se o GP já tem respostas
        if resposta:
            # Verifica pole position
            if palpite.pole == resposta.pole and resposta.pole is not None:
                if gp_slug.startswith('sprint'):
                    pontos_gp += pontuacao_sprint.get(0, 1)
                else:
                    pontos_gp += pontuacao.get(0, 5)
            
            # Verifica posições
            for i in range(1, 11):
                palpite_pos = getattr(palpite, f'pos_{i}')
                resposta_pos = getattr(resposta, f'pos_{i}')
                if palpite_pos == resposta_pos and resposta_pos is not None:
                    if gp_slug.startswith('sprint'):
                        pontos_gp += pontuacao_sprint.get(i, 0)
                    else:
                        pontos_gp += pontuacao.get(i, 0)
        
        total_geral += pontos_gp
        
        # Adiciona a resposta ao objeto palpite
        palpite.resposta = resposta
        
        resultados.append({
            'gp': gp_nome,
            'palpite': palpite,
            'pontos': pontos_gp,
            'tipo': 'corrida'
        })
    
    # Ordena os resultados por data do GP
    def get_gp_index(resultado):
        return next((i for i, gp in enumerate(gps_2025) if gp[0] == resultado['palpite'].gp_slug), float('inf'))
    
    resultados.sort(key=get_gp_index)
    
    return render_template('meus_resultados.html', 
                         resultados=resultados, 
                         gps_2025=gps_2025,
                         total_geral=total_geral,
                         pontuacao=pontuacao,
                         pontuacao_sprint=pontuacao_sprint,
                         usuario_visualizado=usuario)

if __name__ == "__main__":
    criar_admin()  # Cria o usuário admin se não existir
    app.run(debug=True, host='0.0.0.0', port=5000)
