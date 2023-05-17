# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Kelompok 7
"""

import io
from flask import flash, render_template, redirect, request, url_for
import pandas as pd
import numpy as np

from apps import db
from sqlalchemy import func, distinct
from apps.matakuliah import blueprint
from apps.matakuliah.forms import MatakuliahForm
from apps.matakuliah.models import MataKuliah, DosenPengajar, Dosen, PembukaanKelas, MataKuliahKurikulum, MinatData, DeskripsiMataKuliah, Kelas
import csv


@blueprint.route('/')
def route_default():
    return redirect(url_for('matakuliah_blueprint.l'))


@blueprint.route('/mata-kuliah', methods=['GET', 'POST'])
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


@blueprint.route('/list', methods=['GET', 'POST'])
def matakuliah_list():
    #Upload matakuliah kurikulum
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # read the CSV file
            stream = io.StringIO(
                file.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)
            next(csv_input)  # Skip the first row
            for row in csv_input:
                # do something with each row, e.g., add it to the database
                # assuming the first column is the code_matakuliah and the second column is the nama_matakuliah
                rowreal = row[0].split(";")
                new_matakuliah = MataKuliahKurikulum(
                    kode_matakuliah=rowreal[0],
                    nama_matakuliah=rowreal[1],
                    no_programstudi=rowreal[2],
                    nama_programstudi=rowreal[3],
                    sks=rowreal[4],
                    tahun_kurikulum=rowreal[5]
                )
                db.session.add(new_matakuliah)
            db.session.commit()
            flash('CSV file has been uploaded successfully!', 'success')
        flash('New matakuliah has been added successfully!', 'success')
    elif request.method == 'DELETE':
        db.session.query(MataKuliahKurikulum).delete()
        db.session.commit()

    #Read matakuliah kurikulum
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
    ).limit(50)

    matakuliah_list = query.all()

    # Execute the query and print the results
    matkulkurikulum_list = MataKuliahKurikulum.query.limit(50).all()

    matkulminat_list = db.session.query(
            MataKuliah.kode_matakuliah,
            MataKuliah.nama_matakuliah,
            MataKuliah.no_programstudi,
            MataKuliah.nama_programstudi,
            MinatData.sifat,
            MataKuliah.tahun_kurikulum
        ).join(
        MataKuliah, MinatData.kd_matakuliah==MataKuliah.kode_matakuliah
        ).limit(50).all()

    return render_template(
            'home/tables-data.html',
            matakuliah_list=matakuliah_list,
            matkulkurikulum_list=matkulkurikulum_list, 
            matkulminat_list=matkulminat_list, 
            segment='tables-data'
        )

def get_df_matakuliah_kurikulum(kd_programstudi):
    matkul_result = db.session.query(
        DeskripsiMataKuliah.kd_matakuliah,
        Kelas.sifat
    ).join(
        Kelas, Kelas.kd_kuliah == DeskripsiMataKuliah.kd_matakuliah
    ).join(
        MataKuliahKurikulum, DeskripsiMataKuliah.kd_matakuliah == MataKuliahKurikulum.kode_matakuliah
    ).filter(
        MataKuliahKurikulum.no_programstudi == kd_programstudi,
    ).distinct().all()
    row_dict = [dict(r) for r in matkul_result]


    return pd.DataFrame(row_dict)