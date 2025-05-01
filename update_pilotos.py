import sqlite3

# Lista correta de pilotos
pilotos = [
    "Max Verstappen", "Yuki Tsunoda", "Kimi Antonelli", "George Russell",
    "Charles Leclerc", "Lewis Hamilton", "Lando Norris", "Oscar Piastri",
    "Fernando Alonso", "Lance Stroll", "Liam Lawson", "Isack Hadjar",
    "Pierre Gasly", "Jack Doohan", "Niko Hulkenberg", "Gabriel Bortoleto",
    "Esteban Ocon", "Oliver Bearman", "Carlos Sainz", "Alexander Albon"
]

# Conectar ao banco de dados
conn = sqlite3.connect('bolao_f1.db')
c = conn.cursor()

# Limpar a tabela de pilotos
c.execute('DELETE FROM pilotos')

# Inserir os pilotos corretos
for piloto in pilotos:
    c.execute('INSERT INTO pilotos (nome) VALUES (?)', (piloto,))

# Commit e fechar conexão
conn.commit()
conn.close()

print("Lista de pilotos atualizada com sucesso!") 