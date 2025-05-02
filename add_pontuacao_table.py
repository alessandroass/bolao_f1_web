from flask import Flask
from models import db, Pontuacao
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def add_pontuacao_table():
    with app.app_context():
        # Verifica se a tabela já existe e tem dados
        if Pontuacao.query.count() > 0:
            print("Tabela de pontuação já existe e tem dados!")
            return
        
        # Cria os registros de pontuação
        pontos = [
            (1, 25), (2, 18), (3, 15), (4, 12), (5, 10),
            (6, 8), (7, 6), (8, 4), (9, 2), (10, 1)
        ]
        
        for posicao, pontos in pontos:
            pontuacao = Pontuacao(posicao=posicao, pontos=pontos)
            db.session.add(pontuacao)
        
        db.session.commit()
        print("Tabela de pontuação criada e inicializada com sucesso!")

if __name__ == "__main__":
    add_pontuacao_table() 