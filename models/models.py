from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os

db = SQLAlchemy()

# Cross-platform file lock/unlock
if os.name == 'nt':  # Windows
    import msvcrt
    def lock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_LOCK, 1)
    def unlock_file(f):
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
else:  # Unix/Linux
    import fcntl
    def lock_file(f):
        fcntl.flock(f, fcntl.LOCK_EX)
    def unlock_file(f):
        fcntl.flock(f, fcntl.LOCK_UN)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship ke antrian penjualan
    antrian_penjualan = db.relationship('PenjualanAntrian', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Kategori(db.Model):
    __tablename__ = 'kategori'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Kategori {self.nama}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama
        }

class Satuan(db.Model):
    __tablename__ = 'satuan'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(20), unique=True, nullable=False)
    deskripsi = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Satuan {self.nama}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'deskripsi': self.deskripsi
        }

class Supplier(db.Model):
    __tablename__ = 'supplier'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=True)
    alamat = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    barang_list = db.relationship('Barang', backref='supplier_data', lazy='dynamic')
 
    def __repr__(self):
        return f'<Supplier {self.nama}>'

class Barang(db.Model):
    __tablename__ = 'barang'
    
    id = db.Column(db.Integer, primary_key=True)
    kode_barang = db.Column(db.String(50), unique=True, nullable=False)
    nama_barang = db.Column(db.String(100), nullable=False)
    kategori = db.Column(db.String(50), nullable=False)
    stok = db.Column(db.Float, nullable=False, default=0)
    # Harga dan keuntungan
    harga_pokok = db.Column(db.Float, nullable=True, default=0)  # Harga modal/beli
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=True)
    harga_jual = db.Column(db.Float, nullable=False)  # Harga default (eceran)
    harga_grosir = db.Column(db.Float, nullable=True)  # Harga untuk pembelian qty besar
    batas_minimal_grosir = db.Column(db.Integer, nullable=True, default=10)  # Minimal pembelian untuk harga grosir
    satuan = db.Column(db.String(20), nullable=True, default='Pcs')  # Unit produk (Kg, Liter, Pcs, dll)
    gambar = db.Column(db.String(100), nullable=True) 
    tanggal_kadaluarsa = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Barang {self.nama_barang}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'kode_barang': self.kode_barang,
            'nama_barang': self.nama_barang,
            'kategori': self.kategori,
            'stok': self.stok,
            'harga_pokok': self.harga_pokok,
            'harga_jual': self.harga_jual,
            'harga_grosir': self.harga_grosir,
            'batas_minimal_grosir': self.batas_minimal_grosir,
            'satuan': self.satuan,
            'gambar': self.gambar,
            'tanggal_kadaluarsa': self.tanggal_kadaluarsa.strftime('%Y-%m-%d') if self.tanggal_kadaluarsa else None,
            'supplier_id': self.supplier_id,
            'supplier_nama': self.supplier_data.nama if self.supplier_data else None
        }
    
    def hitung_persentase_keuntungan(self, harga_jual_tertentu=None):
        """Menghitung persentase keuntungan berdasarkan harga jual dan harga pokok"""
        if not self.harga_pokok or self.harga_pokok == 0:
            return 0
        
        harga = harga_jual_tertentu if harga_jual_tertentu is not None else self.harga_jual
        return ((harga - self.harga_pokok) / self.harga_pokok) * 100

class Pelanggan(db.Model):
    __tablename__ = 'pelanggan'
    
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    no_hp = db.Column(db.String(20), nullable=True)
    alamat = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    penjualan_records = db.relationship('Penjualan', backref='pelanggan_data', lazy='dynamic')
    
    def __repr__(self):
        return f'<Pelanggan {self.nama}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'nama': self.nama,
            'no_hp': self.no_hp,
            'alamat': self.alamat
        }

