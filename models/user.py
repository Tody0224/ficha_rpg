# models/user.py
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
        """Cria as tabelas necessárias se elas não existirem."""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Cria tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        
        # Opcional: Se você quiser que as fichas fiquem vinculadas a quem as criou,
        # você pode rodar um comando para garantir que a coluna usuario_id exista nas suas tabelas de fichas.
        # Exemplo para conjurador:
        # cursor.execute("ALTER TABLE conjuradores ADD COLUMN usuario_id INTEGER;")
        
        conn.commit()
        conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM usuarios WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Usuario(row[0], row[1], row[2])
        return None

    @staticmethod
    def get_by_username(username):
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password FROM usuarios WHERE username = ?", (username.strip(),))
        row = cursor.fetchone()
        conn.close()
        if row:
            return Usuario(row[0], row[1], row[2])
        return None

    @staticmethod
    def criar_usuario(username, password):
        username = username.strip()
        if not username or not password:
            return False
            
        # Gera o hash seguro da senha
        pwd_hash = generate_password_hash(password)
        
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO usuarios (username, password) VALUES (?, ?)", (username, pwd_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Username já está em uso
        finally:
            conn.close()

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)