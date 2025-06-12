from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from datetime import datetime
from sqlalchemy import func, or_, inspect as sqlalchemy_inspect
import os
import uuid
from werkzeug.utils import secure_filename
import traceback
# Import dari paket models (menggunakan models/models.py)
from models.models import db, Barang, DetailPenjualan, Kategori, Satuan, Supplier
from flask_login import login_required, current_user

products_blueprint = Blueprint('products', __name__, template_folder='templates', static_folder='static', url_prefix='/products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- MANAJEMEN BARANG ---
@products_blueprint.route('/', strict_slashes=False)
@login_required
def barang():
    search = request.args.get('search', '')
    query = Barang.query
    if search:
        query = query.filter(
            or_(Barang.nama_barang.contains(search), Barang.kode_barang.contains(search))
        )
    barang_list = query.order_by(Barang.nama_barang).all()
    return render_template('barang.html', barang_list=barang_list, search=search)

@products_blueprint.route('/tambah', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def tambah_barang():
    supplier_list = Supplier.query.order_by(Supplier.nama).all()
    if request.method == 'POST':
        kode_barang = request.form['kode_barang']
        nama_barang = request.form['nama_barang']
        kategori = request.form['kategori']
        satuan = request.form['satuan']
        supplier_id = request.form.get('supplier_id') or None
        stok = int(request.form.get('stok', 0))
        harga_pokok = float(request.form.get('harga_pokok', 0.0))
        harga_jual = float(request.form.get('harga_jual', 0.0))
        harga_grosir = float(request.form.get('harga_grosir', 0.0))
        batas_minimal_grosir = int(request.form.get('batas_minimal_grosir', 0))
        
        tanggal_kadaluarsa_str = request.form.get('tanggal_kadaluarsa')
        tanggal_kadaluarsa_obj = None
        if tanggal_kadaluarsa_str:
            try:
                tanggal_kadaluarsa_obj = datetime.strptime(tanggal_kadaluarsa_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format tanggal kadaluarsa tidak valid. Gunakan YYYY-MM-DD.', 'error')
                return render_template('barang_form.html', action='Tambah', barang=request.form, supplier_list=supplier_list)

        gambar_filename = None
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file and file.filename != '' and allowed_file(file.filename):
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = str(uuid.uuid4()) + '.' + ext
                filename = secure_filename(unique_filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                gambar_filename = filename
            elif file and file.filename != '':
                flash('Format file gambar tidak diizinkan! (Hanya PNG, JPG, JPEG, GIF)', 'error')
                return render_template('barang_form.html', action='Tambah', barang=request.form, supplier_list=supplier_list)

        existing = Barang.query.filter_by(kode_barang=kode_barang).first()
        if existing:
            flash('Kode barang sudah ada!', 'error')
            return render_template('barang_form.html', action='Tambah', barang=request.form, supplier_list=supplier_list)
        
        new_barang = Barang(
            kode_barang=kode_barang,
            nama_barang=nama_barang,
            satuan=satuan,
            kategori=kategori,
            stok=stok,
            harga_jual=harga_jual,
            harga_pokok=harga_pokok,
            harga_grosir=harga_grosir,
            batas_minimal_grosir=batas_minimal_grosir,
            supplier_id=supplier_id,
            gambar=gambar_filename,
            tanggal_kadaluarsa=tanggal_kadaluarsa_obj
        )
        try:
            db.session.add(new_barang)
            db.session.commit()
            flash('Barang berhasil ditambahkan!', 'success')
            return redirect(url_for('products.barang'))
        except Exception as e:
            db.session.rollback()
            if gambar_filename and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], gambar_filename)):
                 os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], gambar_filename))
            flash(f'Gagal menambahkan barang: {str(e)}', 'error')
            current_app.logger.error(f"Error tambah barang: {e}")
            return render_template('barang_form.html', action='Tambah', barang=request.form, supplier_list=supplier_list)
    
    return render_template('barang_form.html', action='Tambah', barang=None, supplier_list=supplier_list)

