from flask import Flask
from flask_login import LoginManager
from models.user import Usuario
from models.character import CharacterModel  
from controllers.route_controller import bp

app = Flask(__name__)

# CHAVE SECRETA: Essencial para assinar os cookies de sessão de forma segura.
app.secret_key = 'super_secret_rpg_key_123'

# ─────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE SESSÃO: Força a expiração ao fechar a aba/navegador
# ─────────────────────────────────────────────────────────
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

# Inicializa o banco de dados de usuários
Usuario.init_db()

# Inicializa e atualiza a estrutura das tabelas de fichas (conjuradores, relíquias, etc.)
CharacterModel.init_db()

# Inicializa o Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'routes.login'  # Define para onde mandar o usuário se a rota exigir login
login_manager.login_message = "Por favor, faça login para acessar o Hub Místico."
login_manager.login_message_category = "error"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return Usuario.get_by_id(int(user_id))

# Adicione isso no seu app.py
@app.after_request
def add_header(response):
    """
    Força o navegador a não fazer cache das páginas.
    Isso garante que ao voltar para a página, o navegador 
    seja obrigado a verificar se o usuário ainda está logado.
    """
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# Registra as suas rotas
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True)