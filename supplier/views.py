from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from datetime import datetime
import traceback
from models.models import db, Supplier
from flask_login import login_required

supplier_blueprint = Blueprint('supplier', __name__, template_folder='templates', url_prefix='/supplier')

@supplier_blueprint.route('/', strict_slashes=False)
@login_required
def supplier_list():
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 25, type=int)
    allowed_sizes = [10, 25, 50, 100]
    if per_page not in allowed_sizes:
        per_page = 25
        
    query = Supplier.query
    if search:
        query = query.filter(Supplier.nama.contains(search))
    
    total_count = query.count()
    pagination = query.order_by(Supplier.nama).paginate(page=page, per_page=per_page, error_out=False)
    suppliers = pagination.items
    
    return render_template('supplier.html', 
                          suppliers=suppliers, 
                          search=search, 
                          pagination=pagination,
                          per_page=per_page,
                          total_count=total_count)

@supplier_blueprint.route('/tambah', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_supplier():
    if request.method == 'POST':
        nama = request.form['nama']
        no_hp = request.form.get('no_hp')
        alamat = request.form.get('alamat')
        new_supplier = Supplier(nama=nama, no_hp=no_hp, alamat=alamat)
        try:
            db.session.add(new_supplier)
            db.session.commit()
            flash('Supplier berhasil ditambahkan!', 'success')
            return redirect(url_for('supplier.supplier_list'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Gagal menambahkan supplier: {str(e)}', 'error')
            current_app.logger.error(f"Error tambah supplier: {e}")
            return render_template('supplier_form.html', action='Tambah', supplier=request.form)
    return render_template('supplier_form.html', action='Tambah', supplier=None)

@supplier_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_supplier(id):
    supplier_item = Supplier.query.get_or_404(id)
    if request.method == 'POST':
        supplier_item.nama = request.form['nama']
        supplier_item.no_hp = request.form.get('no_hp')
        supplier_item.alamat = request.form.get('alamat')
        try:
            db.session.commit()
            flash('Supplier berhasil diperbarui!', 'success')
            return redirect(url_for('supplier.supplier_list'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Gagal memperbarui supplier: {str(e)}', 'error')
            current_app.logger.error(f"Error edit supplier: {e}")
            return render_template('supplier_form.html', action='Edit', supplier=supplier_item)
    return render_template('supplier_form.html', action='Edit', supplier=supplier_item)

@supplier_blueprint.route('/hapus/<int:id>', strict_slashes=False)
@login_required
def hapus_supplier(id):
    supplier_item = Supplier.query.get_or_404(id)
    try:
        if supplier_item.barang_list.count():
            flash('Supplier tidak bisa dihapus karena terkait dengan barang.', 'error')
            return redirect(url_for('supplier.supplier_list'))
        db.session.delete(supplier_item)
        db.session.commit()
        flash('Supplier berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        traceback.print_exc()
        flash(f'Gagal menghapus supplier: {str(e)}', 'error')
        current_app.logger.error(f"Error hapus supplier: {e}")
    return redirect(url_for('supplier.supplier_list'))

# API endpoints (optional)
@supplier_blueprint.route('/api', methods=['GET'], strict_slashes=False)
@login_required
def get_suppliers_api():
    suppliers = Supplier.query.order_by(Supplier.nama).all()
    data = [{'id': s.id, 'nama': s.nama} for s in suppliers]
    return jsonify(data)
