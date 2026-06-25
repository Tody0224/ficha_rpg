# app.py
from flask import Flask
from flask_login import LoginManager
from models.user import Usuario
from controllers.route_controller import bp

app = Flask(__name__)

# CHAVE SECRETA: Essencial para assinar os cookies de sessão de forma segura.
# Em produção, mude para algo complexo gerado aleatoriamente.
app.secret_key = 'super_secret_rpg_key_123'

# Inicializa o banco de dados e a tabela de usuários
Usuario.init_db()

# Inicializa o Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'routes.login'  # Define para onde mandar o usuário se a rota exigir login
login_manager.login_message = "Por favor, faça login para acessar o Hub Místico."
login_manager.login_message_category = "error"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))

# Registra as suas rotas
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)