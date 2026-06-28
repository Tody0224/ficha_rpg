from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from models.user import Usuario

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.hub'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = Usuario.get_by_username(username)
        if user and user.verificar_password(password):
            login_user(user, remember=False)  
            return redirect(url_for('main.hub'))
        else:
            flash('Usuário ou senha incorretos.', 'error')
            
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.hub'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not password or len(password) < 6:
            flash('A senha deve ter pelo menos 6 caracteres.', 'error')
            return render_template('register.html')
            
        if Usuario.criar_usuario(username, password):
            flash('Conta criada com sucesso! Faça login abaixo.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Este nome de usuário já está em uso.', 'error')
            
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear() 

    return redirect(url_for('main.hub'))