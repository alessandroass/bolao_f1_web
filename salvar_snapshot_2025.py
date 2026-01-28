"""
Script para salvar snapshot das equipes da temporada 2025
"""
import psycopg2

# Configuração do banco PostgreSQL local
DB_URI = 'postgresql://postgres:ale81635721@localhost:5432/bolao_f1'

def salvar_snapshot():
    conn = psycopg2.connect(DB_URI)
    cursor = conn.cursor()
    
    # Verificar se já existe snapshot para 2025
    cursor.execute("SELECT COUNT(*) FROM equipes_temporada WHERE temporada_ano = 2025")
    if cursor.fetchone()[0] > 0:
        print("Snapshot de 2025 já existe! Excluindo para recriar...")
        cursor.execute("DELETE FROM equipes_temporada WHERE temporada_ano = 2025")
    
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
        """, (2025, equipe_nome, piloto1_nome, piloto2_nome))
        print(f"Salvo: {equipe_nome} - {piloto1_nome}, {piloto2_nome}")
    
    conn.commit()
    cursor.close()
    conn.close()
    print("\nSnapshot de 2025 salvo com sucesso!")

if __name__ == '__main__':
    salvar_snapshot()
