"""
Script para corrigir a sequência do id da tabela gps no PostgreSQL.
Use quando aparecer: duplicate key value violates unique constraint "gps_pkey"

Execute uma vez no Render Shell (ou local com DATABASE_URL do Render):
  python fix_sequence_gps.py

Ou no psql conectado ao banco:
  SELECT setval(pg_get_serial_sequence('gps', 'id'), COALESCE((SELECT MAX(id) FROM gps), 1));
"""
import os
import sys

# Garante que usa o app e o banco do Render
if __name__ == '__main__':
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from app1 import app, db
    from sqlalchemy import text

    with app.app_context():
        try:
            url = str(db.engine.url)
            if 'postgresql' not in url:
                print('Este script é apenas para PostgreSQL. Seu banco:', url.split('@')[-1].split('/')[0])
                sys.exit(1)
            db.session.execute(text(
                "SELECT setval(pg_get_serial_sequence('gps', 'id'), COALESCE((SELECT MAX(id) FROM gps), 1))"
            ))
            db.session.commit()
            print('Sequência da tabela gps corrigida com sucesso.')
        except Exception as e:
            db.session.rollback()
            print('Erro:', e)
            sys.exit(1)
