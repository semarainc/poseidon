from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, User

user_bp = Blueprint('user_bp', __name__, url_prefix='/users')

@user_bp.route('/')
@login_required
def user_list():
    if not current_user.is_admin:
        flash('Akses hanya untuk admin.', 'danger')
        return redirect(url_for('dashboard'))
    users = User.query.all()
    return render_template('users/user_list.html', users=users)

@user_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_user():
    if not current_user.is_admin:
        flash('Akses hanya untuk admin.', 'danger')
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        is_admin = bool(request.form.get('is_admin'))
        if User.query.filter_by(username=username).first():
            flash('Username sudah terdaftar.', 'danger')
        else:
            user = User(username=username, is_admin=is_admin)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Pengguna berhasil ditambahkan.', 'success')
            return redirect(url_for('user_bp.user_list'))
    return render_template('users/add_user.html')

@user_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        flash('Akses hanya untuk admin.', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        if request.form['password']:
            user.set_password(request.form['password'])
        user.is_admin = bool(request.form.get('is_admin'))
        db.session.commit()
        flash('Pengguna berhasil diperbarui.', 'success')
        return redirect(url_for('user_bp.user_list'))
    return render_template('users/edit_user.html', user=user)

@user_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        flash('Akses hanya untuk admin.', 'danger')
        return redirect(url_for('dashboard'))
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('Tidak dapat menghapus akun sendiri.', 'danger')
        return redirect(url_for('user_bp.user_list'))
    db.session.delete(user)
    db.session.commit()
    flash('Pengguna berhasil dihapus.', 'success')
    return redirect(url_for('user_bp.user_list'))
