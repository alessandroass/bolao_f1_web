import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo env_local_config
load_dotenv('env_local_config')

class ConfigLocal:
    # Configurações do banco de dados local
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:ale81635721@localhost:5432/bolao_f1'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Outras configurações
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua_chave_secreta_local')
    DEBUG = True 