class Penjualan(db.Model):
    __tablename__ = 'penjualan'
    
    id = db.Column(db.Integer, primary_key=True)
    no_transaksi = db.Column(db.String(50), unique=True, nullable=False)
    tanggal = db.Column(db.DateTime, default=datetime.utcnow)
    pelanggan_id = db.Column(db.Integer, db.ForeignKey('pelanggan.id'), nullable=True)
    total_harga = db.Column(db.Float, nullable=False, default=0)
    status = db.Column(db.String(20), default='selesai') # 'selesai', 'pending', 'batal'
    metode_pembayaran = db.Column(db.String(50), nullable=True, default='tunai')
    jumlah_bayar = db.Column(db.Float, nullable=True) # Jumlah uang yang dibayarkan customer
    kembalian = db.Column(db.Float, nullable=True)    # Kembalian untuk customer
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    detail_penjualan = db.relationship('DetailPenjualan', backref='penjualan_info', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Penjualan {self.no_transaksi}>'
    
    def to_dict(self): # Expanded for more details if needed
        return {
            'id': self.id,
            'no_transaksi': self.no_transaksi,
            'tanggal': self.tanggal.strftime('%Y-%m-%d %H:%M:%S'),
            'pelanggan_id': self.pelanggan_id,
            'total_harga': self.total_harga,
            'status': self.status,
            'metode_pembayaran': self.metode_pembayaran,
            'jumlah_bayar': self.jumlah_bayar,
            'kembalian': self.kembalian,
            'pelanggan_nama': self.pelanggan_data.nama if self.pelanggan_data else None,
            'items': [item.to_dict() for item in self.detail_penjualan]
        }

class PenjualanAntrian(db.Model):
    __tablename__ = 'penjualan_antrian'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    nama_antrian = db.Column(db.String(50), nullable=False)
    data_antrian = db.Column(db.Text, nullable=True)  # JSON string dari cart/items
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<PenjualanAntrian {self.nama_antrian} milik user {self.user_id}>'

class StoreProfile(db.Model):
    __tablename__ = 'store_profile'
    id = db.Column(db.Integer, primary_key=True, default=1)
    name = db.Column(db.String(100), default='POSEIDON')
    tagline = db.Column(db.String(200), default='Toko Alat Perkebunan Terlengkap')
    address = db.Column(db.String(200), default='Jl. Kebun Raya No. 123, Denpasar')
    phone = db.Column(db.String(50), default='(0361) 123-4567')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<StoreProfile {self.name}>'

class DetailPenjualan(db.Model):
    __tablename__ = 'detail_penjualan'
    
    id = db.Column(db.Integer, primary_key=True)
    penjualan_id = db.Column(db.Integer, db.ForeignKey('penjualan.id'), nullable=False)
    barang_id = db.Column(db.Integer, db.ForeignKey('barang.id'), nullable=False)
    jumlah = db.Column(db.Float, nullable=False)  # Mendukung qty desimal
    harga_satuan = db.Column(db.Float, nullable=False) # Harga saat penjualan terjadi
    subtotal = db.Column(db.Float, nullable=False)
    tipe_harga = db.Column(db.String(20), default='eceran')  # 'eceran' atau 'grosir'
    
    # Relationship to Barang model
    barang_data = db.relationship('Barang', backref='penjualan_details') # Changed from barang to barang_data for clarity
    
    def __repr__(self):
        return f'<DetailPenjualan {self.penjualan_id}-{self.barang_id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'penjualan_id': self.penjualan_id,
            'barang_id': self.barang_id,
            'jumlah': self.jumlah,
            'harga_satuan': self.harga_satuan,
            'subtotal': self.subtotal,
            'tipe_harga': self.tipe_harga,
            'nama_barang': self.barang_data.nama_barang if self.barang_data else '',
            'kode_barang': self.barang_data.kode_barang if self.barang_data else '',
            'satuan': self.barang_data.satuan if self.barang_data else 'Pcs'
        }

