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
    
    @staticmethod
    def get_mesas_por_usuario(usuario_id):
        import sqlite3 # Certifique-se de ter o import se necessário
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Busca tanto as mesas que ele criou (mestre_id) quanto as que ele participa
        cursor.execute("""
            SELECT DISTINCT m.id, m.nome, m.codigo_convite, m.mestre_id
            FROM mesas m
            LEFT JOIN participantes p ON p.mesa_id = m.id
            WHERE m.mestre_id = ? OR p.usuario_id = ?
        """, (usuario_id, usuario_id))
        
        mesas_banco = cursor.fetchall()
        conn.close()
        
        # Monta a lista de dicionários ou objetos que o seu hub.html já espera
        mesas = []
        for row in mesas_banco:
            mesas.append({
                'id': row[0],
                'nome': row[1],
                'codigo_convite': row[2],
                'mestre_id': row[3]
            })
        return mesas