from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Temporada(db.Model):
    """Modelo para gerenciar temporadas/anos do bolão"""
    __tablename__ = 'temporadas'
    
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, unique=True, nullable=False)
    ativa = db.Column(db.Boolean, default=False)  # Apenas uma temporada pode estar ativa
    arquivada = db.Column(db.Boolean, default=False)  # True quando a temporada terminou
    data_inicio = db.Column(db.DateTime, nullable=True)
    data_fim = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    campeoes = db.relationship('CampeaoTemporada', backref='temporada', lazy=True)
    
    def __repr__(self):
        return f'<Temporada {self.ano}>'

class CampeaoTemporada(db.Model):
    """Modelo para guardar os campeões de cada temporada"""
    __tablename__ = 'campeoes_temporada'
    
    id = db.Column(db.Integer, primary_key=True)
    temporada_id = db.Column(db.Integer, db.ForeignKey('temporadas.id'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    posicao = db.Column(db.Integer, nullable=False)  # 1, 2, 3 para pódio
    pontos_total = db.Column(db.Integer, nullable=False)
    
    usuario = db.relationship('Usuario', backref=db.backref('titulos', lazy=True))

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

class Equipe(db.Model):
    __tablename__ = 'equipes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    piloto1_id = db.Column(db.Integer, db.ForeignKey('pilotos.id'), nullable=True)
    piloto2_id = db.Column(db.Integer, db.ForeignKey('pilotos.id'), nullable=True)
    
    piloto1 = db.relationship('Piloto', foreign_keys=[piloto1_id], backref='equipe_piloto1')
    piloto2 = db.relationship('Piloto', foreign_keys=[piloto2_id], backref='equipe_piloto2')
    
    def __repr__(self):
        return f'<Equipe {self.nome}>'

class Piloto(db.Model):
    __tablename__ = 'pilotos'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)

class Palpite(db.Model):
    __tablename__ = 'palpites'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    gp_slug = db.Column(db.String(80), nullable=False)
    temporada_ano = db.Column(db.Integer, default=2025)  # Ano da temporada
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
        db.UniqueConstraint('usuario_id', 'gp_slug', 'temporada_ano', name='uq_usuario_gp_temporada'),
    )
    
    usuario = db.relationship('Usuario', backref=db.backref('palpites', lazy=True))

class Resposta(db.Model):
    __tablename__ = 'respostas'
    
    id = db.Column(db.Integer, primary_key=True)
    gp_slug = db.Column(db.String(80), nullable=False)
    temporada_ano = db.Column(db.Integer, default=2025)  # Ano da temporada
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
        db.UniqueConstraint('gp_slug', 'temporada_ano', name='uq_gp_temporada'),
    )

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
    slug = db.Column(db.String(80), nullable=False)
    temporada_ano = db.Column(db.Integer, default=2025)  # Ano da temporada
    nome = db.Column(db.String(80), nullable=False)
    data_corrida = db.Column(db.String(10), nullable=False)
    hora_corrida = db.Column(db.String(5), nullable=False)
    data_classificacao = db.Column(db.String(10), nullable=False)
    hora_classificacao = db.Column(db.String(5), nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('slug', 'temporada_ano', name='uq_gp_slug_temporada'),
    )

class PontuacaoSprint(db.Model):
    __tablename__ = 'pontuacao_sprint'
    
    id = db.Column(db.Integer, primary_key=True)
    posicao = db.Column(db.Integer, unique=True, nullable=False)
    pontos = db.Column(db.Integer, nullable=False)


class PalpiteSprint(db.Model):
    __tablename__ = 'palpites_sprint'
    
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
    
    usuario = db.relationship('Usuario', backref=db.backref('palpites_sprint', lazy=True))


class RespostaSprint(db.Model):
    __tablename__ = 'respostas_sprint'
    
    id = db.Column(db.Integer, primary_key=True)
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


class EquipeTemporada(db.Model):
    """Snapshot das equipes e seus pilotos em cada temporada - protege o histórico"""
    __tablename__ = 'equipes_temporada'
    
    id = db.Column(db.Integer, primary_key=True)
    temporada_ano = db.Column(db.Integer, nullable=False)
    equipe_nome = db.Column(db.String(100), nullable=False)
    piloto1_nome = db.Column(db.String(80), nullable=True)
    piloto2_nome = db.Column(db.String(80), nullable=True)
    
    __table_args__ = (
        db.UniqueConstraint('temporada_ano', 'equipe_nome', name='uq_equipe_temporada'),
    )
    
    def __repr__(self):
        return f'<EquipeTemporada {self.equipe_nome} - {self.temporada_ano}>'