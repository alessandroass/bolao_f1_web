from app1 import app, db
from models import PalpiteSprint

with app.app_context():
    # Drop a tabela se ela existir
    PalpiteSprint.__table__.drop(db.engine, checkfirst=True)
    # Recria a tabela
    db.create_all()
    print("Tabela palpites_sprint recriada com sucesso!") 