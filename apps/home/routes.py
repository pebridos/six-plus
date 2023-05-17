# -*- encoding: utf-8 -*-
"""
Copyright (c) 2023 - present Kelompok 7
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pickle
import warnings

from apps.home import blueprint
from flask import render_template, request, jsonify
from flask_login import login_required
from jinja2 import TemplateNotFound
from sklearn.neighbors import NearestNeighbors
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from random import randint
from time import sleep
from fuzzywuzzy import fuzz
from apps import db
from apps.matakuliah.models import MataKuliah, DosenPengajar, Dosen, PembukaanKelas, MataKuliahKurikulum, PengambilanMK, Kelas, DeskripsiMataKuliah,  MinatData
from sqlalchemy import func


@blueprint.route('/index')
@login_required
def index():
    
    return render_template('home/index.html', segment='index')
    
def get_df_kelas():
    kelas_result = db.session.query(Kelas)
    kelas_result = kelas_result.all()
    df_kelas = pd.DataFrame([r.__dict__ for r in kelas_result])
    df_kelas.drop('_sa_instance_state', axis=1, inplace=True)

    return df_kelas

def get_df_deskripsi_matkul():
    desc_result = db.session.query(DeskripsiMataKuliah)
    desc_result = desc_result.all()
    df_cont = pd.DataFrame([r.__dict__ for r in desc_result])
    df_cont.drop('_sa_instance_state', axis=1, inplace=True)

    return df_cont

def read_data_course_taking(df_mhs):
    # df_mhs = pd.read_excel('pengambilan_mk.xlsx', sheet_name='Pengambilan') #Ganti jadi baca  dari db
    df_mhs['tahun'].astype(np.int64)

    # Encoding NIM
    for i in range(len(df_mhs)):
        kode_ps = df_mhs['id_mhs'].values[i][0:3]
        kode_th = df_mhs['id_mhs'].values[i][4:8]
        kode_ur = df_mhs['id_mhs'].values[i][9:len(df_mhs['id_mhs'].values[i])]

        if (int(kode_ur) < 10):
            b = kode_ps + kode_th[2:4] + '00' + kode_ur
        elif (int(kode_ur) < 100):
            b = kode_ps + kode_th[2:4] + '0' + kode_ur
        else:
            b = kode_ps + kode_th[2:4] + kode_ur

        df_mhs['id_mhs'].values[i] = int(b)

    df_kelas = get_df_kelas()

    df_kd_nama = df_kelas.copy()
    df_kd_nama = df_kd_nama[['kd_kuliah', 'nama_kuliah', 'no_ps_penyelenggara', 'sifat', 'no_kelas']].drop_duplicates()
    df_merged = pd.merge(df_mhs, df_kd_nama, on=['kd_kuliah', 'no_kelas'])
    df_merged["kd_nama_kuliah"] = df_merged["kd_kuliah"] + " " + df_merged["nama_kuliah"]
    df_merged.drop(df_merged.index[df_merged['nama_kuliah'].str.startswith('Agama dan Etika')], inplace = True)
    df_merged.drop(df_merged.index[df_merged['nama_kuliah'].str.startswith('Tugas Akhir')], inplace = True)
    df_merged.drop(df_merged.index[df_merged['nama_kuliah'].str.startswith('Kerja Praktek')], inplace = True)

    def fun(df):
        if df['sifat'] == 'W':
            val = 0.9
        else:
            if (df['no_ps_penyelenggara'] == '135' or df['no_ps_penyelenggara'] == '182') and ['sifat'] == 'P':
                val = 1
            else:
                val = 0.75
        return val

    df_merged['pengambilan'] = df_merged.apply(fun, axis=1)
    
    return df_merged

def filter_data_course_taking(df_merged, min_year = None, max_year = None,  no_ps_mhs = None, no_ps_penyelenggara = None, sifat = None):
    if max_year != None:
        df_merged = df_merged[df_merged['tahun'] <= max_year]
    if min_year != None:
        df_merged = df_merged[df_merged['tahun'] >= min_year]
    if no_ps_penyelenggara != None:
        df_merged = df_merged[df_merged['no_ps_penyelenggara'] == no_ps_penyelenggara] 
    if no_ps_mhs != None:
        df_merged = df_merged[df_merged['nim'].astype(str).str.startswith(no_ps_mhs)]
    if sifat != None:
        df_merged = df_merged[df_merged['sifat'] == sifat]
 
    df_copy = df_merged.copy()
    df = df_copy.pivot_table(index='kd_nama_kuliah',columns='id_mhs',values='pengambilan').fillna(0)
    df_pivot = df.copy()
    
    return df_merged, df, df_pivot

def recommend_course(user, df,df1):
    recommended_course = []

    for m in df[df[user] == 0].index.tolist():
        index_df = df.index.tolist().index(m)
        predicted_prob = df1.iloc[index_df, df1.columns.tolist().index(user)]
        recommended_course.append((m, predicted_prob))

    sorted_rm = sorted(recommended_course, key=lambda x:x[1], reverse=True)
    filtered_sorted_rm = [(name, prob) for name, prob in sorted_rm if prob > 0]
    
    return filtered_sorted_rm

def course_recommender(user, num_neighbors, df, df1):
    number_neighbors = num_neighbors
    
    knn = NearestNeighbors(metric='cosine', algorithm='brute')
    knn.fit(df.values)
    distances, indices = knn.kneighbors(df.values, n_neighbors=number_neighbors)
    
    user_index = df.columns.tolist().index(user)

    for m,t in list(enumerate(df.index)):
        if df.iloc[m, user_index] == 0:
            sim_course = indices[m].tolist()
            course_distances = distances[m].tolist()
            
            if m in sim_course:
                id_course = sim_course.index(m)
                sim_course.remove(m)
                course_distances.pop(id_course) 
                
            else:
                sim_course = sim_course[:num_neighbors-1]
                course_distances = course_distances[:num_neighbors-1]
           
            course_similarity = [1-x for x in course_distances]
            course_similarity_copy = course_similarity.copy()
            nominator = 0

            for s in range(0, len(course_similarity)):
                if df.iloc[sim_course[s], user_index] == 0:
                    if len(course_similarity_copy) == (number_neighbors - 1):
                        course_similarity_copy.pop(s)
                    else:
                        course_similarity_copy.pop(s-(len(course_similarity)-len(course_similarity_copy)))
                else:
                    nominator = nominator + course_similarity[s]*df.iloc[sim_course[s],user_index]
          
            if len(course_similarity_copy) > 0:
                if sum(course_similarity_copy) > 0:
                    predicted_r = nominator/sum(course_similarity_copy)    
                else:
                    predicted_r = 0
            else:
                predicted_r = 0
        
            df1.iloc[m,user_index] = predicted_r
            
    return recommend_course(user, df=df, df1=df1)

def generate_recommendation_collab(no_ps_penyelenggara, df, df1):
    course_prob = defaultdict(list)

    for nim in [x for x in list(df1.columns) if str(x).startswith(no_ps_penyelenggara)]:
        sorted_names_and_prob = course_recommender(nim, 3, df, df1)
        ranked_names = {}
        rank = 1
        prev_prob = None

        for name, prob in sorted_names_and_prob:
            if prob != prev_prob:
                rank = len(sorted_names_and_prob) - sorted_names_and_prob.index((name, prob))
                prev_prob = prob
            ranked_names[name] = [rank, prob]

        for course, prob in ranked_names.items():
            course_prob[course].append(prob)

    course_prob_list = [{'MK': course, 
                        'Total Rank':sum([val[0] for val in prob]), 
                        'Average Prob':sum([val[1] for val in prob])/len(prob)} 
                        for course, prob in course_prob.items()]

    df_final = pd.DataFrame(course_prob_list)
    df_final = df_final.sort_values(by='Total Rank', ascending=False)
    return df_final

def get_recommendation_collab(df_kelas, df_final, kd_kuliah = None, sifat = 'P'):
    df_final.drop(df_final.index[df_final['MK'].str.slice(7,11)=='2013'], inplace=True)
    df_final = df_final[df_final['MK'].str.startswith('II') | df_final['MK'].str.startswith('IF')]
    
    df_kd_nama  = df_kelas.copy()
    df_kd       = df_kd_nama[['kd_kuliah', 'nama_kuliah', 'no_ps_penyelenggara', 'sifat', 'no_kelas']].drop_duplicates()
    df_kd['MK'] = df_kd["kd_kuliah"] + " " + df_kd["nama_kuliah"]
    
    if kd_kuliah != None:
        df_final = df_final[df_final['MK'].str.startswith(kd_kuliah)]
    df_final = pd.merge(df_final, df_kd[['MK', 'sifat']], on='MK')
    if sifat != None:
        df_final_collab = df_final[df_final['sifat'] == sifat].drop_duplicates()
    else:
        df_final_collab = df_final[df_final['sifat'] == 'P'].drop_duplicates()                   
    return df_final_collab

def read_course_description(df_cont):
    # df_cont = pd.read_csv('course_description.csv')
    df_cont['kd_matakuliah'] = df_cont['kd_matakuliah'].str.replace(' ', '')
    df_cont.drop_duplicates()
    df_cont["Kode Nama MK"] = df_cont["kd_matakuliah"] + " " + df_cont["nama_matakuliah_idn"]
    df_cont = df_cont.replace(r"\n", ' ', regex=True)
    df_cont = df_cont.fillna('')
    df_cont['silabus_lengkap_en'] = df_cont['silabus_lengkap_en'].str.replace('\d+', '')
    df_cont['silabus_ringkas_en'] = df_cont['silabus_ringkas_en'].str.replace('\d+', '')
    df_cont['luaran_en'] = df_cont['luaran_en'].str.replace('\d+', '')

    df_cont = df_cont.loc[(df_cont['penyelenggara'] == '135 - Teknik Informatika / STEI') | (df_cont['penyelenggara'] == '182 - Sistem dan Teknologi Informasi / STEI')]
    df_cont = df_cont[df_cont['kd_matakuliah'].str.endswith('2019')]
    df_cont.reset_index(drop=True, inplace=True)

    return df_cont

def get_index_from_title(df_cont, title):
    return df_cont[df_cont['kd_matakuliah'] == title].index.values[0]

def matching_score(a,b):
    return fuzz.ratio(a,b)

def get_title_from_index(df_cont, index):    
    return df_cont[df_cont.index == index]['kd_matakuliah'].values[0]

def get_title_from_index_comp(df_cont, index):    
    return df_cont[df_cont.index == index]['Kode Nama MK'].values[0]

def get_prodi_from_index_comp(index):
    df_cont = get_df_deskripsi_matkul()
    
    return df_cont[df_cont.index == index]['penyelenggara'].values[0]

def find_closest_title(df_cont, title):  
    leven_scores        = list(enumerate(df_cont['kd_matakuliah'].apply(matching_score, b=title)))
    sorted_leven_scores = sorted(leven_scores, key=lambda x: x[1], reverse=True)
    closest_title       = get_title_from_index(df_cont, sorted_leven_scores[0][0])
    distance_score      = sorted_leven_scores[0][1]
    
    return closest_title, distance_score

def content_based_recommender(course, amount, sim_matrix, df_cont):
    closest_title, distance_score = find_closest_title(df_cont, course)
    
    similar_course = []
    
    if distance_score == 100:
        course_index   = get_index_from_title(df_cont, closest_title)
        course_list    = list(enumerate(sim_matrix[int(course_index)]))
        similar_course = list(filter(lambda x:x[0] != int(course_index), sorted(course_list,key=lambda x:x[1], reverse=True))) # remove the typed course itself
        
        similar_course = similar_course[:amount]

    return similar_course

def get_courses(nim, df_merged):
    student_df = df_merged[df_merged['id_mhs'] == nim]
    courses    = student_df['kd_kuliah'].tolist()

    return courses

def generate_recommendation_content(no_ps_penyelenggara, df_merged, df_cont, sim_matrix):
    list_stu = df_merged['id_mhs'].unique().tolist()
    list_rec = []
    for t in [x for x in list_stu if str(x).startswith(no_ps_penyelenggara)]:
        list_rec_stu = []
        list_exp = get_courses(t, df_merged)
        for b in list_exp:
            res = content_based_recommender(b, 10, sim_matrix, df_cont)
            for s in (res):
                if get_title_from_index(df_cont, s[0]) not in list_exp:
                    found = False
                    for j, a in enumerate(list_rec_stu):
                        if a[0] == s[0]:
                            list_rec_stu[j] = (a[0], a[1]+s[1])  
                            found = True
                            break
                    if not found:
                        list_rec_stu.append(s)

        sorted_list_rec_stu = sorted(list_rec_stu, key=lambda x: x[1], reverse=True)
        length              = len(sorted_list_rec_stu)
        ranking_scores      = {}
        for i, item in enumerate(sorted_list_rec_stu):
            score = item[1]
            if score not in ranking_scores:
                ranking_scores[score] = (length - i)
            sorted_list_rec_stu[i] = (item[0], item[1], ranking_scores[score])

        for slr in (sorted_list_rec_stu):
            found = False
            for j, a in enumerate(list_rec):
                if a[0] == slr[0]:
                    list_rec[j] = (a[0], a[1]+slr[1], a[2]+slr[2])  
                    found = True
                    break
            if not found:
                list_rec.append(slr)

    sorted_list_rec = sorted(list_rec, key=lambda x: x[1], reverse=True)

    return sorted_list_rec

def get_recommendation_content(df_cont, df_final, kd_kuliah = None, sifat = 'P'):
    df_kelas                        = get_df_kelas()
    data                            = [(get_title_from_index_comp(df_cont, id), score, rank) for id, score, rank in df_final]
    df_final                        = pd.DataFrame(data, columns=['kd_nama_kuliah', 'score', 'rank'])
    df_kelas_copy                   = df_kelas.copy()
    df_kelas_copy["kd_nama_kuliah"] = df_kelas_copy["kd_kuliah"] + " " + df_kelas_copy["nama_kuliah"]
    df_kelas_copy                   = df_kelas_copy[['kd_nama_kuliah', 'sifat']].drop_duplicates()
    df_final_content                = pd.merge(df_final, df_kelas_copy, on=['kd_nama_kuliah'])
    df_final_content                = df_final_content[df_final_content['sifat'] == 'P']
    
    if kd_kuliah != None:
        df_final_content = df_final_content[df_final_content['MK'].str.startswith(kd_kuliah)]
    if sifat != None:
        df_final_content = df_final_content[df_final_content['sifat'] == sifat].drop_duplicates()
    else:
        df_final_content = df_final_content[df_final_content['sifat'] == 'P'].drop_duplicates() 
    
    return df_final_content

def sim_matrix(df):
    tfidf_vector = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf_vector.fit_transform(df['silabus_lengkap_en'])
    sim_matrix = linear_kernel(tfidf_matrix,tfidf_matrix)

    return sim_matrix

def get_recommendation_hybrid(df_collab, df_content, df_merged, sifat = 'P', no_ps_penyelenggara = None):
    
    df_final_merge                 = pd.merge(df_collab, df_content, left_on='MK', right_on='kd_nama_kuliah', how='right')[['kd_nama_kuliah', 'rank', 'Total Rank']]
    df_final_merge.columns         = ['MK', 'Rank Content', 'Rank Collab']
    df_final_merge['Rank Content'] = df_final_merge['Rank Content'].apply(lambda x: (x - df_final_merge['Rank Content'].min()) / (df_final_merge['Rank Content'].max() - df_final_merge['Rank Content'].min()))
    df_final_merge['Rank Collab']  = df_final_merge['Rank Collab'].apply(lambda x: (x - df_final_merge['Rank Collab'].min()) / (df_final_merge['Rank Collab'].max() - df_final_merge['Rank Collab'].min()))
    df_final_merge['Rank Merged']  = df_final_merge['Rank Content'] + df_final_merge['Rank Collab']
    df_final_merge['Rank Merged']  = df_final_merge['Rank Merged'].apply(lambda x: (x - df_final_merge['Rank Merged'].min()) / (df_final_merge['Rank Merged'].max() - df_final_merge['Rank Merged'].min()))
    df_final_merge['Kode MK']      = df_final_merge['MK'].str[:11]
    df_final_merge['Nama MK']      = df_final_merge['MK'].str[11:]
    df_final_merge                 = df_final_merge[['Kode MK', 'Nama MK', 'Rank Content', 'Rank Collab', 'Rank Merged']]
    df_final_merge                 = df_final_merge.sort_values(by='Rank Merged', ascending=False)
    df_final_merge.reset_index(drop=True, inplace=True)
    df_final_merge = pd.merge(df_final_merge, df_merged[['kd_kuliah', 'sifat', 'no_ps_penyelenggara']].drop_duplicates(), left_on='Kode MK', right_on='kd_kuliah')[['Kode MK', 'Nama MK', 'Rank Content', 'Rank Collab', 'Rank Merged', 'sifat', 'no_ps_penyelenggara']]
    
    if no_ps_penyelenggara != None:
        df_final_merge = df_final_merge[df_final_merge['no_ps_penyelenggara'] == no_ps_penyelenggara]
    if sifat != None:
        df_final_merge = df_final_merge[df_final_merge['sifat'] == sifat].drop_duplicates()
    else:
        df_final_merge = df_final_merge[df_final_merge['sifat'] == 'P'].drop_duplicates()
        
    return df_final_merge.fillna(0)

def generate_data_minat():
    result = db.session.query(PengambilanMK)
    result = result.all()
    df_mhs = pd.DataFrame([r.__dict__ for r in result])
    df_mhs.drop('_sa_instance_state', axis=1, inplace=True)

    # read the data from the Pengambilan table into a pandas DataFrame
    df_mhs['tahun'] = df_mhs['tahun'].astype(int)
    df_kelas    = get_df_kelas()

    df_course_taking    = read_data_course_taking(df_mhs=df_mhs)
    df_merged, df,df1   = filter_data_course_taking(df_course_taking, min_year = None, max_year = None,  no_ps_mhs = None, no_ps_penyelenggara = None, sifat = None)

    df_sti_collab = get_recommendation_collab(df_kelas, generate_recommendation_collab('182', df, df1))
    df_if_collab  = get_recommendation_collab(df_kelas, generate_recommendation_collab('135', df, df1))

    #Function for Content Based
    df_cont = get_df_deskripsi_matkul()
    df_cont = read_course_description(df_cont)
    # return df_merged.to_dict('dict')

    df_sim_matrix = sim_matrix(df_cont)

    df_sti_content = get_recommendation_content(df_cont, generate_recommendation_content('182', df_merged, df_cont, df_sim_matrix))
    df_if_content = get_recommendation_content(df_cont, generate_recommendation_content('135', df_merged, df_cont, df_sim_matrix))

    # return df_sti_content.to_dict('dict')
    #Hybrid recommender
    df_sti_hybrid = get_recommendation_hybrid(df_content=df_sti_content, df_collab=df_sti_collab, df_merged=df_merged)
    df_if_hybrid  = get_recommendation_hybrid(df_content=df_if_content, df_collab=df_if_collab, df_merged=df_merged)

    for i, mk in enumerate(df_if_hybrid['Kode MK']):
        course = MinatData(
            kd_matakuliah       = df_if_hybrid['Kode MK'][i],
            nama_matakuliah     = df_if_hybrid['Nama MK'][i],
            rank_collab         = df_if_hybrid['Rank Collab'][i],
            rank_content        = df_if_hybrid['Rank Content'][i],
            rank_merged         = df_if_hybrid['Rank Merged'][i],
            no_ps_penyelenggara = df_if_hybrid['no_ps_penyelenggara'][i],
            sifat               = df_if_hybrid['sifat'][i],
            generate_from_ps    = '135'
        )
        db.session.add(course)
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error committing data to the database: {e}")
        # Add any additional error handling or logging as needed
    finally:
        db.session.close()
    
    return df_if_hybrid.to_dict('dict')

@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
