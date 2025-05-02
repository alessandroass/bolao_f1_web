from flask import Flask
from models import db, Usuario
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def test_admin():
    with app.app_context():
        # Busca o usuário admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            print("\nUsuário admin encontrado:")
            print("-" * 50)
            print(f"ID: {admin.id}")
            print(f"Username: {admin.username}")
            print(f"Nome: {admin.first_name}")
            print(f"É admin: {admin.is_admin}")
            print(f"Primeiro login: {admin.primeiro_login}")
            print("-" * 50)
        else:
            print("Usuário admin não encontrado!")

if __name__ == "__main__":
    test_admin() 