from flask import Flask
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def check_db():
    with app.app_context():
        # Verifica se as tabelas existem
        print("\nVerificando tabelas no banco de dados:")
        print("-" * 50)
        
        # Verifica cada tabela
        tabelas = {
            'usuarios': Usuario,
            'pilotos': Piloto,
            'palpites': Palpite,
            'respostas': Resposta,
            'pontuacao': Pontuacao,
            'config_votacao': ConfigVotacao,
            'gps': GP
        }
        
        for nome, modelo in tabelas.items():
            try:
                count = modelo.query.count()
                print(f"Tabela '{nome}': {count} registros")
            except Exception as e:
                print(f"Tabela '{nome}': Erro ao verificar - {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    check_db() 