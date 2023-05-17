# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Kelompok 7
"""

import io
import pandas as pd
import numpy as np
import apps.home.routes as minat_routes
import apps.matakuliah.routes as matakuliah_routes
import csv

from flask import flash, render_template, redirect, request, url_for, jsonify, json
from apps import db
from sqlalchemy import func
from apps.alternatif import blueprint
from apps.matakuliah.models import MataKuliah, DosenPengajar, Dosen, PembukaanKelas, MinatData, Kelas, DeskripsiMataKuliah
from apps.alternatif.models import Alternatif, DosenPengampu, MappingDosen
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from collections import defaultdict

@blueprint.route('/')
def route_default():
    return redirect(url_for('alternatif_blueprint.l'))

@blueprint.route('/alternatives', methods=['GET', 'POST'])
def alternatives_data():
    #Input form harus ada
    #Inisialisasi 

    if request.method == 'POST':
        kd_program_studi  = request.form['programStudi']
        tahun_mulai       = int(request.form['tahunKurikulum'])
        pilihan_mk        = request.form['matkulPilihan']
        jumlah_mk_pilihan = int(request.form['jumlahMatkul'])

        df_matkul_kurikulum = matakuliah_routes.get_df_matakuliah_kurikulum(kd_program_studi)
        df_matkul_kurikulum.drop(df_matkul_kurikulum.index[df_matkul_kurikulum['kd_matakuliah'].str.slice(7,11)=='2013'], inplace=True)

        matkulminat_list = db.session.query(
                MinatData.rank_merged,
                MinatData.kd_matakuliah
            ).filter(
                MinatData.generate_from_ps == kd_program_studi
            ).all()
        
        row_dict = {}
        for item in matkulminat_list:
            row_dict[item.kd_matakuliah] = item.rank_merged

        df_historis       = minat_routes.get_df_kelas()
        count_historis_if = df_historis['kd_kuliah'].value_counts().to_dict()

        result = scoring(pilihan_mk, jumlah_mk_pilihan, df_matkul_kurikulum, row_dict, count_historis_if)

        # return jsonify(result)

        df_course       = minat_routes.get_df_deskripsi_matkul()
        df              = minat_routes.read_course_description(df_course)
        sim_matrix      = minat_routes.sim_matrix(df)
        df_mappingdosen = get_df_mappingdosen()
        df_merged       = input_data_dosen_mk(get_df_dosen(), minat_routes.get_df_kelas(), tahun_mulai)

        matkulminat_list = db.session.query(
            Kelas.kd_kuliah,
            Kelas.nama_kuliah,
            Kelas.no_ps_penyelenggara,
            Kelas.nama_ps_penyelenggara,
            Kelas.sks,
            MinatData.sifat
        ).outerjoin(
            MinatData, Kelas.kd_kuliah == MinatData.kd_matakuliah
        ).filter(Kelas.kd_kuliah.in_(result)).distinct().all()
        
        # matkulminat_dict_list = [dict(zip(row.keys(), row)) for row in matkulminat_list]
        # json_str = json.dumps(matkulminat_dict_list)

        # return json_str
        data_rekomendasi = []
        for row in matkulminat_list:
            df_recommend                      = get_dosen_recommendation(df, df_mappingdosen, df_merged, row.kd_kuliah, sim_matrix)
            df_recommend['kd_matakuliah']     = row.kd_kuliah
            df_recommend['nama_matakuliah']   = row.nama_kuliah
            df_recommend['no_programstudi']   = row.no_ps_penyelenggara
            df_recommend['nama_programstudi'] = row.nama_ps_penyelenggara
            df_recommend['sks']               = row.sks

            grouped_df = df_recommend.groupby(['kd_matakuliah', 'nama_matakuliah', 'no_programstudi', 'nama_programstudi', 'sks']).agg({
                'id': lambda x: x.tolist(),
                'id_dosen': lambda x: x.tolist(),
                'lecturer': lambda x: x.tolist(),
                'study_group': lambda x: x.tolist()
            }).reset_index()

            # rename the columns to match the original DataFrame
            grouped_df.columns = ['kd_matakuliah', 'nama_matakuliah', 'no_programstudi', 'nama_programstudi', 'sks', 'id', 'id_dosen', 'lecturer', 'study_group']

            # convert the id and id_dosen columns to strings
            grouped_df['id'] = grouped_df['id'].apply(lambda x: ', '.join(str(i) for i in x))
            grouped_df['id_dosen'] = grouped_df['id_dosen'].apply(lambda x: ', '.join(str(i) for i in x))

            data_rekomendasi.append(grouped_df)

        return render_template('home/alternatives.html', alternatives_list=data_rekomendasi, segment='alternatives')
    elif request.method == 'GET':
        return render_template('home/alternatives.html', segment='alternatives')

    # dict_list = [df.to_dict() for df in data_rekomendasi]
    # json_string = json.dumps(dict_list)

    # return json_string
    
# def alternatives_data():
#     # if request.method == 'POST':
#     df_course       = minat_routes.get_df_deskripsi_matkul()
#     df              = minat_routes.read_course_description(df_course)
#     sim_matrix      = minat_routes.sim_matrix(df)
#     df_mappingdosen = get_df_mappingdosen()
#     df_merged       = input_data_dosen_mk(get_df_dosen(), minat_routes.get_df_kelas(), 2015)

#     matkulminat_list = db.session.query(
#         MataKuliah.kode_matakuliah,
#         MataKuliah.nama_matakuliah,
#         MataKuliah.no_programstudi,
#         MataKuliah.nama_programstudi,
#         MataKuliah.sks,
#         MinatData.sifat,
#         MataKuliah.tahun_kurikulum
#         ).outerjoin(
#         MataKuliah, MinatData.kd_matakuliah==MataKuliah.kode_matakuliah
#         ).limit(9).all()
    
#     data_rekomendasi = []
#     for row in matkulminat_list:
#         df_recommend                      = get_dosen_recommendation(df, df_mappingdosen, df_merged, row.kode_matakuliah, sim_matrix)
#         df_recommend['kd_matakuliah']     = row.kode_matakuliah
#         df_recommend['nama_matakuliah']   = row.nama_matakuliah
#         df_recommend['no_programstudi']   = row.no_programstudi
#         df_recommend['nama_programstudi'] = row.nama_programstudi
#         df_recommend['sks']               = row.sks

#         grouped_df = df_recommend.groupby(['kd_matakuliah', 'nama_matakuliah', 'no_programstudi', 'nama_programstudi', 'sks']).agg({
#             'id': lambda x: x.tolist(),
#             'id_dosen': lambda x: x.tolist(),
#             'lecturer': lambda x: x.tolist(),
#             'study_group': lambda x: x.tolist()
#         }).reset_index()

#         # rename the columns to match the original DataFrame
#         grouped_df.columns = ['kd_matakuliah', 'nama_matakuliah', 'no_programstudi', 'nama_programstudi', 'sks', 'id', 'id_dosen', 'lecturer', 'study_group']

#         # convert the id and id_dosen columns to strings
#         grouped_df['id'] = grouped_df['id'].apply(lambda x: ', '.join(str(i) for i in x))
#         grouped_df['id_dosen'] = grouped_df['id_dosen'].apply(lambda x: ', '.join(str(i) for i in x))

#         data_rekomendasi.append(grouped_df)

#     return render_template('home/alternatives.html', alternatives_list=data_rekomendasi, segment='alternatives')

# def alternatives_datas():
#     df_course       = minat_routes.get_df_deskripsi_matkul()
#     df              = minat_routes.read_course_description(df_course)
#     sim_matrix      = minat_routes.sim_matrix(df)
#     df_mappingdosen = get_df_mappingdosen()
#     df_merged       = input_data_dosen_mk(get_df_dosen(), minat_routes.get_df_kelas(), 2015)

#     df_getdosen   = get_dosen_recommendation(df, df_mappingdosen, df_merged, 'II3131-2019', sim_matrix)
#     df_countdosen = count_dosen_detail(df_mappingdosen, df_merged, 'II3131-2019')
#     df_kkdosen    = count_kk_detail(df_mappingdosen, df_merged, 'II3131-2019')

#     return df_getdosen.to_dict('dict')

def input_data_dosen_mk(df_dosen, df_kelas, start_year):
    df_kd_nama                  = df_kelas.copy()
    df_kd_nama                  = df_kd_nama[['kd_kuliah', 'nama_kuliah', 'no_ps_penyelenggara', 'sifat', 'no_kelas', 'tahun', 'semester']].drop_duplicates()
    df_merged                   = pd.merge(df_dosen, df_kd_nama, on=['kd_kuliah', 'no_kelas', 'tahun', 'semester'])
    df_merged["kd_nama_kuliah"] = df_merged["kd_kuliah"] + " " + df_merged["nama_kuliah"]
    df_merged['tahun']          = df_merged['tahun'].astype('int64')
    df_merged                   = df_merged[df_merged['tahun'] >= start_year]

    return df_merged

def get_df_dosen():
    dosen_result = db.session.query(DosenPengampu)
    dosen_result = dosen_result.all()
    df_dosen     = pd.DataFrame([r.__dict__ for r in dosen_result])
    df_dosen.drop('_sa_instance_state', axis=1, inplace=True)

    return df_dosen

def get_df_mappingdosen():
    mappingdosen_result = db.session.query(MappingDosen)
    mappingdosen_result = mappingdosen_result.all()
    df_mappingdosen     = pd.DataFrame([r.__dict__ for r in mappingdosen_result])
    df_mappingdosen.drop('_sa_instance_state', axis=1, inplace=True)

    return df_mappingdosen

def count_dosen(df_merged, kd_kuliah):
    dosen_dict = {}
    
    for idx, row in df_merged.iterrows():
        if row['kd_kuliah'] == kd_kuliah:
            dosen = row['id_dosen']
            if dosen in dosen_dict:
                dosen_dict[dosen] += 1
            else:
                dosen_dict[dosen] = 1
    
    return dosen_dict

def count_mk(df_merged, id_dosen):
    mk_dict = {}
    
    for idx, row in df_merged.iterrows():
        if row['id_dosen'] == id_dosen:
            mk = row['kd_nama_kuliah']
            if mk in mk_dict:
                mk_dict[mk] += 1
            else:
                mk_dict[mk] = 1
    sorted_list = sorted(mk_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_list

def get_dosen_recommendation(df_course, df_mappingdosen, df_merged, kd_kuliah, sim_matrix):
    res = minat_routes.content_based_recommender(kd_kuliah, 2, sim_matrix, df_course)
    
    res_mk_list = []
    res_mk_list.append(kd_kuliah)
    for i,s in res: 
        res_mk_list.append(minat_routes.get_title_from_index(df_course, i))
    
    final_dict = defaultdict(int)
    
    for i in res_mk_list:
        dict_temp = count_dosen(df_merged, i)
        for k, v in dict_temp.items():
            final_dict[k] += v
            
    sorted_list = sorted(final_dict.items(), key=lambda x: x[1], reverse=True)
    final_list = [k for k, v in sorted_list]
    
    final_list = [i for i in final_list if i in df_mappingdosen['id_dosen'].unique().tolist()]
    filtered_df = df_mappingdosen[df_mappingdosen['id_dosen'].isin(final_list)]
    sorted_df = filtered_df.set_index('id_dosen').loc[final_list].reset_index()     

    return sorted_df

def count_dosen_detail(df_mappingdosen, df_merged, kd_kuliah):
    dosen_dict = {}
    
    for idx, row in df_merged.iterrows():
        if row['kd_kuliah'] == kd_kuliah:
            dosen = row['id_dosen']
            if dosen in dosen_dict:
                dosen_dict[dosen] += 1
            else:
                dosen_dict[dosen] = 1
    
    dosen_dict_set = set(df_mappingdosen["id_dosen"])
    dosen_dict = {k: v for k, v in dosen_dict.items() if k in dosen_dict_set}
    name_dict = {row["id_dosen"]: row["lecturer"] for _, row in df_mappingdosen.iterrows()}
    new_dict = {name_dict[k]: v for k, v in dosen_dict.items()}

    new_df = pd.DataFrame({
        "lecturer": list(new_dict.keys()),
        "amount": list(new_dict.values())
    })
    return new_df

def count_kk_detail(df_mappingdosen, df_merged, kd_kuliah):
    df_temp = count_dosen_detail(df_mappingdosen, df_merged, kd_kuliah)
    df_merged = pd.merge(df_temp, df_mappingdosen, on='lecturer')[['study_group', 'amount']]
    df_group = df_merged.groupby("study_group").sum('amount').reset_index()

    return df_group

def get_df_matkul_kurikulum():
    kurikulum_list = db.session.query(
            DeskripsiMataKuliah.kd_matakuliah,
            Kelas.semester,
            Kelas.sifat,
            ).outerjoin(
            DeskripsiMataKuliah, DeskripsiMataKuliah.kd_matakuliah==Kelas.kd_kuliah
            ).limit(9).all()
    kurikulum_list = kurikulum_list.all()
    df_dkurikulum     = pd.DataFrame([r.__dict__ for r in kurikulum_list])
    df_dkurikulum.drop('_sa_instance_state', axis=1, inplace=True)

    return df_dkurikulum

def scoring(choice, limitation, mk_kurikulum, rank_minat, count_historis):
    mk = {}
    result = []
    # # Starting Point
    # sifat_kurikulum = mk_kurikulum['sifat']
    # mk_kurikulum    = mk_kurikulum['kd_matakuliah'].unique()
    # sifat_kurikulum = dict(zip(mk_kurikulum, sifat_kurikulum))

    mk_kurikulum = mk_kurikulum.drop_duplicates(subset=["kd_matakuliah", "sifat"])
    list_matkul = mk_kurikulum["kd_matakuliah"].to_list()
    sifat_kurikulum = {row["kd_matakuliah"]: row["sifat"] for row in mk_kurikulum.to_dict(orient="records")}
    for matkul in list_matkul:
        mk[matkul] = 0
        if (sifat_kurikulum[matkul] == "W"):
            mk[matkul] += 101

    if (choice == "Mata Kuliah Minat"):
        for matkul_kurikulum in mk:
            for matkul_minat in rank_minat:
                if (matkul_minat in matkul_kurikulum):
                    bobot = (rank_minat[matkul_minat]) * 100
                    mk[matkul_kurikulum] += bobot
    elif (choice == "Mata Kuliah Historis"):
        for matkul_kurikulum in mk:
            for matkul_historis in count_historis:
                if (matkul_historis in matkul_kurikulum):
                    if (sifat_kurikulum[matkul] != "W"):
                        bobot = ((count_historis[matkul_historis]) / len(matkul_historis)) * 100
                        mk[matkul_kurikulum] += bobot
    else: # Choice = Combination
        for matkul_kurikulum in mk:
            for matkul_historis in count_historis:
                for matkul_minat in rank_minat:
                    if (matkul_historis in matkul_kurikulum) and (matkul_minat in matkul_kurikulum):
                        bobot = (((count_historis[matkul_historis]) / len(matkul_historis)) * 50) + ((rank_minat[matkul_minat]) * 50)
                        mk[matkul_kurikulum] += bobot

    sorted_mk = sorted(mk.items(), key=lambda x: x[1], reverse=True)

    # Enter the MK Wajib
    for i in range (len(sorted_mk)):
        if (sorted_mk[i][1] == 101):
            result.append(sorted_mk[i][0])
    print(f"Wajib: {len(result)}")
    
    for i in range (len(result), (len(result) + limitation)):
        result.append(sorted_mk[i][0])
    print(f"Minat: {limitation}")

    return result