from flask import Flask
from models import db, Usuario
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def make_admin():
    with app.app_context():
        # Busca o usuário admin
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            # Atualiza os dados do admin
            admin.is_admin = True
            admin.primeiro_login = True
            admin.set_password('admin123')
            db.session.commit()
            print("Usuário admin atualizado com sucesso!")
        else:
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
            print("Novo admin criado com sucesso!")

if __name__ == "__main__":
    make_admin() 