@products_blueprint.route('/edit/<int:id>', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def edit_barang(id):
    supplier_list = Supplier.query.order_by(Supplier.nama).all()
    barang_item = Barang.query.get_or_404(id)
    if request.method == 'POST':
        new_kode_barang = request.form['kode_barang']
        if new_kode_barang != barang_item.kode_barang:
            existing = Barang.query.filter(Barang.id != id, Barang.kode_barang == new_kode_barang).first()
            if existing:
                flash('Kode barang sudah digunakan oleh barang lain!', 'error')
                return render_template('barang_form.html', action='Edit', barang=barang_item, supplier_list=supplier_list)

        tanggal_kadaluarsa_str = request.form.get('tanggal_kadaluarsa')
        tanggal_kadaluarsa_obj = None 
        if tanggal_kadaluarsa_str: 
            try:
                tanggal_kadaluarsa_obj = datetime.strptime(tanggal_kadaluarsa_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Format tanggal kadaluarsa tidak valid.', 'error')
                return render_template('barang_form.html', action='Edit', barang=barang_item, supplier_list=supplier_list)
        
        gambar_filename = barang_item.gambar
        if 'gambar' in request.files:
            file = request.files['gambar']
            if file and file.filename != '' and allowed_file(file.filename):
                if barang_item.gambar and os.path.exists(os.path.join(current_app.config['UPLOAD_FOLDER'], barang_item.gambar)):
                    try:
                        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], barang_item.gambar))
                    except OSError as e:
                        current_app.logger.error(f"Error deleting old image: {e}")
                ext = file.filename.rsplit('.', 1)[1].lower()
                unique_filename = str(uuid.uuid4()) + '.' + ext
                filename = secure_filename(unique_filename)
                file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                gambar_filename = filename
            elif file and file.filename != '': 
                flash('Format file gambar tidak diizinkan! (Hanya PNG, JPG, JPEG, GIF)', 'error')
                return render_template('barang_form.html', action='Edit', barang=barang_item, supplier_list=supplier_list)

        supplier_id = request.form.get('supplier_id') or None
        barang_item.kode_barang = new_kode_barang
        barang_item.nama_barang = request.form['nama_barang']
        barang_item.satuan = request.form['satuan']
        barang_item.kategori = request.form['kategori']
        barang_item.stok = float(request.form.get('stok', barang_item.stok))
        barang_item.harga_jual = float(request.form.get('harga_jual', barang_item.harga_jual))
        barang_item.harga_pokok = float(request.form.get('harga_pokok', barang_item.harga_pokok))
        barang_item.harga_grosir = float(request.form.get('harga_grosir', barang_item.harga_grosir))
        barang_item.batas_minimal_grosir = int(request.form.get('batas_minimal_grosir', barang_item.batas_minimal_grosir))
        barang_item.supplier_id = supplier_id
        barang_item.gambar = gambar_filename
        barang_item.tanggal_kadaluarsa = tanggal_kadaluarsa_obj 
        
        try:
            db.session.commit()
            flash('Barang berhasil diperbarui!', 'success')
            return redirect(url_for('products.barang'))
        except Exception as e:
            db.session.rollback()
            traceback.print_exc()
            flash(f'Gagal memperbarui barang: {str(e)}', 'error')
            current_app.logger.error(f"Error edit barang: {e}")
            return render_template('barang_form.html', action='Edit', barang=barang_item, supplier_list=supplier_list)
    return render_template('barang_form.html', action='Edit', barang=barang_item, supplier_list=supplier_list)

@products_blueprint.route('/hapus/<int:id>', strict_slashes=False)
@login_required
def hapus_barang(id):
    barang_item = Barang.query.get_or_404(id)
    try:
        if DetailPenjualan.query.filter_by(barang_id=id).first():
            flash('Barang tidak bisa dihapus karena sudah ada dalam transaksi penjualan.', 'error')
            return redirect(url_for('products.barang'))
        gambar_path = None
        if barang_item.gambar:
             gambar_path = os.path.join(current_app.config['UPLOAD_FOLDER'], barang_item.gambar)
        db.session.delete(barang_item)
        db.session.commit()
        if gambar_path and os.path.exists(gambar_path):
            try:
                os.remove(gambar_path)
            except OSError as e:
                current_app.logger.error(f"Error deleting image file: {e}")
        flash('Barang berhasil dihapus!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Gagal menghapus barang: {str(e)}', 'error')
        current_app.logger.error(f"Error hapus barang: {e}")
    return redirect(url_for('products.barang'))

# --- API untuk Kategori dan Satuan ---
@products_blueprint.route('/api/kategori', methods=['GET'], strict_slashes=False)
@login_required
def get_all_kategori():
    kategori_list = Kategori.query.order_by(Kategori.nama).all()
    return jsonify({'kategori': [kategori.to_dict() for kategori in kategori_list]})

@products_blueprint.route('/api/kategori', methods=['POST'], strict_slashes=False)
@login_required
def add_kategori():
    data = request.get_json()
    if not data or 'nama' not in data:
        return jsonify({'success': False, 'message': 'Nama kategori harus diisi'}), 400
        
    nama = data['nama'].strip()
    if not nama:
        return jsonify({'success': False, 'message': 'Nama kategori tidak boleh kosong'}), 400
    
    existing = Kategori.query.filter(func.lower(Kategori.nama) == func.lower(nama)).first()
    if existing:
        return jsonify({'success': False, 'message': 'Kategori dengan nama ini sudah ada'}), 400
    
    try:
        new_kategori = Kategori(nama=nama)
        db.session.add(new_kategori)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Kategori berhasil ditambahkan', 
            'kategori': new_kategori.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding kategori: {e}")
        return jsonify({'success': False, 'message': f'Gagal menambahkan kategori: {str(e)}'}), 500

