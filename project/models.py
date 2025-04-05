from project import db, bcrypt
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from datetime import datetime


#############################
#
# Berkaitan dengan Data User/Pengguna [FIXME]
#
#############################
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password = db.Column(db.LargeBinary(60), nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    registered_on = db.Column(db.DateTime, nullable=True)
    last_logged_in = db.Column(db.DateTime, nullable=True)
    current_logged_in = db.Column(db.DateTime, nullable=True)
    role = db.Column(db.String, default='user')

    # Relationships [This is making me mad btw :) ]
    pembelianhd_entries = db.relationship("PembelianHD", back_populates="pengguna")  # Relasi ke PembelianHD
    penjualanhd_entries = db.relationship("PenjualanHD", back_populates="pengguna")  # <-- Relasi ke PenjualanHD

    items = db.relationship('Items', backref='user', lazy='dynamic')

    def __init__(self, username, password, role='user'):
        self.username = username
        self.password = password
        self.authenticated = False
        self.registered_on = datetime.now()
        self.last_logged_in = None
        self.current_logged_in = datetime.now()
        self.role = role

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, password):
        self._password = bcrypt.generate_password_hash(password)

    @hybrid_method
    def is_correct_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    @property
    def is_active(self):
        """Always True, as all users are active."""
        return True

    @property
    def is_anonymous(self):
        """Always False, as anonymous users aren't supported."""
        return False

    def get_id(self):
        """Return the username address to satisfy Flask-Login's requirements."""
        """Requires use of Python 3"""
        return str(self.id)

    def __repr__(self):
        return '<User {}>'.format(self.username)


#############################
#
# Berkaitan dengan Data Barang
#
#############################
class Satuan(db.Model):
    __tablename__ = 'satuan'
    satuan = db.Column(db.String, nullable=False, primary_key=True)

class Kelompok(db.Model):
    __tablename__ = 'kelompok'
    kelompok = db.Column(db.String, nullable=False, primary_key=True)

class Barang(db.Model):
    __tablename__ = 'databarang'
    kode_barang = db.Column(db.String, primary_key=True)
    nama_barang = db.Column(db.String, nullable=False)
    satuan = db.Column(db.String, nullable=False)
    kelompok = db.Column(db.String, nullable=False)
    kadaluarsa = db.Column(db.String, nullable=False)
    harga_pokok = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    harga_jual = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    stok = db.Column(db.Integer, nullable=False)
    stok_minimal = db.Column(db.Integer, nullable=False)

#############################
#
# Berkaitan dengan Data Pelanggan
#
#############################
class Pelanggan(db.Model):
    __tablename__ = 'pelanggan'
    kode_pelanggan = db.Column(db.String, primary_key=True)
    nama = db.Column(db.String, nullable=False)
    alamat = db.Column(db.String, nullable=False)
    telp = db.Column(db.String, nullable=False)

#############################
#
# Berkaitan dengan Data Pemasok/Supplier
#
#############################
class Supplier(db.Model):
    __tablename__ = 'supplier'
    kode_supplier = db.Column(db.String, primary_key=True)
    nama = db.Column(db.String, nullable=False)
    alamat = db.Column(db.String, nullable=True)
    telp = db.Column(db.String, nullable=True)

    # Relasi One-to-Many ke PembelianHD
    pembelianhd_entries = db.relationship("PembelianHD", back_populates="supplier")

#############################
#
# Berkaitan dengan Data Pembelian
#
#############################
class PembelianHD(db.Model):
    __tablename__ = 'pembelianhd'
    no_faktur = db.Column(db.String, primary_key=True)
    tanggal= db.Column(db.String, nullable=False)
    kode_supplier = db.Column(db.String, nullable=False)

    # Foreign Keys untuk relasi Many-to-One
    kode_supplier = db.Column(db.String, db.ForeignKey('supplier.kode_supplier'), nullable=False)

    kode_pengguna = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    total = db.Column(db.Numeric(precision=2), nullable=False)

    # Relasi One-to-Many ke PembelianDT
    details = db.relationship("PembelianDT", back_populates="header")

    # Relasi Many-to-One ke Supplier
    supplier = db.relationship("Supplier", back_populates="pembelianhd_entries")

    # Relasi Many-to-One ke Pelanggan
    pengguna = db.relationship("User", back_populates="pembelianhd_entries")

class PembelianDT(db.Model):
    __tablename__ = 'pembeliandt'
    no_faktur = db.Column(db.String, db.ForeignKey('pembelianhd.no_faktur'), primary_key=True)  # <-- Foreign Key
    kode_barang = db.Column(db.String, nullable=False)
    nama_barang = db.Column(db.String, nullable=False)
    harga_beli = db.Column(db.Numeric(precision=2), nullable=False)
    qty = db.Column(db.Numeric(precision=2), nullable=False)

    # Relationship ke PenjualanHD
    header = db.relationship("PembelianHD", back_populates="details")

#############################
#
# Berkaitan dengan Data Penjualan
#
#############################
class PenjualanHD(db.Model):
    __tablename__ = 'penjualanhd'
    no_faktur = db.Column(db.String, primary_key=True)
    tanggal= db.Column(db.String, nullable=False)

    # Foreign Key ke Pelanggan
    kode_pengguna = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)

    total = db.Column(db.Numeric(precision=2), nullable=False)
    ppn = db.Column(db.Numeric(precision=2), nullable=False)
    grand_total = db.Column(db.Numeric(precision=2), nullable=False)
    bayar = db.Column(db.Numeric(precision=2), nullable=False)
    kembali = db.Column(db.Numeric(precision=2), nullable=False)

    # Relationship ke PenjualanDT
    details = db.relationship("PenjualanDT", back_populates="header")
    # Relasi Many-to-One ke Pelanggan
    pengguna = db.relationship("User", back_populates="penjualanhd_entries")

class PenjualanDT(db.Model):
    __tablename__ = 'penjualandt'
    no_faktur = db.Column(db.String, db.ForeignKey('penjualanhd.no_faktur'), primary_key=True)  # <-- Foreign Key
    kode_barang = db.Column(db.String, nullable=False)
    nama_barang = db.Column(db.String, nullable=False)
    harga_jual = db.Column(db.Numeric(precision=2), nullable=False)
    qty = db.Column(db.Numeric(precision=2), nullable=False)

    # Relationship ke PenjualanHD
    header = db.relationship("PenjualanHD", back_populates="details")

#SOON TO BE DELETED
class Items(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    notes = db.Column(db.String, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, name, notes, user_id):
        self.name = name
        self.notes = notes
        self.user_id = user_id

    def __repr__(self):
        return '<id {}>'.format(self.id)
