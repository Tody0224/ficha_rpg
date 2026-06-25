# controllers/route_controller.py
from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for
from models.character import CharacterModel
from models.pdf_generator import PDFGeneratorModel
import constants

bp = Blueprint('routes', __name__)
pdf_generator = PDFGeneratorModel()

@bp.route('/')
def hub():
    # Coleta as conjurações salvas para listar na página inicial
    saved_conjuracoes = CharacterModel.get_all_conjuracoes()
    return render_template('hub.html', conjuracoes=saved_conjuracoes)

@bp.route('/create/<sheet_type>')
def create_form(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=None)

@bp.route('/edit/conjuracao/<int:entity_id>')
def edit_conjuracao(entity_id):
    """Rota para carregar o formulário preenchido com dados do banco para edição."""
    conjuracao = CharacterModel.get_conjuracao_by_id(entity_id)
    if not conjuracao:
        return "Conjuração não encontrada", 404
    return render_template('conjuracao.html', constants=constants, sheet_type='conjuracao', entity=conjuracao)

@bp.route('/delete/conjuracao/<int:entity_id>', methods=['POST'])
def delete_conjuracao(entity_id):
    """Rota para deletar uma conjuração e retornar ao Hub."""
    CharacterModel.delete_conjuracao(entity_id)
    return redirect(url_for('routes.hub'))

@bp.route('/save_and_process/<sheet_type>', methods=['POST'])
@bp.route('/save_and_process/<sheet_type>/<int:entity_id>', methods=['POST'])
def save_and_process(sheet_type, entity_id=None):
    """Salva os dados no banco de dados (se aplicável) e gera o PDF ou volta ao Hub."""
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404

    form_data = request.form.to_dict()
    action_type = request.form.get('action_type', 'pdf') # 'pdf' ou 'database'
    
    # ─────────────────────────────────────────────────────────
    # APLICAÇÃO DE REGRAS DE NEGÓCIO DA FICHA
    # ─────────────────────────────────────────────────────────
    if sheet_type == "conjurador":
        form_data['PASSIVA_ESCOLA'] = constants.PASSIVAS_ESCOLAS.get(form_data.get('ESCOLA'), '')
        pericias_list = request.form.getlist('pericias')
        form_data['PERICIAS'] = ", ".join(pericias_list)
        # Recálculo seguro dos atributos de Vida e Conexão baseados no Grau e Atributos
        res = CharacterModel.calculate_resources(
            int(form_data.get('GRAU', 1)), 
            int(form_data.get('VITALIDADE', 1)), 
            int(form_data.get('SINTONIA', 1))
        )
        form_data['VIDA_MAX'] = res['vida']
        form_data['CONEXAO_MAX'] = res['conexao']
        if not form_data.get('RELIQUIA'):
            form_data['RELIQUIA'] = f"Relíquia de {form_data.get('NOME', 'Desconhecido')}"
            
    elif sheet_type == "conjuracao":
        form_data['SUB_MATRIZ'] = form_data.get('SUB_MATRIZ') or "NENHUMA"
        form_data['GANHO'] = form_data.get('GANHO') or "NENHUM"
        # Grava ou atualiza no banco de dados SQLite
        entity_id = CharacterModel.save_conjuracao(form_data, conjuracao_id=entity_id)
        
    elif sheet_type == "familiar":
        form_data['MATRIZ'] = form_data.get('MATRIZ') or "NEUTRO"
        form_data['SUB_MATRIZ'] = form_data.get('SUB_MATRIZ') or "NENHUMA"
        
    elif sheet_type == "reliquia":
        if not form_data.get('FAMILIAR'):
            form_data['FAMILIAR'] = "Nenhum familiar vinculado"

    # ─────────────────────────────────────────────────────────
    # FLUXO DE RETORNO (BANCO DE DADOS VS EXPORTAÇÃO PDF)
    # ─────────────────────────────────────────────────────────
    # Se o usuário clicou em "Salvar no Banco", redireciona para o Hub
    if action_type == "database":
        return redirect(url_for('routes.hub'))

    # Caso contrário, prossegue para gerar e entregar o PDF dinamicamente
    pdf_buffer = pdf_generator.build_pdf(sheet_type, form_data)
    filename = f"Ficha_{form_data.get('NOME', 'Ficha').replace(' ', '_')}.pdf"
    return send_file(
        pdf_buffer, 
        mimetype='application/pdf', 
        as_attachment=True, 
        download_name=filename
    )

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