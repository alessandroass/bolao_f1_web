from flask import Flask
from models import db, Usuario
from config import Config
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def reset_admin_password():
    with app.app_context():
        # Verifica se o admin já existe
        admin = Usuario.query.filter_by(username='admin').first()
        
        if admin:
            # Se existir, apenas reseta a senha
            admin.set_password('admin123')
            admin.primeiro_login = True
        else:
            # Se não existir, cria um novo admin
            admin = Usuario(
                username='admin',
                first_name='Administrador',
                is_admin=True,
                primeiro_login=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        db.session.commit()
        print("Senha do admin resetada com sucesso!")

if __name__ == "__main__":
    reset_admin_password() 