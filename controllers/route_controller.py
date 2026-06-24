# controllers/route_controller.py
from flask import Blueprint, render_template, request, jsonify, send_file
from models.character import CharacterModel
from models.pdf_generator import PDFGeneratorModel
import constants

bp = Blueprint('routes', __name__)
pdf_generator = PDFGeneratorModel()

@bp.route('/')
def hub():
    return render_template('hub.html')

@bp.route('/create/<sheet_type>')
def create_form(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    # Injeta as constantes diretamente no Jinja para povoar os inputs HTML select
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type)

@bp.route('/api/calculate_resources', methods=['POST'])
def api_calculate():
    data = request.json
    res = CharacterModel.calculate_resources(data.get('grau', 1), data.get('vitalidade', 1), data.get('sintonia', 1))
    return jsonify(res)

@bp.route('/api/test_mode/<sheet_type>')
def api_test_mode(sheet_type):
    test_data = CharacterModel.get_test_data(sheet_type)
    return jsonify(test_data)

@bp.route('/generate_pdf/<sheet_type>', methods=['POST'])
def generate_pdf(sheet_type):
    form_data = request.form.to_dict()
    
    # Processamentos pontuais equivalentes aos que a interface desktop fazia antes de enviar para o ReportLab
    if sheet_type == "conjurador":
        form_data['PASSIVA_ESCOLA'] = constants.PASSIVAS_ESCOLAS.get(form_data.get('ESCOLA'), '')
        pericias_list = request.form.getlist('pericias')
        form_data['PERICIAS'] = ", ".join(pericias_list)
        # Força o recálculo seguro no servidor para evitar fraudes ou dados zerados no PDF
        res = CharacterModel.calculate_resources(form_data.get('GRAU', 1), form_data.get('VITALIDADE', 1), form_data.get('SINTONIA', 1))
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
            form_data['FAMILIAR'] = f"Familiar de {form_data.get('NOME')}"

    pdf_buffer = pdf_generator.build_pdf(sheet_type, form_data)
    filename = f"Ficha_{form_data.get('NOME', 'SemNome').replace(' ', '_')}.pdf"
    
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)