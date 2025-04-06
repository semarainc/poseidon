from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired

class SupplierForm(FlaskForm):
    #kode_pelanggan = StringField('Kode Barang', validators=[DataRequired()])
    nama = StringField('Nama Supplier', validators=[DataRequired()])
    alamat = StringField('Alamat')
    telp = StringField('Telp')
