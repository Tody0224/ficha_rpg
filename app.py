# app.py
from flask import Flask
from controllers.route_controller import bp

app = Flask(__name__)
app.register_blueprint(bp)

if __name__ == '__main__':
    # Roda localmente para testes e depuração
    app.run(debug=True, port=5000)