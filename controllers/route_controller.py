from flask import Blueprint, render_template, request, jsonify, send_file, redirect, url_for, flash, abort, session
from flask_login import login_user, logout_user, login_required, current_user
from models.character import CharacterModel
from models.pdf_generator import PDFGeneratorModel
from models.user import Usuario
import constants
import random
from datetime import datetime, timedelta
import sqlite3
from models.mesa import MesaModel

bp = Blueprint('routes', __name__)
pdf_generator = PDFGeneratorModel()

# ─────────────────────────────────────────────────────────
# ROTAS DE AUTENTICAÇÃO (SISTEMA DE LOGIN)
# ─────────────────────────────────────────────────────────

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('routes.hub'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.get_by_username(username)
        if user and user.verificar_password(password):
            # CORREÇÃO: alterado de remember=True para remember=False
            # Isso impede que um cookie persistente de longo prazo seja gerado.
            login_user(user, remember=False)  
            return redirect(url_for('routes.hub'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
            
    return render_template('login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('routes.hub'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not password or len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
            
        if Usuario.criar_usuario(username, password):
            flash('Conta criada com sucesso! Faça login abaixo.', 'success')
            return redirect(url_for('routes.login'))
        else:
            flash('Este nome de usuário já está em uso.', 'error')
            
    return render_template('register.html')

# controllers/route_controller.py

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    # Limpa a sessão do Flask completamente
    session.clear() 
    # Força o redirecionamento para o login
    return redirect(url_for('routes.login'))


# ─────────────────────────────────────────────────────────
# ROTAS DO JOGO E GERENCIAMENTO DE FICHAS (PROTEGIDAS)
# ─────────────────────────────────────────────────────────

# ROTA RAIZ (O que acontece quando acessam a URL principal sem nada depois)
@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('routes.hub')) # Se logado, vai pro Hub
    return redirect(url_for('routes.login'))   # Se não, vai pro Login

@bp.route('/hub')
@login_required
def hub():
    conjuradores = CharacterModel.get_all_by_type('conjurador', current_user.id)
    conjuracoes = CharacterModel.get_all_by_type('conjuracao', current_user.id)
    familiares = CharacterModel.get_all_by_type('familiar', current_user.id)
    reliquias = CharacterModel.get_all_by_type('reliquia', current_user.id)
    
    # O seu MesaModel agora faz o trabalho pesado por baixo dos panos!
    minhas_mesas = MesaModel.get_mesas_por_usuario(current_user.id)
    
    return render_template('hub.html', 
                           conjuradores=conjuradores,
                           conjuracoes=conjuracoes,
                           familiares=familiares,
                           reliquias=reliquias,
                           mesas=minhas_mesas)

@bp.route('/create/<sheet_type>')
@login_required
def create_form(sheet_type):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404
    return render_template(f'{sheet_type}.html', constants=constants, sheet_type=sheet_type, entity=None)

@bp.route('/edit/<sheet_type>/<int:entity_id>')
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

@bp.route('/save_and_process/<sheet_type>', methods=['POST'])
@bp.route('/save_and_process/<sheet_type>/<int:entity_id>', methods=['POST'])
@login_required
def save_and_process(sheet_type, entity_id=None):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Not Found", 404

    if entity_id:
        existing = CharacterModel.get_entity_by_id(sheet_type, entity_id)
        if existing and 'usuario_id' in existing.keys() and existing['usuario_id'] != current_user.id:
            abort(403)

    form_data = request.form.to_dict()
    action_type = request.form.get('action_type', 'pdf')
    
    form_data['usuario_id'] = current_user.id
    
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
        return redirect(url_for('routes.hub'))

    pdf_buffer = pdf_generator.build_pdf(sheet_type, form_data)
    filename = f"Ficha_{form_data.get('NOME', 'Ficha').replace(' ', '_')}.pdf"
    return send_file(pdf_buffer, mimetype='application/pdf', as_attachment=True, download_name=filename)


@bp.route('/delete/<sheet_type>/<int:entity_id>', methods=['POST'])
@login_required
def delete_entity(sheet_type, entity_id):
    if sheet_type not in ['conjurador', 'conjuracao', 'familiar', 'reliquia']:
        return "Tipo inválido", 404

    existing = CharacterModel.get_entity_by_id(sheet_type, entity_id)
    if not existing:
        flash("Registo não encontrado.", "error")
        return redirect(url_for('routes.hub'))

    # Coleta o ID do dono convertendo o objeto de forma segura
    usuario_dono = None
    try:
        if hasattr(existing, 'keys'):
            usuario_dono = existing['usuario_id']
    except Exception:
        try:
            usuario_dono = dict(existing).get('usuario_id')
        except Exception:
            pass

    # Se não achou em minúsculo, tenta em maiúsculo
    if usuario_dono is None:
        try:
            usuario_dono = existing['USUARIO_ID']
        except Exception:
            pass

    # Validação do proprietário
    if usuario_dono is not None and int(usuario_dono) != int(current_user.id):
        abort(403)

    # Executa a exclusão definitiva
    CharacterModel.delete_entity(sheet_type, entity_id)
    flash(f"{sheet_type.capitalize()} excluído com sucesso!", "success")
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
@login_required
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

@bp.route('/api/active_users')
@login_required # Importante: só usuários logados podem ver quem está online
def get_active_users():
    # Define o limite de 5 minutos
    limite = datetime.now() - timedelta(minutes=5)
    
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # A query busca quem foi ativo nos últimos 5 min
    cursor.execute("SELECT username FROM usuarios WHERE last_active > ?", (limite,))
    users = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({"count": len(users), "users": users})

@bp.route('/mesa/criar', methods=['POST'])
@login_required
def criar_mesa():
    nome_mesa = request.form.get('nome_mesa')
    codigo = MesaModel.criar_mesa(nome_mesa, current_user.id)
    flash(f'Mesa criada! Código para convite: {codigo}', 'success')
    return redirect(url_for('routes.hub'))


@bp.route('/mesa/entrar', methods=['POST'])
@login_required
def entrar_mesa():
    codigo = request.form.get('codigo_mesa')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Busca a mesa pelo código
    cursor.execute("SELECT id FROM mesas WHERE codigo_convite = ?", (codigo,))
    mesa = cursor.fetchone()
    
    if mesa:
        mesa_id = mesa[0]
        
        # 1. Verifica se o usuário já é participante desta mesa
        cursor.execute("SELECT 1 FROM participantes WHERE mesa_id = ? AND usuario_id = ?", 
                       (mesa_id, current_user.id))
        ja_participa = cursor.fetchone()
        
        # 2. Se não existir, insere. Se já existir, não faz nada (apenas deixa entrar)
        if not ja_participa:
            cursor.execute("INSERT INTO participantes (mesa_id, usuario_id) VALUES (?, ?)", 
                           (mesa_id, current_user.id))
            conn.commit()
            flash('Você entrou na mesa com sucesso!', 'success')
        else:
            flash('Você já participa desta mesa.', 'info')
            
        conn.close()
        return redirect(url_for('routes.detalhes_mesa', mesa_id=mesa_id))
    else:
        conn.close()
        flash('Código de mesa inválido.', 'error')
        return redirect(url_for('routes.hub'))

@bp.route('/mesa/detalhes/<int:mesa_id>')
@login_required
def detalhes_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 1. Busca os dados básicos da mesa
    cursor.execute("SELECT id, nome, mestre_id, codigo_convite FROM mesas WHERE id = ?", (mesa_id,))
    mesa = cursor.fetchone()
    
    if not mesa:
        conn.close()
        abort(404)
    
    mestre_id = mesa[2]
    e_o_mestre = (mestre_id == current_user.id)
    codigo_convite = mesa[3]
    
    # 2. CORREÇÃO DO SQL: Busca os participantes normais OU o mestre da mesa
    cursor.execute("""
        SELECT DISTINCT u.username, u.id 
        FROM usuarios u
        LEFT JOIN participantes p ON p.usuario_id = u.id
        WHERE p.mesa_id = ? OR u.id = ?
    """, (mesa_id, mestre_id))
    jogadores_banco = cursor.fetchall()
    
    # 3. Busca as fichas de cada membro encontrado
    fichas_dos_jogadores = []
    for jogador in jogadores_banco:
        username_jogador = jogador[0]
        user_id_jogador = jogador[1]
        
        # Identifica se este usuário específico é o criador/mestre da mesa
        jogador_e_mestre = (mestre_id == user_id_jogador)
        
        dados_jogador = {
            'username': username_jogador,
            'is_master': jogador_e_mestre,
            'fichas': []
        }
        
        # Busca as fichas (Conjuradores, Conjurações, Familiares, Relíquias)
        cursor.execute("SELECT id, nome FROM conjuradores WHERE usuario_id = ?", (user_id_jogador,))
        for c in cursor.fetchall():
            dados_jogador['fichas'].append({'id': c[0], 'NOME': c[1], 'tipo': 'conjurador'})
            
        cursor.execute("SELECT id, nome FROM conjuracoes WHERE usuario_id = ?", (user_id_jogador,))
        for c in cursor.fetchall():
            dados_jogador['fichas'].append({'id': c[0], 'NOME': c[1], 'tipo': 'conjuracao'})
            
        cursor.execute("SELECT id, nome FROM familiares WHERE usuario_id = ?", (user_id_jogador,))
        for f in cursor.fetchall():
            dados_jogador['fichas'].append({'id': f[0], 'NOME': f[1], 'tipo': 'familiar'})
            
        cursor.execute("SELECT id, nome FROM reliquias WHERE usuario_id = ?", (user_id_jogador,))
        for r in cursor.fetchall():
            dados_jogador['fichas'].append({'id': r[0], 'NOME': r[1], 'tipo': 'reliquia'})
            
        fichas_dos_jogadores.append(dados_jogador)
    
    conn.close()
    
    return render_template(
        'mesa_detalhes.html', 
        mesa_nome=mesa[1], 
        mesa_id=mesa_id, 
        codigo_convite=codigo_convite,
        jogadores=fichas_dos_jogadores,
        e_mestre=e_o_mestre
    )

@bp.route('/mesa/delete/<int:mesa_id>', methods=['POST'])
@login_required
def delete_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        # 1. Validar primeiro se a mesa pertence mesmo ao utilizador atual
        cursor.execute("SELECT mestre_id FROM mesas WHERE id = ?", (mesa_id,))
        mesa = cursor.fetchone()
        
        if not mesa or int(mesa[0]) != int(current_user.id):
            conn.close()
            abort(403) # Não é o mestre da mesa
            
        # 2. Remover os participantes primeiro para evitar violações de integridade (Foreign Keys)
        cursor.execute("DELETE FROM participantes WHERE mesa_id = ?", (mesa_id,))
        
        # 3. Eliminar a mesa
        cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
        
        conn.commit()
        flash('Mesa excluída permanentemente!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao excluir mesa: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('routes.hub'))

@bp.route('/mesa/sair/<int:mesa_id>', methods=['POST'])
@login_required
def sair_da_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # Remove o usuário da tabela participantes
    cursor.execute("DELETE FROM participantes WHERE mesa_id = ? AND usuario_id = ?", 
                   (mesa_id, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Você saiu da mesa com sucesso.', 'info')
    return redirect(url_for('routes.hub'))