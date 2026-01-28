"""
Script para adicionar a tabela equipes_temporada ao banco de dados existente.
Esta tabela guarda o snapshot das equipes e seus pilotos em cada temporada,
protegendo o histórico de alterações futuras.
"""

import sqlite3
import os

# Caminho do banco de dados
DB_PATH = 'bolao_f1.db'

def criar_tabela():
    """Cria a tabela equipes_temporada se não existir"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Verificar se a tabela já existe
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='equipes_temporada'
    """)
    
    if cursor.fetchone():
        print("Tabela 'equipes_temporada' já existe!")
    else:
        # Criar a tabela
        cursor.execute("""
            CREATE TABLE equipes_temporada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                temporada_ano INTEGER NOT NULL,
                equipe_nome VARCHAR(100) NOT NULL,
                piloto1_nome VARCHAR(80),
                piloto2_nome VARCHAR(80),
                UNIQUE (temporada_ano, equipe_nome)
            )
        """)
        conn.commit()
        print("Tabela 'equipes_temporada' criada com sucesso!")
    
    conn.close()

if __name__ == '__main__':
    if os.path.exists(DB_PATH):
        criar_tabela()
    else:
        print(f"Banco de dados '{DB_PATH}' não encontrado!")
