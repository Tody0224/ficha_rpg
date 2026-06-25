import sqlite3
import random

class MesaModel:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        # Tabela de Mesas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo_convite TEXT UNIQUE NOT NULL,
                mestre_id INTEGER NOT NULL,
                FOREIGN KEY(mestre_id) REFERENCES usuarios(id)
            )
        ''')
        # Tabela de Participantes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS participantes (
                mesa_id INTEGER,
                usuario_id INTEGER,
                FOREIGN KEY(mesa_id) REFERENCES mesas(id),
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        ''')
        conn.commit()
        conn.close()

    @staticmethod
    def criar_mesa(nome, mestre_id):
        codigo = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO mesas (nome, codigo_convite, mestre_id) VALUES (?, ?, ?)", 
                       (nome, codigo, mestre_id))
        conn.commit()
        conn.close()
        return codigo

    @staticmethod
    def get_mesas_por_usuario(usuario_id):
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row  # Isso permite acessar as colunas pelo nome
        cursor = conn.cursor()
        # Busca mesas onde o usuário é mestre
        cursor.execute("SELECT * FROM mesas WHERE mestre_id = ?", (usuario_id,))
        mesas = cursor.fetchall()
        conn.close()
        return [dict(mesa) for mesa in mesas]