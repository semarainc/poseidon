from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired

class PelangganForm(FlaskForm):
    #kode_pelanggan = StringField('Kode Barang', validators=[DataRequired()])
    nama = StringField('Nama Pelanggan', validators=[DataRequired()])
    alamat = StringField('Alamat')
    telp = StringField('Telp')
