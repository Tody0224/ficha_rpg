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
        """Cria as tabelas necessárias e atualiza as de fichas para o sistema de login."""
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # 1. Cria a tabela de usuários
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            );
        """)
        
        # 2. Varre as tabelas de fichas para garantir que todas possuem o vínculo 'usuario_id'
        tabelas_fichas = ['conjuradores', 'conjuracoes', 'familiares', 'reliquias']
        
        for tabela in tabelas_fichas:
            # Verifica se a tabela já existe
            cursor.execute(f"PRAGMA table_info({tabela});")
            colunas = [col[1] for col in cursor.fetchall()]
            
            if colunas:
                # Se a tabela existe mas não tem 'usuario_id', adiciona a coluna de forma segura
                if 'usuario_id' not in colunas:
                    try:
                        cursor.execute(f"ALTER TABLE {tabela} ADD COLUMN usuario_id INTEGER DEFAULT 1;")
                        print(f"📌 Coluna 'usuario_id' adicionada com sucesso à tabela '{tabela}'.")
                    except sqlite3.OperationalError as e:
                        print(f"⚠️ Erro ao atualizar tabela {tabela}: {e}")
            else:
                # Caso a tabela ainda vá ser criada do zero no seu CharacterModel,
                # garanta que ela já nasça com o 'usuario_id INTEGER' na query de criação.
                pass
        
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