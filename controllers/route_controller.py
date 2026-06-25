# controllers/route_controller.py
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for
from models.character import CharacterModel
from models.pdf_generator import PDFGeneratorModel
import constants

bp = Blueprint('routes', __name__)
pdf_generator = PDFGeneratorModel()

@bp.route('/')
def hub():
    # Coleta todas as fichas separadas por categoria para listar no Hub
    return render_template('hub.html', 
                           conjuradores=CharacterModel.get_all_by_type('conjurador'),
                           conjuracoes=CharacterModel.get_all_by_type('conjuracao'),
                           familiares=CharacterModel.get_all_by_type('familiar'),
                           reliquias=CharacterModel.get_all_by_type('reliquia'))

@bp.route('/create/<sheet_type>')
def create_form(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=None)

@bp.route('/edit/<sheet_type>/<int:entity_id>')
def edit_entity(sheet_type, entity_id):
    """Rota dinâmica de edição para qualquer tipo de ficha."""
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    entity = CharacterModel.get_entity_by_id(sheet_type, entity_id)
    if not entity:
        return f"{sheet_type.capitalize()} não encontrado(a)", 404
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=entity)

@bp.route('/save_and_process/<sheet_type>', methods=['POST'])
@bp.route('/save_and_process/<sheet_type>/<int:entity_id>', methods=['POST'])
def save_and_process(sheet_type, entity_id=None):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404

    form_data = request.form.to_dict()
    action_type = request.form.get('action_type', 'pdf')
    
    # Processamento de Regras de Negócio antes de salvar/gerar
    if sheet_type == "conjurador":
        form_data['PASSIVA_ESCOLA'] = constants.PASSIVAS_ESCOLAS.get(form_data.get('ESCOLA'), '')
        form_data['PERICIAS'] = ", ".join(request.form.getlist('pericias'))
        res = CharacterModel.calculate_resources(
            int(form_data.get('GRAU', 1)), 
            int(form_data.get('VITALIDADE', 1)), 
            int(form_data.get('SINTONIA_ATRIB', 1))
        )
        form_data['VIDA_MAX'] = res['vida']
        form_data['CONEXAO_MAX'] = res['conexao']
        if not form_data.get('RELIQUIA'):
            form_data['RELIQUIA'] = f"Relíquia de {form_data.get('NOME')}"
            
    elif sheet_type == "conjuracao":
        form_data['SUB_MATRIZ'] = form_data.get('SUB_MATRIZ') or "NENHUMA"
        
    elif sheet_type == "familiar":
        form_data['MATRIZ'] = form_data.get('MATRIZ') or "NEUTRO"
        form_data['SUB_MATRIZ'] = form_data.get('SUB_MATRIZ') or "NENHUMA"
        
    elif sheet_type == "reliquia":
        if not form_data.get('FAMILIAR'):
            form_data['FAMILIAR'] = "Nenhum familiar vinculado"

    # ─────────────────────────────────────────────────────────
    # FLUXO SEGUIDO POR TIPO DE AÇÃO (CORRIGIDO)
    # ─────────────────────────────────────────────────────────
    if action_type == "database":
        # SÓ grava e redireciona se o utilizador escolheu salvar no banco
        CharacterModel.save_entity(sheet_type, form_data, entity_id=entity_id)
        return redirect(url_for('routes.hub'))

    # Caso contrário (Modo 'pdf'), gera APENAS o PDF na memória sem tocar na base de dados
    pdf_buffer = pdf_generator.build_pdf(sheet_type, form_data)
    filename = f"Ficha_{form_data.get('NOME', 'Ficha').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

@bp.route('/delete/<sheet_type>/<int:entity_id>', methods=['POST'])
def delete_entity(sheet_type, entity_id):
    """Rota polimórfica para remover qualquer tipo de ficha."""
    CharacterModel.delete_entity(sheet_type, entity_id)
    return redirect(url_for('routes.hub'))

# ─────────────────────────────────────────────────────────
# ENDPOINTS DA API (CÁLCULOS ASSÍNCRONOS E MODO TESTE)
# ─────────────────────────────────────────────────────────
@bp.route('/api/calculate_resources', methods=['POST'])
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

@bp.route('/api/test_mode/<sheet_type>')
def api_test_mode(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return jsonify({"error": "Tipo inválido"}), 400
    mock_data = CharacterModel.get_test_data(sheet_type)
    return jsonify(mock_data)