# app.py
from flask import Flask
from controllers.route_controller import bp
from models.character import CharacterModel

app = Flask(__name__)
app.register_blueprint(bp)

# Inicializa o arquivo SQLite caso ele não exista
with app.app_context():
    CharacterModel.init_db()

if __name__ == '__main__':
    app.run(debug=True, port=5000)