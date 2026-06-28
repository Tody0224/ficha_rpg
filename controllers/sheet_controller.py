from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from models.character import CharacterModel
from models.pdf_generator import PDFGeneratorModel
import constants

sheet_bp = Blueprint('sheet', __name__)
pdf_generator = PDFGeneratorModel()

@sheet_bp.route('/create/<sheet_type>')
def create_form(sheet_type):
    # Rota pública: Qualquer um pode acessar o formulário de criação
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=None)

@sheet_bp.route('/edit/<sheet_type>/<int:entity_id>')
@login_required
def edit_entity(sheet_type, entity_id):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
        
    entity = CharacterModel.get_entity_by_id(sheet_type, entity_id)
    if not entity:
        return f"{sheet_type.capitalize()} não encontrado(a)", 404
        
    if 'usuario_id' in entity.keys() and entity['usuario_id'] != current_user.id:
        abort(403)
        
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=entity)

@sheet_bp.route('/save_and_process/<sheet_type>', methods=['POST'])
@sheet_bp.route('/save_and_process/<sheet_type>/<int:entity_id>', methods=['POST'])
def save_and_process(sheet_type, entity_id=None):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404

    action_type = request.form.get('action_type', 'pdf')
    
    # SE O USUÁRIO QUER SALVAR NO BANCO: Exige login manualmente aqui
    if action_type == "database":
        if not current_user.is_authenticated:
            flash('Você precisa estar logado para salvar fichas no sistema.', 'error')
            return redirect(url_for('auth.login'))
            
        if entity_id:
            existing = CharacterModel.get_entity_by_id(sheet_type, entity_id)
            if existing and 'usuario_id' in existing.keys() and existing['usuario_id'] != current_user.id:
                abort(403)

    form_data = request.form.to_dict()
    form_data['usuario_id'] = current_user.id if current_user.is_authenticated else None
    
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

    if action_type == "database":
        CharacterModel.save_entity(sheet_type, form_data, entity_id=entity_id)
        return redirect(url_for('main.hub'))

    # Se a ação for apenas gerar PDF, funciona de forma 100% anônima e sem login!
    pdf_buffer = pdf_generator.build_pdf(sheet_type, form_data)
    filename = f"Ficha_{form_data.get('NOME', 'Ficha').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)

@sheet_bp.route('/delete/<sheet_type>/<int:entity_id>', methods=['POST'])
@login_required
def delete_entity(sheet_type, entity_id):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Tipo inválido", 404

    existing = CharacterModel.get_entity_by_id(sheet_type, entity_id)
    if not existing:
        flash("Registo não encontrado.", "error")
        return redirect(url_for('main.hub'))

    usuario_dono = None
    try:
        if hasattr(existing, 'keys'):
            usuario_dono = existing['usuario_id']
    except Exception:
        try:
            usuario_dono = dict(existing).get('usuario_id')
        except Exception:
            pass

    if usuario_dono is None:
        try:
            usuario_dono = existing['USUARIO_ID']
        except Exception:
            pass

    if usuario_dono is not None and int(usuario_dono) != int(current_user.id):
        abort(403)

    CharacterModel.delete_entity(sheet_type, entity_id)
    flash(f"{sheet_type.capitalize()} excluído com sucesso!", "success")
    return redirect(url_for('main.hub'))