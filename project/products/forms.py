from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired

def Kadaluarsa_Validation(form, field):
    if len(field.data) != 0:
        try:
            datetime.strptime(field.data, "%Y-%m-%d")
        except:
            raise ValidationError('Tanggal Kadaluarsa Tidak Valid')

class BarangForm(FlaskForm):
    kode_barang = StringField('Kode Barang', validators=[DataRequired()])
    nama_barang = StringField('Nama Barang', validators=[DataRequired()])
    satuan = SelectField('Satuan', validators=[DataRequired()])
    kelompok = SelectField('Kelompok', validators=[DataRequired()])
    kadaluarsa = DateField('Kadaluarsa', validators=[Kadaluarsa_Validation]) #-> After request will be converted to unixtimestamp!
    harga_pokok = StringField('Harga Pokok', validators=[DataRequired()])
    harga_jual = StringField('Harga Jual', validators=[DataRequired()])
    stok = StringField('Stok', validators=[DataRequired()])
    stok_minimal = StringField('Stok Minimal', validators=[DataRequired()])
