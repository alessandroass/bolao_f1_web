"""
Script para salvar snapshot das equipes da temporada 2025 no Render
Execute no Shell do Render: python salvar_snapshot_render.py
"""
import os
import psycopg2

# Pega a DATABASE_URL do ambiente (configurada automaticamente no Render)
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

def salvar_snapshot(ano=2025):
    if not DATABASE_URL:
        print("ERRO: DATABASE_URL não encontrada!")
        return
    
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    # Verificar se já existe snapshot para o ano
    cursor.execute("SELECT COUNT(*) FROM equipes_temporada WHERE temporada_ano = %s", (ano,))
    if cursor.fetchone()[0] > 0:
        print(f"Snapshot de {ano} já existe! Excluindo para recriar...")
        cursor.execute("DELETE FROM equipes_temporada WHERE temporada_ano = %s", (ano,))
    
    # Buscar todas as equipes com seus pilotos
    cursor.execute("""
        SELECT e.nome, p1.nome, p2.nome
        FROM equipes e
        LEFT JOIN pilotos p1 ON e.piloto1_id = p1.id
        LEFT JOIN pilotos p2 ON e.piloto2_id = p2.id
    """)
    
    equipes = cursor.fetchall()
    
    for equipe_nome, piloto1_nome, piloto2_nome in equipes:
        cursor.execute("""
            INSERT INTO equipes_temporada (temporada_ano, equipe_nome, piloto1_nome, piloto2_nome)
            VALUES (%s, %s, %s, %s)
        """, (ano, equipe_nome, piloto1_nome, piloto2_nome))
        print(f"Salvo: {equipe_nome} - {piloto1_nome}, {piloto2_nome}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f"\nSnapshot de {ano} salvo com sucesso!")

if __name__ == '__main__':
    salvar_snapshot(2025)
