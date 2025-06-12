from flask import Blueprint, render_template
from flask_login import login_required
from datetime import date, timedelta
from sqlalchemy import func
from models.models import db, Barang, Pelanggan, Penjualan

main_bp = Blueprint('main', __name__)

@main_bp.route('/', strict_slashes=False)
@login_required
def dashboard():
    total_barang = Barang.query.count()
    total_pelanggan = Pelanggan.query.count()
    total_transaksi = Penjualan.query.count()
    
    today = date.today()
    penjualan_hari_ini = db.session.query(func.sum(Penjualan.total_harga)).filter(
        func.date(Penjualan.tanggal) == today 
    ).scalar() or 0.0
    
    # Existing Stok Rendah (<10)
    barang_stok_rendah = Barang.query.filter(Barang.stok < 10).order_by(Barang.stok.asc()).all()

    # Barang Stok Mau Habis (stok >= 10 AND stok < 20)
    barang_stok_mau_habis = Barang.query.filter(Barang.stok >= 10, Barang.stok < 20).order_by(Barang.stok.asc()).all()

    near_expiry_limit = today + timedelta(days=30)
    barang_kadaluarsa_dekat = Barang.query.filter(
        Barang.tanggal_kadaluarsa != None,
        Barang.tanggal_kadaluarsa <= near_expiry_limit
    ).order_by(Barang.tanggal_kadaluarsa.asc()).limit(10).all()
    
    return render_template('dashboard.html', 
                         total_barang=total_barang,
                         total_pelanggan=total_pelanggan,
                         total_transaksi=total_transaksi,
                         penjualan_hari_ini=penjualan_hari_ini,
                         barang_stok_rendah=barang_stok_rendah,
                         barang_stok_mau_habis=barang_stok_mau_habis,
                         barang_kadaluarsa_dekat=barang_kadaluarsa_dekat,
                         today_date=today)

@main_bp.route('/about', strict_slashes=False)
def about():
    return render_template('about.html')