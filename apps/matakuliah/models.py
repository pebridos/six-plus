# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from apps import db

class MataKuliah(db.Model):

    __tablename__ = 'matakuliah'

    id                = db.Column(db.Integer, primary_key=True)
    kode_matakuliah   = db.Column(db.String(255))
    nama_matakuliah   = db.Column(db.String(255))
    tahun_kurikulum   = db.Column(db.Integer)
    sks               = db.Column(db.Integer)
    no_programstudi   = db.Column(db.String(50))
    nama_programstudi = db.Column(db.String(255))


class DosenPengajar(db.Model):

    __tablename__ = 'dosenpengajar'

    id                = db.Column(db.Integer, primary_key=True)
    id_pembukaankelas = db.Column(db.Integer)
    id_dosen          = db.Column(db.Integer)

class Dosen(db.Model):

    __tablename__ = 'dosen'

    id             = db.Column(db.Integer, primary_key=True)
    no_induk_dosen = db.Column(db.String(50))
    nama_dosen     = db.Column(db.String(255))
    

class PembukaanKelas(db.Model):

    __tablename__ = 'pembukaankelas'

    id                = db.Column(db.Integer, primary_key=True)
    kode_matakuliah   = db.Column(db.String(255))
    no_kelas          = db.Column(db.String(255))
    tahun_pengambilan = db.Column(db.Integer)
    semester          = db.Column(db.Integer)
    sifat             = db.Column(db.String(10))

    