def init_db_with_app_context(app_instance, instance_folder_name='instance'):
    from sqlalchemy import inspect as sqlalchemy_inspect
    from lib.apppath import app_path

    # Buat folder instance jika belum ada
    instance_folder_path = app_path(instance_folder_name)
    os.makedirs(instance_folder_path, exist_ok=True)

    lockfile_path = app_path(f'{instance_folder_name}/poseidon_db_init.lock')
    with open(lockfile_path, 'w') as lockfile:
        lock_file(lockfile)
        try:
            with app_instance.app_context():
                inspector = sqlalchemy_inspect(db.engine)
                required_tables = ['barang', 'pelanggan', 'penjualan', 'detail_penjualan', 'user', 'penjualan_antrian', 'store_profile', 'supplier', 'kategori', 'satuan']
                existing_tables = inspector.get_table_names()
                missing_tables = [t for t in required_tables if t not in existing_tables]
                if missing_tables:
                    print(f"Tabel berikut belum ada: {missing_tables}, menjalankan db.create_all()...")
                    db.create_all()
                else:
                    print("Semua tabel sudah ada.")

                # User admin
                if not User.query.filter_by(username='admin').first():
                    admin = User(username='admin', is_admin=True)
                    admin.set_password('admin123')
                    db.session.add(admin)

                # Supplier default
                if not Supplier.query.filter_by(nama='Default Supplier').first():
                    db.session.add(Supplier(nama='Default Supplier', no_hp='-', alamat='-'))

                # Barang sample
                sample_barang = [
                    dict(kode_barang='SKP001', nama_barang='Sekop Kecil', kategori='Alat Taman', stok=25, harga_pokok=25000, harga_jual=35000, harga_grosir=30000, satuan='Pcs', tanggal_kadaluarsa=date(2025, 12, 31)),
                    dict(kode_barang='BJH001', nama_barang='Benih Jagung Hibrida', kategori='Benih', stok=50, harga_pokok=18000, harga_jual=25000, harga_grosir=22000, satuan='Pack', tanggal_kadaluarsa=date(2024, 8, 15)),
                    dict(kode_barang='PPK001', nama_barang='Pupuk NPK 1kg', kategori='Pupuk', stok=100, harga_pokok=10000, harga_jual=15000, harga_grosir=13000, satuan='Kg', tanggal_kadaluarsa=date(2024, 5, 1)),
                    dict(kode_barang='SPR001', nama_barang='Sprayer Elektrik 16L', kategori='Alat Semprot', stok=10, harga_pokok=250000, harga_jual=350000, harga_grosir=325000, satuan='Unit'),
                    dict(kode_barang='IRG001', nama_barang='Selang Irigasi 10m', kategori='Irigasi', stok=30, harga_pokok=50000, harga_jual=75000, harga_grosir=65000, satuan='Roll'),
                ]
                for barang in sample_barang:
                    if not Barang.query.filter_by(kode_barang=barang['kode_barang']).first():
                        db.session.add(Barang(**barang))

                # Pelanggan sample
                if not Pelanggan.query.filter_by(nama='Umum').first():
                    db.session.add(Pelanggan(nama='Umum', no_hp='-', alamat='-'))
                sample_pelanggan = [
                    dict(nama='Pak Tani', no_hp='081234567890', alamat='Desa Sukamaju RT 01/01'),
                    dict(nama='Ibu Sri', no_hp='085678901234', alamat='Komplek Agropolitan A1'),
                ]
                for pelanggan in sample_pelanggan:
                    if pelanggan['nama'].lower() != 'umum' and not Pelanggan.query.filter_by(nama=pelanggan['nama']).first():
                        db.session.add(Pelanggan(**pelanggan))

                # Store profile
                if not StoreProfile.query.get(1):
                    db.session.add(StoreProfile(id=1))

                try:
                    db.session.commit()
                    print("Database initialized/checked for sample data using models.py!")
                except Exception as e:
                    db.session.rollback()
                    if 'UNIQUE constraint failed: user.username' in str(e):
                        print("User 'admin' sudah ada, dilewati (race condition handled).")
                    else:
                        print(f"Error during database initialization with models.py: {e}")
        finally:
            unlock_file(lockfile)


def generate_no_transaksi():
    now = datetime.now()
    date_str = now.strftime('%Y%m%d') # e.g., 20231027
    
    # Find the last transaction for today to determine the next sequence number
    last_transaction_today = Penjualan.query.filter(
        Penjualan.no_transaksi.like(f"TRX{date_str}%")
    ).order_by(Penjualan.no_transaksi.desc()).first()
    
    if last_transaction_today:
        # Extract the sequence number part (last 3 digits)
        last_num_str = last_transaction_today.no_transaksi[-3:]
        try:
            last_num = int(last_num_str)
            new_num = last_num + 1
        except ValueError:
            # Fallback if the number part is not as expected, count existing for today
            new_num = Penjualan.query.filter(Penjualan.no_transaksi.like(f"TRX{date_str}%")).count() + 1
    else:
        # First transaction of the day
        new_num = 1
    
    return f"TRX{date_str}{new_num:03d}" # Format to 3 digits, e.g., TRX20231027001