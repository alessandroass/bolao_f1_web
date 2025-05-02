from flask import Flask
from models import db, Piloto
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def check_pilotos():
    with app.app_context():
        # Busca todos os pilotos
        pilotos = Piloto.query.order_by(Piloto.nome).all()
        
        if not pilotos:
            print("Nenhum piloto encontrado no banco de dados!")
            return
        
        print("\nLista de pilotos no banco de dados:")
        print("-" * 50)
        for piloto in pilotos:
            print(f"ID: {piloto.id} | Nome: {piloto.nome}")
        print("-" * 50)
        print(f"Total de pilotos: {len(pilotos)}")

if __name__ == "__main__":
    check_pilotos() 