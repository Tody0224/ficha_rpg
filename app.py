from flask import Flask
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from models.user import Usuario
from models.character import CharacterModel
from datetime import datetime
import sqlite3
import os

from controllers.auth_controller import auth_bp
from controllers.main_controller import main_bp
from controllers.sheet_controller import sheet_bp
from controllers.table_controller import table_bp

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
app.secret_key = os.environ.get('SECRET_KEY', 'chave_padrao_local')

app.config['SESSION_PERMANENT'] = False
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

@app.before_request
def update_user_activity():
    if current_user.is_authenticated:
        # AQUI É ONDE O CONTADOR COMEÇA A FUNCIONAR
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE usuarios SET last_active = ? WHERE id = ?", 
                       (datetime.now(), current_user.id))
        conn.commit()
        conn.close()

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Inicializações do Banco de Dados
Usuario.init_db()
CharacterModel.init_db()

# Configuração do Gerenciador de Login
login_manager = LoginManager()
# AJUSTE: Alterado de 'routes.login' para 'auth.login' refletindo a nova divisão
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))

# REGISTRO DOS BLUEPRINTS MODULARES
app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(main_bp, url_prefix='/')
app.register_blueprint(sheet_bp, url_prefix='/')
app.register_blueprint(table_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)