# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Kelompok 7
"""

from apps import db

class Alternatif(db.Model):

    __tablename__ = 'alternatif'

    id                = db.Column(db.Integer, primary_key=True)
    kode_matakuliah   = db.Column(db.String(255))
    nama_matakuliah   = db.Column(db.String(255))

class MappingDosen(db.Model):

    __tablename__ = 'mappingdosen'

    id          = db.Column(db.Integer, primary_key=True)
    id_dosen    = db.Column(db.String(255))
    lecturer    = db.Column(db.String(255))
    study_group = db.Column(db.String(255))

class DosenPengampu(db.Model):
    __tablename__ = 'dosenpengampu'

    id        = db.Column(db.Integer, primary_key=True)
    kd_kuliah = db.Column(db.String(20))
    no_kelas  = db.Column(db.String(20))
    tahun     = db.Column(db.String(20))
    semester  = db.Column(db.String(20))
    id_dosen  = db.Column(db.String(20))
