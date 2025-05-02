from flask import Flask
from models import db, Usuario
from config import Config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://banco_de_dados_bolao_f1_user:8SROg9IMNE87J5UnqWktF10noqQMohTO@dpg-d09ofvbuibrs73fhptr0-a.oregon-postgres.render.com/banco_de_dados_bolao_f1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def reset_all_passwords():
    with app.app_context():
        # Busca todos os usuários
        usuarios = Usuario.query.all()
        
        for usuario in usuarios:
            # Se for admin, usa a senha padrão
            if usuario.username == 'admin':
                usuario.set_password('admin123')
            else:
                # Para outros usuários, usa o username como senha
                usuario.set_password(usuario.username)
            usuario.primeiro_login = True
        
        db.session.commit()
        print("Todas as senhas foram resetadas com sucesso!")

if __name__ == '__main__':
    reset_all_passwords() 