# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

class MataKuliah(db.Model, UserMixin):

    __tablename__ = 'matakuliah'

    id     = db.Column(db.Integer, primary_key=True)
    kode_matakuliah   = db.Column(db.String(255))
    nama_matakuliah   = db.Column(db.String(255))
    tahun_kurikulum   = db.Column(db.Integer)
    sks               = db.Column(db.Integer)
    no_programstudi   = db.Column(db.String(50))
    nama_programstudi = db.Column(db.String(255))

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def matakuliah_loader(id):
    return MataKuliah.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = MataKuliah.query.filter_by(username=username).first()
    return user if user else None
