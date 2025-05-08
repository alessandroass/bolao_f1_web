from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    first_name = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(500), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    primeiro_login = db.Column(db.Boolean, default=True)
    
    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256')
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

class Piloto(db.Model):
    __tablename__ = 'pilotos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)

class Palpite(db.Model):
    __tablename__ = 'palpites'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    gp_slug = db.Column(db.String(80), nullable=False)
    pos_1 = db.Column(db.String(80))
    pos_2 = db.Column(db.String(80))
    pos_3 = db.Column(db.String(80))
    pos_4 = db.Column(db.String(80))
    pos_5 = db.Column(db.String(80))
    pos_6 = db.Column(db.String(80))
    pos_7 = db.Column(db.String(80))
    pos_8 = db.Column(db.String(80))
    pos_9 = db.Column(db.String(80))
    pos_10 = db.Column(db.String(80))
    pole = db.Column(db.String(80))
    
    __table_args__ = (
        db.UniqueConstraint('usuario_id', 'gp_slug', name='uq_usuario_gp'),
    )
    
    usuario = db.relationship('Usuario', backref=db.backref('palpites', lazy=True))

class Resposta(db.Model):
    __tablename__ = 'respostas'
    
    id = db.Column(db.Integer, primary_key=True)
    gp_slug = db.Column(db.String(80), unique=True, nullable=False)
    pos_1 = db.Column(db.String(80))
    pos_2 = db.Column(db.String(80))
    pos_3 = db.Column(db.String(80))
    pos_4 = db.Column(db.String(80))
    pos_5 = db.Column(db.String(80))
    pos_6 = db.Column(db.String(80))
    pos_7 = db.Column(db.String(80))
    pos_8 = db.Column(db.String(80))
    pos_9 = db.Column(db.String(80))
    pos_10 = db.Column(db.String(80))
    pole = db.Column(db.String(80))

class Pontuacao(db.Model):
    __tablename__ = 'pontuacao'
    
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, unique=True, nullable=False)
    pontos = db.Column(db.Integer, nullable=False)

class ConfigVotacao(db.Model):
    __tablename__ = 'config_votacao'
    
    id = db.Column(db.Integer, primary_key=True)
    gp_slug = db.Column(db.String(80), unique=True, nullable=False)
    pole_habilitado = db.Column(db.Boolean, default=True)
    posicoes_habilitado = db.Column(db.Boolean, default=True)

class GP(db.Model):
    __tablename__ = 'gps'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    nome = db.Column(db.String(80), nullable=False)
    data_corrida = db.Column(db.String(10), nullable=False)
    hora_corrida = db.Column(db.String(5), nullable=False)
    data_classificacao = db.Column(db.String(10), nullable=False)
    hora_classificacao = db.Column(db.String(5), nullable=False)

class PontuacaoSprint(db.Model):
    __tablename__ = 'pontuacao_sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, unique=True, nullable=False)
    pontos = db.Column(db.Integer, nullable=False) 