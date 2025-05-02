from flask import Flask
from models import db, Usuario
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def add_admin_column():
    with app.app_context():
        # Verifica se a coluna is_admin já existe
        try:
            # Tenta buscar um usuário com is_admin
            usuario = Usuario.query.first()
            if usuario and hasattr(usuario, 'is_admin'):
                print("Coluna is_admin já existe!")
                return
        except Exception:
            pass
        
        # Se chegou aqui, a coluna não existe
        print("Adicionando coluna is_admin...")
        
        # Atualiza todos os usuários existentes para não serem admin
        usuarios = Usuario.query.all()
        for usuario in usuarios:
            usuario.is_admin = False
        
        # Define o usuário admin como administrador
        admin = Usuario.query.filter_by(username='admin').first()
        if admin:
            admin.is_admin = True
        
        db.session.commit()
        print("Coluna is_admin adicionada com sucesso!")

if __name__ == "__main__":
    add_admin_column() 