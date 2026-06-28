from flask import Blueprint, request, redirect, url_for, flash, abort, render_template
from flask_login import login_required, current_user
import sqlite3
from models.mesa import MesaModel

table_bp = Blueprint('table', __name__)

@table_bp.route('/mesa/criar', methods=['POST'])
@login_required
def criar_mesa():
    nome_mesa = request.form.get('nome_mesa')
    codigo = MesaModel.criar_mesa(nome_mesa, current_user.id)
    flash(f'Mesa criada! Código para convite: {codigo}', 'success')
    return redirect(url_for('main.hub'))

@table_bp.route('/mesa/entrar', methods=['POST'])
@login_required
def entrar_mesa():
    codigo = request.form.get('codigo_mesa')
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM mesas WHERE codigo_convite = ?", (codigo,))
    mesa = cursor.fetchone()
    
    if mesa:
        mesa_id = mesa[0]
        cursor.execute("SELECT 1 FROM participantes WHERE mesa_id = ? AND usuario_id = ?", 
                       (mesa_id, current_user.id))
        ja_participa = cursor.fetchone()
        
        if not ja_participa:
            cursor.execute("INSERT INTO participantes (mesa_id, usuario_id) VALUES (?, ?)", 
                           (mesa_id, current_user.id))
            conn.commit()
            flash('Você entrou na mesa com sucesso!', 'success')
        else:
            flash('Você já participa desta mesa.', 'info')
            
        conn.close()
        return redirect(url_for('table.detalhes_mesa', mesa_id=mesa_id))
    else:
        conn.close()
        flash('Código de mesa inválido.', 'error')
        return redirect(url_for('main.hub'))

@table_bp.route('/mesa/detalhes/<int:mesa_id>')
@login_required
def detalhes_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, nome, mestre_id, codigo_convite FROM mesas WHERE id = ?", (mesa_id,))
    mesa = cursor.fetchone()
    
    if not mesa:
        conn.close()
        abort(404)
    
    mestre_id = mesa[2]
    e_o_mestre = (mestre_id == current_user.id)
    codigo_convite = mesa[3]
    
    cursor.execute("""
        SELECT DISTINCT u.username, u.id 
        FROM usuarios u
        LEFT JOIN participantes p ON p.usuario_id = u.id
        WHERE p.mesa_id = ? OR u.id = ?
    """, (mesa_id, mestre_id))
    jogadores_banco = cursor.fetchall()
    
    fichas_dos_jogadores = []
    for jogador in jogadores_banco:
        username_jogador = jogador[0]
        user_id_jogador = jogador[1]
        jogador_e_mestre = (mestre_id == user_id_jogador)
        
        dados_jogador = {
            'username': username_jogador,
            'is_master': jogador_e_mestre,
            'fichas': []
        }
        
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

@table_bp.route('/mesa/delete/<int:mesa_id>', methods=['POST'])
@login_required
def delete_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT mestre_id FROM mesas WHERE id = ?", (mesa_id,))
        mesa = cursor.fetchone()
        
        if not mesa or int(mesa[0]) != int(current_user.id):
            conn.close()
            abort(403)
            
        cursor.execute("DELETE FROM participantes WHERE mesa_id = ?", (mesa_id,))
        cursor.execute("DELETE FROM mesas WHERE id = ?", (mesa_id,))
        conn.commit()
        flash('Mesa excluída permanentemente!', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'Erro ao excluir mesa: {str(e)}', 'error')
    finally:
        conn.close()
        
    return redirect(url_for('main.hub'))

@table_bp.route('/mesa/sair/<int:mesa_id>', methods=['POST'])
@login_required
def sair_da_mesa(mesa_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM participantes WHERE mesa_id = ? AND usuario_id = ?", 
                   (mesa_id, current_user.id))
    conn.commit()
    conn.close()
    
    flash('Você saiu da mesa com sucesso.', 'info')
    return redirect(url_for('main.hub'))