@products_blueprint.route('/api/kategori/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_kategori(id):
    kategori = Kategori.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'nama' not in data:
        return jsonify({'success': False, 'message': 'Nama kategori harus diisi'}), 400
        
    nama = data['nama'].strip()
    if not nama:
        return jsonify({'success': False, 'message': 'Nama kategori tidak boleh kosong'}), 400
    
    existing = Kategori.query.filter(Kategori.id != id, func.lower(Kategori.nama) == func.lower(nama)).first()
    if existing:
        return jsonify({'success': False, 'message': 'Kategori dengan nama ini sudah ada'}), 400
    
    try:
        kategori.nama = nama
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Kategori berhasil diperbarui', 
            'kategori': kategori.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating kategori: {e}")
        return jsonify({'success': False, 'message': f'Gagal memperbarui kategori: {str(e)}'}), 500

@products_blueprint.route('/api/kategori/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_kategori(id):
    kategori = Kategori.query.get_or_404(id)
       
    # Check if kategori is being used in any products
    used_in_products = Barang.query.filter_by(kategori=kategori.nama).first()
    if used_in_products:
        return jsonify({
            'success': False, 
            'message': f'Kategori sedang digunakan oleh barang: {used_in_products.nama_barang}'
        }), 400
    
    try:
        db.session.delete(kategori)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Kategori berhasil dihapus'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting kategori: {e}")
        return jsonify({'success': False, 'message': f'Gagal menghapus kategori: {str(e)}'}), 500

# Satuan (Unit) API
@products_blueprint.route('/api/satuan', methods=['GET'], strict_slashes=False)
@login_required
def get_all_satuan():
    satuan_list = Satuan.query.order_by(Satuan.nama).all()
    return jsonify({'satuan': [satuan.to_dict() for satuan in satuan_list]})

@products_blueprint.route('/api/satuan', methods=['POST'])
@login_required
def add_satuan():
    data = request.get_json()
    if not data or 'nama' not in data:
        return jsonify({'success': False, 'message': 'Nama satuan harus diisi'}), 400
        
    nama = data['nama'].strip()
    deskripsi = data.get('deskripsi', '').strip()
    
    if not nama:
        return jsonify({'success': False, 'message': 'Nama satuan tidak boleh kosong'}), 400
    
    existing = Satuan.query.filter(func.lower(Satuan.nama) == func.lower(nama)).first()
    if existing:
        return jsonify({'success': False, 'message': 'Satuan dengan nama ini sudah ada'}), 400
    
    try:
        new_satuan = Satuan(nama=nama, deskripsi=deskripsi)
        db.session.add(new_satuan)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Satuan berhasil ditambahkan', 
            'satuan': new_satuan.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding satuan: {e}")
        return jsonify({'success': False, 'message': f'Gagal menambahkan satuan: {str(e)}'}), 500

@products_blueprint.route('/api/satuan/<int:id>', methods=['PUT'], strict_slashes=False)
@login_required
def update_satuan(id):
    satuan = Satuan.query.get_or_404(id)
    data = request.get_json()
    
    if not data or 'nama' not in data:
        return jsonify({'success': False, 'message': 'Nama satuan harus diisi'}), 400
        
    nama = data['nama'].strip()
    deskripsi = data.get('deskripsi', satuan.deskripsi or '').strip()
    
    if not nama:
        return jsonify({'success': False, 'message': 'Nama satuan tidak boleh kosong'}), 400
    
    existing = Satuan.query.filter(Satuan.id != id, func.lower(Satuan.nama) == func.lower(nama)).first()
    if existing:
        return jsonify({'success': False, 'message': 'Satuan dengan nama ini sudah ada'}), 400
    
    try:
        satuan.nama = nama
        satuan.deskripsi = deskripsi
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Satuan berhasil diperbarui', 
            'satuan': satuan.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating satuan: {e}")
        return jsonify({'success': False, 'message': f'Gagal memperbarui satuan: {str(e)}'}), 500

@products_blueprint.route('/api/satuan/<int:id>', methods=['DELETE'], strict_slashes=False)
@login_required
def delete_satuan(id):
    satuan = Satuan.query.get_or_404(id)
    
    # Check if satuan is being used in any products
    used_in_products = Barang.query.filter_by(satuan=satuan.nama).first()
    if used_in_products:
        return jsonify({
            'success': False, 
            'message': f'Satuan sedang digunakan oleh barang: {used_in_products.nama_barang}'
        }), 400
    
    try:
        db.session.delete(satuan)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Satuan berhasil dihapus'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting satuan: {e}")
        return jsonify({'success': False, 'message': f'Gagal menghapus satuan: {str(e)}'}), 500