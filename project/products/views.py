# project/products/views.py

# IMPORTS
from datetime import datetime
from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import current_user, login_required
from project import db
from project.models import User, Barang, Satuan, Kelompok
from .forms import BarangForm

# CONFIG
products_blueprint = Blueprint('products', __name__, template_folder='templates')

#HELPER
def isBarangExists(kodebrg):
    #Check Whether Kode_Barang Already Exists on DB
    brg_ = Barang.query.filter_by(kode_barang=kodebrg).first()

    if brg_:
        return True

    return False

def kadaluarsa_sanitizer(kadaluarsa):
    if kadaluarsa == "":
        return -1

    tgl_ = datetime.strptime(kadaluarsa, "%Y-%m-%d")

    return datetime.timestamp(tgl_) #Set To UnixTimestamp

def kadaluarsa_toDate(timestamp):
    if str(timestamp) == "-1":
        return ""

    return str(datetime.fromtimestamp(float(timestamp)).strftime("%Y-%m-%d"))

# ROUTES
@products_blueprint.route('/all_items', methods=['GET', 'POST'])
@login_required
def all_items():
    """Render homepage"""
    all_user_items = Items.query.filter_by(user_id=current_user.id)
    return render_template('all_items.html', items=all_user_items)


@products_blueprint.route('/products')
@login_required
def get_items():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search = request.args.get('search[value]', type=str)

    query = Barang.query
    if search:
        query = query.filter(db.or_(
            Barang.kode_barang.like(f'%{search}%'),
            Barang.nama_barang.like(f'%{search}%')
        ))

    total = query.count()
    items = query.offset(start).limit(length).all()

    data = [{
        'kode_barang': item.kode_barang,
        'nama_barang': item.nama_barang,
        'satuan': item.satuan,
        'kelompok': item.kelompok,
        'kadaluarsa': kadaluarsa_toDate(item.kadaluarsa),
        'harga_pokok': item.harga_pokok,
        'harga_jual': item.harga_jual,
        'stok': item.stok,
        'stok_minimal' : item.stok_minimal
    } for item in items]

    return jsonify({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': total,
        'data': data
    })

@products_blueprint.route('/product', methods=['GET', 'POST'])
@login_required
def create_item():
    if request.method == 'GET':
        form = BarangForm(request.form)

        #Retrive Data from DB
        satuan_ = Satuan.query.all()
        kelompok_ = Kelompok.query.all()

        #All Choices in Forms
        form.satuan.choices = [g.satuan for g in satuan_]
        form.kelompok.choices = [g.kelompok for g in kelompok_]
        return render_template("crud_barang.html", form=form)

    #Need To Check Whether Item Exists
    data = request.get_json()

    #Ensure Input barang Valid First
    if data.get("kode_barang", None) is None:
        return jsonify({'message': 'Kode Barang Not Included!'}), 400

    #Check Whether Kode_Barang Already Exists on DB
    if isBarangExists(data.get("kode_barang", None)):
        return jsonify({'message': 'Kode Barang is Already Exists'}), 400

    new_item = Barang(
        kode_barang=data['kode_barang'],
        nama_barang=data['nama_barang'],
        satuan=data['satuan'],
        kelompok=data['kelompok'],
        kadaluarsa=kadaluarsa_sanitizer(data['kadaluarsa']),
        harga_pokok=data['harga_pokok'],
        harga_jual=data['harga_jual'],
        stok=data['stok'],
        stok_minimal=data['stok_minimal']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item Barang created'}), 201

@products_blueprint.route('/product_update/<string:kodebrg>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_item(kodebrg):
    item = Barang.query.get_or_404(kodebrg)

    if request.method == 'GET':
        return jsonify({
                "kode_barang" :item.kode_barang,
                "nama_barang" : item.nama_barang,
                "satuan": item.satuan,
                "kelompok": item.kelompok,
                "kadaluarsa": kadaluarsa_toDate(item.kadaluarsa),
                "harga_pokok": item.harga_pokok,
                "harga_jual": item.harga_jual,
                "stok": item.stok,
                "stok_minimal": item.stok_minimal
                }
            ), 201
    if request.method == 'PUT':
        data = request.get_json()

        #Check Whether Kode_Barang Already Exists on DB
        print(data["kode_barang"])
        print(kodebrg)
        if data["kode_barang"] != kodebrg: #bug karena gk bisa cek klo kodebrg berubah
            if isBarangExists(data.get("kode_barang", None)):
                return jsonify({'message': 'Kode Barang is Already Exists'}), 400

        item.kode_barang = data['kode_barang']
        item.nama_barang = data['nama_barang']
        item.satuan = data['satuan']
        item.kelompok = data['kelompok']
        item.kadaluarsa = kadaluarsa_sanitizer(data['kadaluarsa'])
        item.harga_pokok = data['harga_pokok']
        item.harga_jual = data['harga_jual']
        item.stok = data['stok']
        item.stok_minimal = data['stok_minimal']
        db.session.commit()
        return jsonify({'message': 'Item updated'})

    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted'})
