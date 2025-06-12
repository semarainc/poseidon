from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from models.models import db, StoreProfile

store_bp = Blueprint('store', __name__)

@store_bp.route('/pengaturan_toko', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def pengaturan_toko():
    if not current_user.is_admin:
        flash('Tidak memiliki hak akses.', 'error')
        return redirect(url_for('main.dashboard'))
    
    profile = StoreProfile.query.get(1)
    if not profile:
        profile = StoreProfile(id=1)
        db.session.add(profile)
        db.session.commit()

    if request.method == 'POST':
        profile.name = request.form.get('name', profile.name)
        profile.tagline = request.form.get('tagline', profile.tagline)
        profile.address = request.form.get('address', profile.address)
        profile.phone = request.form.get('phone', profile.phone)
        db.session.commit()
        flash('Profil toko berhasil diperbarui.', 'success')
        return redirect(url_for('store.pengaturan_toko'))

    return render_template('pengaturan_toko.html', profile=profile)