from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, validators

class MatakuliahForm(FlaskForm):
    kode_matakuliah   = StringField('Kode Matakuliah', validators=[validators.DataRequired(), validators.Length(max=255)])
    nama_matakuliah   = StringField('Nama Matakuliah', validators=[validators.DataRequired(), validators.Length(max=255)])
    tahun_kurikulum   = IntegerField('Tahun Kurikulum', validators=[validators.DataRequired()])
    sks               = IntegerField('SKS', validators=[validators.DataRequired()])
    no_programstudi   = StringField('No. Program Studi', validators=[validators.DataRequired(), validators.Length(max=50)])
    nama_programstudi = StringField('Nama Program Studi', validators=[validators.DataRequired(), validators.Length(max=255)])
