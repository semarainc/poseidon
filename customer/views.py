# project/products/views.py

# IMPORTS
from datetime import datetime
from flask import render_template, Blueprint, request, redirect, url_for, flash, jsonify
from markupsafe import Markup
from flask_login import current_user, login_required
from project import db
from project.models import Pelanggan
from .forms import PelangganForm

# CONFIG
customer_blueprint = Blueprint('customer', __name__, template_folder='templates')

# ROUTES

#######################
#Pelanggan [FIXME]
#Potential Fix:
#   - Conccorenct Request (Which is unlikely in this case, but not impossible!) could cause ID conflicts when on high load
########################
@customer_blueprint.route('/customers')
@login_required
def get_customers():
    draw = request.args.get('draw', type=int)
    start = request.args.get('start', type=int)
    length = request.args.get('length', type=int)
    search = request.args.get('search[value]', type=str)

    query = Pelanggan.query
    if search:
        query = query.filter(db.or_(
            Pelanggan.kode_pelanggan.like(f'%{search}%'),
            Pelanggan.nama.like(f'%{search}%')
        ))

    total = query.count()
    items = query.offset(start).limit(length).all()

    data = [{
        'kode_pelanggan': item.kode_pelanggan,
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

@customer_blueprint.route('/customer', methods=['GET', 'POST'])
@login_required
def create_customer():
    if request.method == 'GET':
        form = PelangganForm(request.form)
        return render_template("crud_pelanggan.html", form=form)

    #Need To Check Whether Item Exists
    data = request.get_json()

    if data['nama'] == "":
        return jsonify({'message': 'Nama Pelanggan Tidak Boleh Kosong'}), 400

    # Generate next customer ID
    max_num = db.session.query(
        db.func.max(
            db.cast(
                db.func.substr(Pelanggan.kode_pelanggan, 6),
                db.Integer
            )
        )
    ).scalar()

    if max_num is not None:
        next_number = max_num + 1
    else:
        next_number = 1

    new_id = f'CUST0{next_number}'

    new_item = Pelanggan(
        kode_pelanggan=new_id,
        nama=data['nama'],
        alamat=data['alamat'],
        telp=data['telp']
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify({'message': 'Item Pelanggan created'}), 201

@customer_blueprint.route('/customer_update/<string:kodecust>', methods=['GET', 'PUT', 'DELETE'])
@login_required
def manage_customer(kodecust):
    item = Pelanggan.query.get_or_404(kodecust)

    if request.method == 'GET':
        return jsonify({
                "kode_pelanggan" :item.kode_pelanggan,
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
