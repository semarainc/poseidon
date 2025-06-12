from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from datetime import datetime
from sqlalchemy import func, or_, inspect as sqlalchemy_inspect
import os
import uuid
from werkzeug.utils import secure_filename
import traceback
# Import dari paket models (menggunakan models/__init__.py)
from models.models import db, Pelanggan, Penjualan, DetailPenjualan
from flask_login import login_required, current_user

customer_blueprint = Blueprint('customer', __name__, template_folder='templates', static_folder='static', url_prefix='/customer')

# --- MANAJEMEN PELANGGAN ---
@customer_blueprint.route('/')
@login_required
def pelanggan():
    search = request.args.get('search', '')
    query = Pelanggan.query
    if search:
        query = query.filter(
            or_(Pelanggan.nama.contains(search), Pelanggan.no_hp.contains(search))
        )
    pelanggan_list = query.order_by(Pelanggan.nama).all()
    return render_template('pelanggan.html', pelanggan_list=pelanggan_list, search=search)

@customer_blueprint.route('/tambah', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_pelanggan():
    if request.method == 'POST':
        nama = request.form['nama']
        no_hp = request.form.get('no_hp')
        alamat = request.form.get('alamat')
        new_pelanggan = Pelanggan(nama=nama, no_hp=no_hp, alamat=alamat)
        try:
            db.session.add(new_pelanggan)
            db.session.commit()
            flash('Pelanggan berhasil ditambahkan!', 'success')
            return redirect(url_for('customer.pelanggan'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Gagal menambahkan pelanggan: {str(e)}', 'error')
            current_app.logger.error(f"Error tambah pelanggan: {e}")
            return render_template('pelanggan_form.html', action='Tambah', pelanggan=request.form)
    return render_template('pelanggan_form.html', action='Tambah', pelanggan=None)

@customer_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_pelanggan(id):
    pelanggan_item = Pelanggan.query.get_or_404(id)
    if request.method == 'POST':
        pelanggan_item.nama = request.form['nama']
        pelanggan_item.no_hp = request.form.get('no_hp', pelanggan_item.no_hp)
        pelanggan_item.alamat = request.form.get('alamat', pelanggan_item.alamat)
        try:
            db.session.commit()
            flash('Pelanggan berhasil diperbarui!', 'success')
            return redirect(url_for('customer.pelanggan'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Gagal memperbarui pelanggan: {str(e)}', 'error')
            current_app.logger.error(f"Error edit pelanggan: {e}")
            return render_template('pelanggan_form.html', action='Edit', pelanggan=pelanggan_item)
    return render_template('pelanggan_form.html', action='Edit', pelanggan=pelanggan_item)

@customer_blueprint.route('/hapus/<int:id>', strict_slashes=False)
@login_required
def hapus_pelanggan(id):
    pelanggan_item = Pelanggan.query.get_or_404(id)
    try:
        if pelanggan_item.nama.lower() == 'umum': 
            flash('Pelanggan "Umum" tidak dapat dihapus.', 'error')
            return redirect(url_for('customer.pelanggan'))
            
        if Penjualan.query.filter_by(pelanggan_id=id).first():
             flash('Pelanggan tidak bisa dihapus karena memiliki riwayat transaksi.', 'error')
             return redirect(url_for('customer.pelanggan'))
        db.session.delete(pelanggan_item)
        db.session.commit()
        flash('Pelanggan berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f'Gagal menghapus pelanggan: {str(e)}', 'error')
        current_app.logger.error(f"Error hapus pelanggan: {e}")
    return redirect(url_for('customer.pelanggan'))