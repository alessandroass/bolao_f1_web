import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from flask import Flask
from models import db, Usuario, Piloto, Palpite, Resposta, Pontuacao, ConfigVotacao, GP

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://banco_de_dados_bolao_f1_user:8SROg9IMNE87J5UnqWktF10noqQMohTO@dpg-d09ofvbuibrs73fhptr0-a.oregon-postgres.render.com/banco_de_dados_bolao_f1'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

def migrate_sqlite_to_postgres():
    # Configura a conexão com o SQLite
    sqlite_path = os.path.join('data', 'bolao_f1.db')
    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Configura a conexão com o PostgreSQL
    pg_conn = psycopg2.connect(
        "postgresql://banco_de_dados_bolao_f1_user:8SROg9IMNE87J5UnqWktF10noqQMohTO@dpg-d09ofvbuibrs73fhptr0-a.oregon-postgres.render.com/banco_de_dados_bolao_f1"
    )
    pg_conn.autocommit = True
    pg_cursor = pg_conn.cursor(cursor_factory=DictCursor)
    
    try:
        # Lê e executa o arquivo SQL para criar as tabelas
        with open('create_tables.sql', 'r') as f:
            sql = f.read()
            pg_cursor.execute(sql)
        print("Tabelas criadas com sucesso!")
        
        # Migra dados da tabela usuarios
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute('SELECT * FROM usuarios')
        for row in sqlite_cursor.fetchall():
            pg_cursor.execute('''
                INSERT INTO usuarios (id, username, first_name, password, is_admin, primeiro_login)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (
                row['id'],
                row['username'],
                row['first_name'],
                row['password'],
                bool(row['is_admin']),
                bool(row['primeiro_login'])
            ))
        print("Usuários migrados com sucesso!")
        
        # Migra dados da tabela pilotos
        sqlite_cursor.execute('SELECT * FROM pilotos')
        for row in sqlite_cursor.fetchall():
            pg_cursor.execute('''
                INSERT INTO pilotos (id, nome)
                VALUES (%s, %s)
            ''', (row['id'], row['nome']))
        print("Pilotos migrados com sucesso!")
        
        # Migra dados da tabela palpites
        sqlite_cursor.execute('SELECT * FROM palpites')
        for row in sqlite_cursor.fetchall():
            pg_cursor.execute('''
                INSERT INTO palpites (id, usuario_id, gp_slug, pos_1, pos_2, pos_3, pos_4, pos_5,
                                    pos_6, pos_7, pos_8, pos_9, pos_10, pole)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                row['id'],
                row['usuario_id'],
                row['gp_slug'],
                row['pos_1'],
                row['pos_2'],
                row['pos_3'],
                row['pos_4'],
                row['pos_5'],
                row['pos_6'],
                row['pos_7'],
                row['pos_8'],
                row['pos_9'],
                row['pos_10'],
                row['pole']
            ))
        print("Palpites migrados com sucesso!")
        
        # Migra dados da tabela respostas
        sqlite_cursor.execute('SELECT * FROM respostas')
        for row in sqlite_cursor.fetchall():
            pg_cursor.execute('''
                INSERT INTO respostas (id, gp_slug, pos_1, pos_2, pos_3, pos_4, pos_5,
                                     pos_6, pos_7, pos_8, pos_9, pos_10, pole)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (
                row['id'],
                row['gp_slug'],
                row['pos_1'],
                row['pos_2'],
                row['pos_3'],
                row['pos_4'],
                row['pos_5'],
                row['pos_6'],
                row['pos_7'],
                row['pos_8'],
                row['pos_9'],
                row['pos_10'],
                row['pole']
            ))
        print("Respostas migradas com sucesso!")
        
        # Migra dados da tabela pontuacao
        sqlite_cursor.execute('SELECT * FROM pontuacao')
        for row in sqlite_cursor.fetchall():
            pg_cursor.execute('''
                INSERT INTO pontuacao (id, posicao, pontos)
                VALUES (%s, %s, %s)
            ''', (row['id'], row['posicao'], row['pontos']))
        print("Pontuações migradas com sucesso!")
        
        # Migra dados da tabela config_votacao
        try:
            sqlite_cursor.execute('SELECT * FROM config_votacao')
            for row in sqlite_cursor.fetchall():
                pg_cursor.execute('''
                    INSERT INTO config_votacao (id, gp_slug, pole_habilitado, posicoes_habilitado)
                    VALUES (%s, %s, %s, %s)
                ''', (
                    row['id'],
                    row['gp_slug'],
                    True,  # Valores padrão
                    True   # Valores padrão
                ))
            print("Configurações de votação migradas com sucesso!")
        except Exception as e:
            print(f"Erro ao migrar configurações de votação: {str(e)}")
            print("Criando configurações padrão...")
            # Cria configurações padrão para todos os GPs
            sqlite_cursor.execute('SELECT DISTINCT gp_slug FROM palpites')
            for row in sqlite_cursor.fetchall():
                pg_cursor.execute('''
                    INSERT INTO config_votacao (gp_slug, pole_habilitado, posicoes_habilitado)
                    VALUES (%s, %s, %s)
                ''', (row['gp_slug'], True, True))
        
        # Migra dados da tabela gps
        try:
            sqlite_cursor.execute('SELECT * FROM gps')
            for row in sqlite_cursor.fetchall():
                pg_cursor.execute('''
                    INSERT INTO gps (id, slug, nome, data_corrida, hora_corrida,
                                   data_classificacao, hora_classificacao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                ''', (
                    row['id'],
                    row['slug'],
                    row['nome'],
                    row['data_corrida'],
                    row['hora_corrida'],
                    row['data_classificacao'],
                    row['hora_classificacao']
                ))
            print("GPs migrados com sucesso!")
        except Exception as e:
            print(f"Erro ao migrar GPs: {str(e)}")
            print("Criando GPs padrão...")
            # Cria GPs padrão baseado nos palpites existentes
            sqlite_cursor.execute('SELECT DISTINCT gp_slug FROM palpites')
            for row in sqlite_cursor.fetchall():
                pg_cursor.execute('''
                    INSERT INTO gps (slug, nome, data_corrida, hora_corrida,
                                   data_classificacao, hora_classificacao)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (
                    row['gp_slug'],
                    f"GP {row['gp_slug']}",
                    "2025-01-01",
                    "12:00",
                    "2025-01-01",
                    "12:00"
                ))
        
        print("Migração concluída com sucesso!")
        
    except Exception as e:
        print(f"Erro durante a migração: {str(e)}")
        pg_conn.rollback()
        raise
    finally:
        sqlite_conn.close()
        pg_conn.close()

if __name__ == '__main__':
    migrate_sqlite_to_postgres() 