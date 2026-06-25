from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class Usuario(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    @staticmethod
    def init_db():
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                last_active TIMESTAMP
            );
        """)
        
        tabelas_fichas = ['conjuradores', 'conjuracoes', 'familiares', 'reliquias']
        for tabela in tabelas_fichas:
            cursor.execute(f"PRAGMA table_info({tabela});")
            colunas = [col[1] for col in cursor.fetchall()]
            if colunas and 'usuario_id' not in colunas:
                cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER DEFAULT 1;")
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return Usuario(row[0], row[1], row[2]) if row else None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM usuarios WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        conn.close()
        return Usuario(row[0], row[1], row[2]) if row else None

    @staticmethod
    def criar_usuario(username, password):
        username = username.strip()
        if not username or not password:
            return False
            
        pwd_hash = generate_password_hash(password)
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, pwd_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)