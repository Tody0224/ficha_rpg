import sqlite3
import random

class MesaModel:
    @staticmethod
    def init_db():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mesas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo_convite TEXT UNIQUE NOT NULL,
                mestre_id INTEGER NOT NULL,
                FOREIGN KEY(mestre_id) REFERENCES usuarios(id)
            )
        ''')
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
        conn.row_factory = sqlite3.Row  # Garante que acessamos por nome da coluna tanto no Python quanto Jinja
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT m.id, m.nome, m.codigo_convite, m.mestre_id
            FROM mesas m
            LEFT JOIN participantes p ON p.mesa_id = m.id
            WHERE m.mestre_id = ? OR p.usuario_id = ?
        """, (usuario_id, usuario_id))
        
        mesas_banco = cursor.fetchall()
        conn.close()
        
        # Converte para dicionários puros para evitar incompatibilidades no template hub.html
        return [dict(row) for row in mesas_banco]