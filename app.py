from flask import Flask
from flask_login import LoginManager, current_user
from models.user import Usuario
from models.character import CharacterModel
from controllers.route_controller import bp
from datetime import datetime
import sqlite3

app = Flask(__name__)
app.secret_key = 'super_secret_rpg_key_123'

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

# Inicializações
Usuario.init_db()
CharacterModel.init_db()

login_manager = LoginManager()
login_manager.login_view = 'routes.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))

app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)