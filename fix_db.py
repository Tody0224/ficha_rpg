import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE usuarios ADD COLUMN last_active TIMESTAMP;")
    conn.commit()
    print("✅ Coluna adicionada com sucesso!")
except sqlite3.OperationalError as e:
    print(f"⚠️ Ocorreu um erro: {e}")
    print("Provavelmente a coluna já existe no banco. Tudo bem!")

conn.close()