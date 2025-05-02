from flask import Flask
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP
from config import Config

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
                (1, 25), (2, 18), (3, 15), (4, 12), (5, 10),
                (6, 8), (7, 6), (8, 4), (9, 2), (10, 1)
            ]
            for posicao, pontos in pontos:
                pontuacao = Pontuacao(posicao=posicao, pontos=pontos)
                db.session.add(pontuacao)
            
            db.session.commit()
            print("Tabela de pontuação inicializada com sucesso!")

if __name__ == "__main__":
    create_tables() 