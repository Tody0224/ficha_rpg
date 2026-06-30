from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import login_required, current_user
from models.character import CharacterModel
from models.mesa import MesaModel
import constants
import random
from datetime import datetime, timedelta
import sqlite3

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    return redirect(url_for('main.hub'))

@main_bp.route('/hub')
def hub():
    if current_user.is_authenticated:
        conjuradores = CharacterModel.get_all_by_type('conjurador', current_user.id)
        conjuracoes = CharacterModel.get_all_by_type('conjuracao', current_user.id)
        familiares = CharacterModel.get_all_by_type('familiar', current_user.id)
        reliquias = CharacterModel.get_all_by_type('reliquia', current_user.id)
        minhas_mesas = MesaModel.get_mesas_por_usuario(current_user.id)
    else:
        conjuradores = []
        conjuracoes = []
        familiares = []
        reliquias = []
        minhas_mesas = []
    
    return render_template('hub.html', 
                           conjuradores=conjuradores,
                           conjuracoes=conjuracoes,
                           familiares=familiares,
                           reliquias=reliquias,
                           mesas=minhas_mesas)

@main_bp.route('/api/calculate_resources', methods=['POST'])
def api_resources():
    data = request.json or {}
    try:
        grau = int(data.get('grau', 1))
        vit = int(data.get('vitalidade', 1))
        sin = int(data.get('sintonia', 1))
        res = CharacterModel.calculate_resources(grau, vit, sin)
        return jsonify(res)
    except ValueError:
        return jsonify({"error": "Parâmetros inválidos"}), 400

@main_bp.route('/api/test_mode/<sheet_type>')
def api_test_mode(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return jsonify({"error": "Tipo inválido"}), 400
        
    mock_data = CharacterModel.get_test_data(sheet_type)
    
    if sheet_type in ['familiar', 'conjuracao']:
        opcoes_sub = ["NENHUMA"] + list(getattr(constants, 'SUB_MATRIZES', []))
        opcoes_sub = list(set([str(op).upper() for op in opcoes_sub if op]))
        sub_sorteada = random.choice(opcoes_sub)
        mock_data['SUB_MATRIZ'] = sub_sorteada
        mock_data['v_sub'] = sub_sorteada

    elif sheet_type == 'reliquia':
        mock_data['NOME'] = f"Artefato Místico {random.randint(100, 999)}"
        mock_data['NIVEL'] = random.choice(list(getattr(constants, 'NIVEIS_REL', ['I', 'II', 'III'])))
        mock_data['NUCLEO'] = random.choice(list(getattr(constants, 'NUCLEOS_REL', []))) if getattr(constants, 'NUCLEOS_REL', []) else "NÚCLEO INSTÁVEL"
        mock_data['MATRIZ'] = random.choice(list(getattr(constants, 'MATRIZES', ['NEUTRO'])))
        
        opcoes_sub = ["NENHUMA"] + list(getattr(constants, 'SUB_MATRIZES', []))
        opcoes_sub = list(set([str(op).upper() for op in opcoes_sub if op]))
        mock_data['SUB_MATRIZ'] = random.choice(opcoes_sub)
        
        mock_data['ALCANCE'] = random.choice(list(getattr(constants, 'ALCANCES', ['Curto'])))
        mock_data['DANO'] = random.choice(['1d6', '1d8', '1d10', '2d4', '—'])
        mock_data['FAMILIAR'] = random.choice(['', 'Pip', 'Serpente das Sombras', 'Grimório Alado'])
        
        mock_data['CONJURACOES'] = "Esfera de Fogo, Escudo Arcano (Gravados na estrutura física da Relíquia)."
        mock_data['DESCRICAO'] = "Uma relíquia antiga gerada automaticamente pelo modo teste, emanando uma sutil oscilação de energia fundamental."

    return jsonify(mock_data)

@main_bp.route('/api/active_users')
@login_required
def get_active_users():
    limite = datetime.now() - timedelta(minutes=5)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username FROM usuarios WHERE last_active > ?", (limite,))
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    return jsonify({"count": len(users), "users": users})