import psycopg2
from werkzeug.security import generate_password_hash

# Configuração da conexão
conn = psycopg2.connect(
    dbname='banco_de_dados_bolao_f1',
    user='banco_de_dados_bolao_f1_user',
    password='8SROg9IMNE87J5UnqWktF10noqQMohTO',
    host='dpg-d09ofvbuibrs73fhptr0-a.oregon-postgres.render.com'
)

def reset_all_passwords():
    try:
        with conn.cursor() as cur:
            # Busca todos os usuários
            cur.execute("SELECT id, username FROM usuarios")
            usuarios = cur.fetchall()
            
            for usuario_id, username in usuarios:
                # Se for admin, usa a senha padrão
                if username == 'admin':
                    senha = 'admin123'
                else:
                    # Para outros usuários, usa o username como senha
                    senha = username
                
                # Gera o hash da senha
                senha_hash = generate_password_hash(senha, method='pbkdf2:sha256')
                
                # Atualiza a senha e define primeiro_login como True
                cur.execute(
                    "UPDATE usuarios SET password = %s, primeiro_login = TRUE WHERE id = %s",
                    (senha_hash, usuario_id)
                )
            
            conn.commit()
            print("Todas as senhas foram resetadas com sucesso!")
            
    except Exception as e:
        print(f"Erro ao resetar senhas: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    reset_all_passwords() 