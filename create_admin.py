from flask import Flask
from models import db, Usuario
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def create_admin():
    with app.app_context():
        # Verifica se o admin já existe
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            print("Usuário admin já existe!")
            return
        
        # Cria um novo admin
        admin = Usuario(
            username='admin',
            first_name='Administrador',
            is_admin=True,
            primeiro_login=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Usuário admin criado com sucesso!")
        print("Login: admin")
        print("Senha: admin123")

if __name__ == "__main__":
    create_admin() 