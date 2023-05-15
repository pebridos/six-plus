# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Kelompok 7
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

class MataKuliahKurikulum(db.Model):

    __tablename__ = 'matakuliahkurikulum'

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

class PengambilanMK(db.Model):

    __tablename__ = 'pengambilanmk'

    id        = db.Column(db.Integer, primary_key=True)
    kd_kuliah = db.Column(db.String(255))
    no_kelas  = db.Column(db.String(255))
    tahun     = db.Column(db.Integer)
    semester  = db.Column(db.Integer)
    id_mhs    = db.Column(db.String(255))


class Kelas(db.Model):
    __tablename__ = 'kelas'

    id                    = db.Column(db.Integer, primary_key=True)
    kd_kuliah             = db.Column(db.String(255))
    th_kur                = db.Column(db.String(10))
    nama_kuliah           = db.Column(db.String(255))
    sks                   = db.Column(db.String(10))
    no_kelas              = db.Column(db.String(10))
    tahun                 = db.Column(db.String(10))
    semester              = db.Column(db.String(10))
    no_ps_penyelenggara   = db.Column(db.String(10))
    nama_ps_penyelenggara = db.Column(db.String(255))
    sifat                 = db.Column(db.String(10))

class DeskripsiMataKuliah(db.Model):
    __tablename__ = 'deskripsimatakuliah'

    id                  = db.Column(db.Integer, primary_key=True)
    kd_matakuliah       = db.Column(db.String(20))
    penyelenggara       = db.Column(db.String(50))
    nama_matakuliah_idn = db.Column(db.String(100))
    nama_matakuliah_en  = db.Column(db.String(100))
    silabus_ringkas_idn = db.Column(db.String(500))
    silabus_ringkas_en  = db.Column(db.String(500))
    silabus_lengkap_idn = db.Column(db.String(1000))
    silabus_lengkap_en  = db.Column(db.String(1000))
    luaran_idn          = db.Column(db.String(500))
    luaran_en           = db.Column(db.String(500))

class MinatData(db.Model):
    __tablename__ = 'minatdata'

    id                  = db.Column(db.Integer, primary_key=True)
    kd_matakuliah       = db.Column(db.String(20))
    nama_matakuliah     = db.Column(db.String(100))
    rank_collab         = db.Column(db.Float)
    rank_content        = db.Column(db.Float)
    rank_merged         = db.Column(db.Float)
    no_ps_penyelenggara = db.Column(db.String(10))
    sifat               = db.Column(db.String(10))
    generate_from_ps    = db.Column(db.String(10))

