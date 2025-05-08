from app1 import app, db
from models import PontuacaoSprint

def update_sprint_points():
    with app.app_context():
        # Limpa a tabela de pontuação de sprint
        PontuacaoSprint.query.delete()
        db.session.commit()
        
        # Define os novos pontos para sprint
        pontos_sprint = [
            (0, 1),   # Pole Position
            (1, 8),   # 1º lugar
            (2, 7),   # 2º lugar
            (3, 6),   # 3º lugar
            (4, 5),   # 4º lugar
            (5, 4),   # 5º lugar
            (6, 3),   # 6º lugar
            (7, 2),   # 7º lugar
            (8, 1)    # 8º lugar
        ]
        
        # Insere os novos pontos
        for posicao, pontos in pontos_sprint:
            pontuacao = PontuacaoSprint(posicao=posicao, pontos=pontos)
            db.session.add(pontuacao)
        
        try:
            db.session.commit()
            print("Pontuação dos sprints atualizada com sucesso!")
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao atualizar pontuação dos sprints: {str(e)}")

if __name__ == '__main__':
    update_sprint_points() 