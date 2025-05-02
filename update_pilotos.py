from flask import Flask
from models import db, Piloto
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def update_pilotos():
    with app.app_context():
        # Lista dos pilotos da F1 2025
        pilotos_2025 = [
            "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
            "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
            "Fernando Alonso", "Lance Stroll", "Liam Lawson", "Isack Hadjar",
            "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg", "Gabriel Bortoleto",
            "Esteban Ocon", "Oliver Bearman", "Carlos Sainz", "Alexander Albon"
        ]
        
        # Remove todos os pilotos existentes
        Piloto.query.delete()
        
        # Adiciona os novos pilotos
        for nome in pilotos_2025:
            piloto = Piloto(nome=nome)
            db.session.add(piloto)
        
        db.session.commit()
        print("Pilotos atualizados com sucesso!")

if __name__ == "__main__":
    update_pilotos() 