"""
Script para adicionar as colunas de temporada nas tabelas existentes.
Execute apenas uma vez!
"""

import psycopg2
from config_local import ConfigLocal

def migrar_banco():
    print("Iniciando migração do banco de dados...")
    
    # Conectar ao banco de dados
    conn = psycopg2.connect(ConfigLocal.SQLALCHEMY_DATABASE_URI)
    cursor = conn.cursor()
    
    try:
        # 1. Criar tabela temporadas
        print("Criando tabela 'temporadas'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS temporadas (
                id SERIAL PRIMARY KEY,
                ano INTEGER UNIQUE NOT NULL,
                ativa BOOLEAN DEFAULT FALSE,
                arquivada BOOLEAN DEFAULT FALSE,
                data_inicio TIMESTAMP,
                data_fim TIMESTAMP
            )
        """)
        print("  ✓ Tabela 'temporadas' criada")
        
        # 2. Criar tabela campeoes_temporada
        print("Criando tabela 'campeoes_temporada'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS campeoes_temporada (
                id SERIAL PRIMARY KEY,
                temporada_id INTEGER REFERENCES temporadas(id),
                usuario_id INTEGER REFERENCES usuarios(id),
                posicao INTEGER NOT NULL,
                pontos_total INTEGER NOT NULL
            )
        """)
        print("  ✓ Tabela 'campeoes_temporada' criada")
        
        # 3. Adicionar coluna temporada_ano na tabela palpites
        print("Adicionando coluna 'temporada_ano' na tabela 'palpites'...")
        try:
            cursor.execute("""
                ALTER TABLE palpites 
                ADD COLUMN IF NOT EXISTS temporada_ano INTEGER DEFAULT 2025
            """)
            print("  ✓ Coluna adicionada em 'palpites'")
        except Exception as e:
            print(f"  (coluna já existe ou erro: {e})")
        
        # 4. Adicionar coluna temporada_ano na tabela respostas
        print("Adicionando coluna 'temporada_ano' na tabela 'respostas'...")
        try:
            cursor.execute("""
                ALTER TABLE respostas 
                ADD COLUMN IF NOT EXISTS temporada_ano INTEGER DEFAULT 2025
            """)
            print("  ✓ Coluna adicionada em 'respostas'")
        except Exception as e:
            print(f"  (coluna já existe ou erro: {e})")
        
        # 5. Adicionar coluna temporada_ano na tabela gps
        print("Adicionando coluna 'temporada_ano' na tabela 'gps'...")
        try:
            cursor.execute("""
                ALTER TABLE gps 
                ADD COLUMN IF NOT EXISTS temporada_ano INTEGER DEFAULT 2025
            """)
            print("  ✓ Coluna adicionada em 'gps'")
        except Exception as e:
            print(f"  (coluna já existe ou erro: {e})")
        
        # 6. Atualizar registros existentes para temporada 2025
        print("Atualizando registros existentes para temporada 2025...")
        cursor.execute("UPDATE palpites SET temporada_ano = 2025 WHERE temporada_ano IS NULL")
        cursor.execute("UPDATE respostas SET temporada_ano = 2025 WHERE temporada_ano IS NULL")
        cursor.execute("UPDATE gps SET temporada_ano = 2025 WHERE temporada_ano IS NULL")
        print("  ✓ Registros atualizados")
        
        # Commit das alterações
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro na migração: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    migrar_banco()
