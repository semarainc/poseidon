# project/products/views.py

# IMPORTS
from datetime import datetime
from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import current_user, login_required
from project import db
from project.models import Supplier
from .forms import SupplierForm

# CONFIG
supplier_blueprint = Blueprint('supplier', __name__, template_folder='templates')

# ROUTES

#######################
#Supplier [FIXME]
#Potential Fix:
#   - Conccorenct Request (Which is unlikely in this case, but not impossible!) could cause ID conflicts when on high load
########################
@supplier_blueprint.route('/suppliers')
@login_required
def get_suppliers():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search = request.args.get('search[value]', type=str)

    query = Supplier.query
    if search:
        query = query.filter(db.or_(
            Supplier.kode_supplier.like(f'%{search}%'),
            Supplier.nama.like(f'%{search}%')
        ))

    total = query.count()
    items = query.offset(start).limit(length).all()

    data = [{
        'kode_supplier': item.kode_supplier,
        'nama': item.nama,
        'alamat': item.alamat,
        'telp': item.telp
    } for item in items]

    return jsonify({
        'draw': draw,
        'recordsTotal': total,
        'recordsFiltered': total,
        'data': data
    })

@supplier_blueprint.route('/supplier', methods=['GET', 'POST'])
@login_required
def create_supplier():
    if request.method == 'GET':
        form = SupplierForm(request.form)
        return render_template("crud_supplier.html", form=form)

    #Need To Check Whether Item Exists
    data = request.get_json()

    if data['nama'] == "":
        return jsonify({'message': 'Nama Supplier Tidak Boleh Kosong'}), 400

    # Generate next customer ID
    max_num = db.session.query(
        db.func.max(
            db.cast(
                db.func.substr(Supplier.kode_supplier, 6),
                db.Integer
            )
        )
    ).scalar()

    if max_num is not None:
        next_number = max_num + 1
    else:
        next_number = 1

    new_id = f'SUPL0{next_number}'

    new_item = Supplier(
        kode_supplier=new_id,
        nama=data['nama'],
        alamat=data['alamat'],
        telp=data['telp']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item Supplier created'}), 201

@supplier_blueprint.route('/supplier_update/<string:kodesupp>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_supplier(kodesupp):
    item = Supplier.query.get_or_404(kodesupp)

    if request.method == 'GET':
        return jsonify({
                "kode_pelanggan" :item.kode_supplier,
                "nama" : item.nama,
                "alamat": item.alamat,
                "telp": item.telp
                }
            ), 201
    if request.method == 'PUT':
        data = request.get_json()

        item.nama = data['nama']
        item.alamat = data['alamat']
        item.telp = data['telp']
        db.session.commit()
        return jsonify({'message': 'Item updated'})

    if request.method == 'DELETE':
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted'})
