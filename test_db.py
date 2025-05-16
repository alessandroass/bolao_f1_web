from flask import Flask
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP, PontuacaoSprint
from config_local import ConfigLocal
import traceback

app = Flask(__name__)
app.config.from_object(ConfigLocal)
db.init_app(app)

print("Tentando conectar ao banco de dados...")
print(f"URL do banco: {app.config['SQLALCHEMY_DATABASE_URI']}")

with app.app_context():
    try:
        # Testa a conexão criando um usuário admin
        print("\nVerificando conexão com o banco...")
        db.engine.connect()
        print("Conexão bem sucedida!")
        
        # Verifica se já existe um admin
        print("\nVerificando usuário admin...")
        admin = Usuario.query.filter_by(username='admin').first()
        if not admin:
            admin = Usuario(
                username='admin',
                first_name='Administrador',
                is_admin=True,
                primeiro_login=False
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("Usuário admin criado com sucesso!")
        else:
            print("Usuário admin já existe!")
            
        # Lista todas as tabelas
        print("\nTabelas no banco de dados:")
        for table in db.metadata.tables.keys():
            print(f"- {table}")
            
    except Exception as e:
        print(f"\nErro ao testar o banco de dados:")
        print(f"Tipo do erro: {type(e).__name__}")
        print(f"Mensagem do erro: {str(e)}")
        print("\nStack trace completo:")
        traceback.print_exc() 