# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask import render_template, redirect, request, url_for

from apps import db
from sqlalchemy import func
from apps.matakuliah import blueprint
from apps.matakuliah.forms import MatakuliahForm
from apps.matakuliah.models import MataKuliah, DosenPengajar, Dosen, PembukaanKelas

@blueprint.route('/')
def route_default():
    return redirect(url_for('matakuliah_blueprint.l'))


@blueprint.route('/mata-kuliah', methods=['GET', 'POST'])
def create_matakuliah():
    form = MatakuliahForm()

    if request.method == 'POST' and form.validate():
        # Create a new Matakuliah instance and save it to the database
        matakuliah = MataKuliah(
            kode_matakuliah   = form.kode_matakuliah.data,
            nama_matakuliah   = form.nama_matakuliah.data,
            tahun_kurikulum   = form.tahun_kurikulum.data,
            sks               = form.sks.data,
            no_programstudi   = form.no_programstudi.data,
            nama_programstudi = form.nama_programstudi.data
        )
        db.session.add(matakuliah)
        db.session.commit()

        return redirect(url_for('matakuliah_list'))

    return render_template('create_matakuliah.html', form=form)

@blueprint.route('/list', methods=['GET'])
def matakuliah_list():
    # matakuliah_list = query = session.query(
    query = db.session.query(
        MataKuliah.kode_matakuliah,
        MataKuliah.nama_matakuliah,
        MataKuliah.no_programstudi,
        MataKuliah.nama_programstudi,
        MataKuliah.sks,
        PembukaanKelas.tahun_pengambilan,
        func.group_concat(Dosen.no_induk_dosen).label('nid'),
        func.group_concat(Dosen.nama_dosen).label('dosen')
    ).join(
        PembukaanKelas,
        MataKuliah.kode_matakuliah == PembukaanKelas.kode_matakuliah
    ).join(
        DosenPengajar,
        DosenPengajar.id_pembukaankelas == PembukaanKelas.id
    ).join(
        Dosen,
        DosenPengajar.id_dosen == Dosen.id
    ).group_by(
        MataKuliah.kode_matakuliah,
        MataKuliah.nama_matakuliah,
        MataKuliah.nama_programstudi,
        MataKuliah.no_programstudi,
        MataKuliah.sks,
        PembukaanKelas.tahun_pengambilan
    ).order_by(
        PembukaanKelas.tahun_pengambilan,
        MataKuliah.nama_programstudi.asc()
    ).limit(100)

    matakuliah_list = query.all()
    # Execute the query and print the results
    matkulkurikulum_list = MataKuliah.query.limit(20).all()

    return render_template('home/tables-data.html', matakuliah_list=matakuliah_list, matkulkurikulum_list=matkulkurikulum_list, segment='tables-data')

@blueprint.route('/list', methods=['GET'])
def matakuliah_kurikulum_list():
    # Execute the query and print the results
    matakuliah_list = MataKuliah.query.limit(20).all()

    return render_template('home/tables-data.html', matakuliah_list=matakuliah_list, segment='tables-data')

@blueprint.route('/list-alternatives', methods=['GET'])
def alternatives_list():
    query = db.session.query(
        MataKuliah.kode_matakuliah,
        MataKuliah.nama_matakuliah,
        MataKuliah.no_programstudi,
        MataKuliah.nama_programstudi,
        MataKuliah.sks,
        PembukaanKelas.tahun_pengambilan,
        func.group_concat(Dosen.no_induk_dosen).label('nid'),
        func.group_concat(Dosen.nama_dosen).label('dosen')
    ).join(
        PembukaanKelas,
        MataKuliah.kode_matakuliah == PembukaanKelas.kode_matakuliah
    ).join(
        DosenPengajar,
        DosenPengajar.id_pembukaankelas == PembukaanKelas.id
    ).join(
        Dosen,
        DosenPengajar.id_dosen == Dosen.id
    ).group_by(
        MataKuliah.kode_matakuliah,
        MataKuliah.nama_matakuliah,
        MataKuliah.nama_programstudi,
        MataKuliah.no_programstudi,
        MataKuliah.sks,
        PembukaanKelas.tahun_pengambilan
    ).order_by(
        PembukaanKelas.tahun_pengambilan,
        MataKuliah.nama_programstudi.asc()
    ).limit(20)

    alternatives_list = query.all()

    return render_template('home/alternatives.html', alternatives_list=alternatives_list,  segment='alternatives')
