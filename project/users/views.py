# project/users/views.py

# IMPORTS
from flask import render_template, Blueprint, request, redirect, url_for, flash,  abort
from markupsafe import Markup
from sqlalchemy.exc import IntegrityError
from flask_login import login_user, current_user, login_required, logout_user
from itsdangerous import URLSafeTimedSerializer
from threading import Thread
from datetime import datetime, timedelta

from .forms import RegisterForm, LoginForm, PasswordForm
from project import app, db
from project.models import User


# CONFIG
users_blueprint = Blueprint('users', __name__, template_folder='templates')


# ROUTES
@users_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_user = User(form.username.data, form.password.data)
                new_user.authenticated = True
                db.session.add(new_user)
                db.session.commit()
                message = Markup(
                    "<strong>Success!</strong> Thanks for registering. Please check your email to confirm your email address.")
                flash(message, 'success')
                return redirect(url_for('home'))
            except IntegrityError:
                db.session.rollback()
                message = Markup(
                    "<strong>Error!</strong> Unable to process registration.")
                flash(message, 'danger')
    return render_template('register.html', form=form)


@users_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)

    if request.method == 'GET':
        if not current_user.is_anonymous:
            if current_user.authenticated:
                return redirect(url_for('home'))

    if request.method == 'POST':
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is not None and user.is_correct_password(form.password.data):
                user.authenticated = True
                user.last_logged_in = user.current_logged_in
                user.current_logged_in = datetime.now()
                db.session.add(user)
                db.session.commit()
                login_user(user)
                message = Markup(
                    "<strong>Welcome back!</strong> You are now successfully logged in.")
                flash(message, 'success')
                return redirect(url_for('home'))
            else:
                message = Markup(
                    "<strong>Error!</strong> Incorrect login credentials.")
                flash(message, 'danger')
    return render_template('login_new.html', form=form)


@users_blueprint.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    return render_template('user_profile.html')

@users_blueprint.route('/admin_view_users')
@login_required
def admin_view_users():
    if current_user.role != 'admin':
        abort(403)
    else:
        users = User.query.order_by(User.id).all()
        return render_template('admin_view_users.html', users=users)


@users_blueprint.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        abort(403)
    else:
        users = User.query.order_by(User.id).all()
        kpi_mau = User.query.filter(User.last_logged_in > (datetime.today() - timedelta(days=30))).count()
        kpi_total_confirmed = 1
        kpi_mau_percentage = (100 / kpi_total_confirmed) * kpi_mau
        return render_template('admin_dashboard.html', users=users, kpi_mau=kpi_mau, kpi_total_confirmed=kpi_total_confirmed, kpi_mau_percentage=kpi_mau_percentage)


@users_blueprint.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    message = Markup("<strong>Goodbye!</strong> You are now logged out.")
    flash(message, 'info')
    return redirect(url_for('users.login'))


@users_blueprint.route('/password_change', methods=["GET", "POST"])
@login_required
def user_password_change():
    form = PasswordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = current_user
            user.password = form.password.data
            db.session.add(user)
            db.session.commit()
            message = Markup(
                "Password has been updated!")
            flash(message, 'success')
            return redirect(url_for('users.user_profile'))

    return render_template('password_change.html', form=form)
