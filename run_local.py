import os
from app1 import app, create_tables

if __name__ == '__main__':
    # Define o ambiente como desenvolvimento
    os.environ['FLASK_ENV'] = 'development'
    
    # Cria as tabelas se não existirem
    with app.app_context():
        create_tables()
    
    # Inicia o servidor de desenvolvimento
    app.run(debug=True, host='0.0.0.0', port=5000) 