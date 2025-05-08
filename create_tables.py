from flask import Flask
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP, PontuacaoSprint
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_tables():
    with app.app_context():
        # Cria todas as tabelas definidas nos modelos
        db.create_all()
        
        # Inicializa a tabela de pontuação se estiver vazia
        if Pontuacao.query.count() == 0:
            pontos = [
                (0, 5),  # Pole Position
                (1, 25), (2, 18), (3, 15), (4, 12), (5, 10),
                (6, 8), (7, 6), (8, 4), (9, 2), (10, 1)
            ]
            for posicao, pontos in pontos:
                pontuacao = Pontuacao(posicao=posicao, pontos=pontos)
                db.session.add(pontuacao)
            
            db.session.commit()
            print("Tabela de pontuação inicializada com sucesso!")
        
        # Se estiver em produção (Render) ou se for solicitado explicitamente
        if os.getenv('FLASK_ENV') == 'production' or os.getenv('UPDATE_SPRINT_POINTS') == 'true':
            # Limpa a tabela de pontuação de sprint
            PontuacaoSprint.query.delete()
            db.session.commit()
            
            # Inicializa a tabela de pontuação de sprint
            pontos_sprint = [
                (0, 1),   # Pole Position
                (1, 8),   # 1º lugar
                (2, 7),   # 2º lugar
                (3, 6),   # 3º lugar
                (4, 5),   # 4º lugar
                (5, 4),   # 5º lugar
                (6, 3),   # 6º lugar
                (7, 2),   # 7º lugar
                (8, 1)    # 8º lugar
            ]
            for posicao, pontos in pontos_sprint:
                pontuacao = PontuacaoSprint(posicao=posicao, pontos=pontos)
                db.session.add(pontuacao)
            
            db.session.commit()
            print("Tabela de pontuação de sprint inicializada com sucesso!")

if __name__ == "__main__":
    create_tables() 