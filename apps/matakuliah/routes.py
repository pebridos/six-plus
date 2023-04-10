# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for
from flask_login import (
    current_user,
    login_user,
    logout_user
)

from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, CreateAccountForm
from apps.authentication.models import Users
from apps.matakuliah.forms import MatakuliahForm
from apps.matakuliah.models import MataKuliah

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('matakuliah_blueprint.l'))


@blueprint.route('/matakuliah', methods=['GET', 'POST'])
def create_matakuliah():
    form = MatakuliahForm()

    if request.method == 'POST' and form.validate():
        # Create a new Matakuliah instance and save it to the database
        matakuliah = MataKuliah(
            kode_matakuliah=form.kode_matakuliah.data,
            nama_matakuliah=form.nama_matakuliah.data,
            tahun_kurikulum=form.tahun_kurikulum.data,
            sks=form.sks.data,
            no_programstudi=form.no_programstudi.data,
            nama_programstudi=form.nama_programstudi.data
        )
        db.session.add(matakuliah)
        db.session.commit()
        return redirect(url_for('matakuliah_list'))

    return render_template('create_matakuliah.html', form=form)

@blueprint.route('/matakuliah', methods=['GET'])
def matakuliah_list():
    matakuliah_list = MataKuliah.query.first()

    return render_template('tables-data.html', matakuliah_list=matakuliah_list)
