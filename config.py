import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

class Config:
    # Configuração do banco de dados PostgreSQL
    DATABASE_URL = os.getenv('DATABASE_URL')
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Chave secreta para sessões
    SECRET_KEY = os.getenv('SECRET_KEY', 'sua_chave_secreta_aqui')
    
    # Configurações adicionais
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true' 