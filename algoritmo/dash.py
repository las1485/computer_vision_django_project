# Projeto final de Programacao
# Autor: Lauro Henriko Garcia Alves de Souza.
# Matricula: 1912713
# Orientador: Waldemar Celes

# ==============================================================================

"""Transforma dados de ondas em estatiscas relevantes.


1. Checa se na ultima hora teve dados e se a qualidade foi boa.
2. Calcula as estatiscas.
3. Insere no banco de dados.

Este e o arquivo que transforma os dados das ondas do wave_detection.py
 e executado por um cron diariamente toda hora entre 6:51-16:51h.
"""

# ==============================================================================




import cv2
from skimage import io, color
import matplotlib.pyplot as plt
import matplotlib.ticker as plticker
import numpy as np
import time
from scipy.spatial import distance
import pandas as pd
import datetime
import pytz
from conectadb import retorna_ondas,retorna_ultima_rodada,insere_latest_stats,retorna_controle_conexao
import ast
from datetime import datetime
import geolocalizacao
import math
import time
pd.options.mode.chained_assignment = None  # default='warn'


def haversine(coord1, coord2):
    """Calcula a distância em metros a partir de 2 coordenadas em lat-long"""

    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def convert_start_and_tracing_in_lista(ondasDF):
    """Faz conversao de unicode"""

    i = 0
    for value in (ondasDF['tracing']):
        value = str(value)
        value = ast.literal_eval(value)
        ondasDF['tracing'][i] = value
        i = i + 1

    i = 0
    for value in (ondasDF['start_pixel']):
        value = str(value)
        value = ast.literal_eval(value)
        ondasDF['start_pixel'][i] = value
        i = i + 1

    return ondasDF

def ondas_longas(ondasDF):
    """Seleciona ondas maior que a distancia min determinada"""

    long = 0
    short = 0
    for wave in ondasDF['tracing']:
        if len(wave) >= 5:
            dist = distance.euclidean(wave[0], wave[-1])
            if dist >= dist_to_surfable_wave:
                long = long + 1
            else:
                short = short + 1

    return long, short


def wave_direction(ondas):
    """Encontra as ondas para esquerda e direita
     maior que a distancia min determinada"""

    esquerdas = 0
    direitas = 0
    for idx, wave in enumerate(ondasDF['tracing']):
        if len(wave) >= 5:
            dist = distance.euclidean(wave[0], wave[-1])
            if ondasDF.loc[idx]['direction'] == 'esquerda' and dist >= dist_to_surfable_wave:
                esquerdas = esquerdas + 1
            elif ondasDF.loc[idx]['direction'] == 'direita' and dist >= dist_to_surfable_wave:
                direitas = direitas + 1

    return esquerdas, direitas

def ondas_da_serie(ondasDF):
    """Descobre as ondas que comecaram na arrebentacao"""

    arrebentacao = 2000
    ondas_da_serie=[]
    for idx,wave in enumerate(ondasDF['tracing']):
        if len(wave)>=3:
            if wave[0][1] < arrebentacao:
                arrebentacao = wave[0][1]


    for idx, wave in enumerate(ondasDF['tracing']):
        if len(wave) >= 3:
                if (arrebentacao - wave[0][1]) <=15:
                    onda = ondasDF.loc[idx]['id']
                    ondas_da_serie.append(onda)

    return ondas_da_serie


def intervalo_series(ondas_da_serie,ondasDF):
    """Calcula o intervalo em minutos entre as series"""

    horario_das_ondas=[]
    horario_das_series = []
    for idx,wave in enumerate(ondas_da_serie):
        horario_das_ondas.append(float(ondasDF.loc[ondasDF.id == wave, 'wave_time_start'].values[0]))

    horario_das_ondas.sort()
    #print 'horario_da_ondas',horario_das_ondas

    for idx,wave in enumerate(horario_das_ondas):
        if not horario_das_series:
            horario_das_series.append(wave)

        elif wave - horario_das_series[-1] > 180:
            horario_das_series.append(wave)

    horario_das_series_formatado=[]
    for horario in horario_das_series:
        horario_das_series_formatado.append(datetime.fromtimestamp(horario).strftime('%H:%M:%S'))

    print 'horario_das_series', horario_das_series_formatado

    diffs = []
    for idx,serie in enumerate(horario_das_series):
        if idx +1<len(horario_das_series):
            diff = abs(horario_das_series[idx] - horario_das_series[idx+1])
            diffs.append(diff)


    if len(diffs)>1:
        intervalo = np.array(diffs)
        intervalo = intervalo.mean()
        intervalo= round(intervalo/60,0)
    else:
        intervalo =0


    return intervalo


def ondas_por_tempo(ondasDF,hora_inicio,dia):
    """Calcula a quantidade de ondas para cada 10 minutos"""

    count10,count20,count30,count40,count50 = 0,0,0,0,0

    hora = hora_inicio[:2]
    minutos = ['10','20','30','40','50']
    horarios = [hora+':'+minutos[0],hora+':'+minutos[1],hora+':'+minutos[2],hora+':'+minutos[3],hora+':'+minutos[4]]
    horarios_unix=[]
    for horario in horarios:
        dt = dia + ' ' + horario
        dt = datetime.strptime(dt, '%Y-%m-%d %H:%M')
        dt_unix = time.mktime(dt.utctimetuple())

        horarios_unix.append(dt_unix)
    #print horarios_unix

    for idx,wave in enumerate(ondasDF['tracing']):
        if len(wave) >= 5:
            start_da_onda = float(ondasDF.loc[idx]['wave_time_start'])
            if start_da_onda < horarios_unix[0]:
                count10 = count10 +1
            elif horarios_unix[0] < start_da_onda < horarios_unix[1]:
                count20 = count20 + 1
            elif horarios_unix[1] < start_da_onda < horarios_unix[2]:
                count30 = count30 + 1
            elif horarios_unix[2] < start_da_onda < horarios_unix[3]:
                count40 = count40 + 1
            elif horarios_unix[3] < start_da_onda < horarios_unix[4]:
                count50 = count50 + 1
    print count10,count20,count30,count40,count50

    media = (count10+count20+count30+count40+count50)/5

    print media

    return media

def distancia_das_ondas(ondasDF,height):
    """Calcula a distancia media
    em metros pecorrido pelas ondas"""

    distancias=[]
    for idx, wave in enumerate(ondasDF['tracing']):
        if len(wave)>3:
            inicio_onda = wave[0]
            fim_onda = wave[-1]
            px_inicio = inicio_onda[0]
            py_inicio = height-inicio_onda[1]
            px_fim = fim_onda[0]
            py_fim = height-fim_onda[1]
            pixels_coords_ini = np.array([px_inicio, py_inicio])
            pixels_coords_fim = np.array([px_fim, py_fim])
            points_3d_plano_ini = geolocalizacao.project_points_to3d(pixels_coords_ini)
            points_3d_plano_fim = geolocalizacao.project_points_to3d(pixels_coords_fim)

            geo_coords_ini = (round(points_3d_plano_ini[1], 6), round(points_3d_plano_ini[0], 6))
            geo_coords_fim = (round(points_3d_plano_fim[1], 6), round(points_3d_plano_fim[0], 6))

            distancia = haversine(geo_coords_ini,geo_coords_fim)
            #print ondasDF.loc[idx]['wave_time_start'],ondasDF.loc[idx]['wave_time_end'],geo_coords_ini,geo_coords_fim,distancia
            distancias.append(distancia)

    distancias = np.array(distancias)
    distancia_media = distancias.mean()

    return distancia_media

def duracao_da_onda(ondasDF):
    """Calcula a duracao media das ondas segundos"""

    duracoes = []
    for idx, wave in enumerate(ondasDF['tracing']):
        if len(wave) > 10:
            duracao = abs(float(ondasDF.loc[idx]['wave_time_start'])-float(ondasDF.loc[idx]['wave_time_end']))+1 #soma 1 segundo pelo tempo de quebra inicial
            #print 'duracao',duracao
            duracoes.append(duracao)

    duracoes=np.array(duracoes)
    duracao_media = round(duracoes.mean(),0)

    return duracao_media

def distancia_arrebentacao(ondasDF,height):
    """Calcula a distancia em metros da
    areia ate a arrebentacao"""

    arrebentacao_pixel = height
    ondas_da_serie = []
    wave_max_idx = 0
    for idx, wave in enumerate(ondasDF['tracing']):
        if len(wave) >= 5:
            if wave[0][1] < arrebentacao_pixel:
                arrebentacao_pixel = wave[0][1]
                wave_max_idx =idx

    #600 para centralizar o eixo x
    arrebentacao_pixel=(600,arrebentacao_pixel)
    #print arrebentacao_pixel
    areia = (600,720)
    px_inicio = areia[0]
    py_inicio = height - areia[1]
    px_fim = arrebentacao_pixel[0]
    py_fim = height - arrebentacao_pixel[1]
    pixels_coords_ini = np.array([px_inicio, py_inicio])
    pixels_coords_fim = np.array([px_fim, py_fim])
    points_3d_plano_ini = geolocalizacao.project_points_to3d(pixels_coords_ini)
    points_3d_plano_fim = geolocalizacao.project_points_to3d(pixels_coords_fim)
    geo_coords_ini = (round(points_3d_plano_ini[1], 6), round(points_3d_plano_ini[0], 6))
    geo_coords_fim = (round(points_3d_plano_fim[1], 6), round(points_3d_plano_fim[0], 6))
    print ondasDF.loc[wave_max_idx]['wave_time_start'],geo_coords_fim
    distancia_arrebentacao_metros = haversine(geo_coords_ini, geo_coords_fim)
    print distancia_arrebentacao_metros
    return distancia_arrebentacao_metros


# ==============================================================================
"""Inicializacao de variaveis"""

#pegando a ultima hora

dist_to_surfable_wave=200

date, hour = map(str, time.strftime("%Y-%m-%d %H").split(' '))

prev_hour = int(hour)-1

if prev_hour<10:
    prev_hour = '0'+str(prev_hour)
else:
    prev_hour = str(prev_hour)



dt_query_inicio = date+' '+prev_hour+':00:00'
dt_query_fim = date+' '+hour+':00:00'

print dt_query_inicio,dt_query_fim

spot = 'arpoador'

# ==============================================================================



# pega os dados sobre qualidade da transmissao
controle,mycursor = retorna_controle_conexao(spot,dt_query_inicio,dt_query_fim)

print 'c',controle

if controle:
    #Se tiver dados da ultima hora
    framecount = int(controle[0][4])
    missed_frame = int(controle[0][5])
    run = controle[0][3]
    print 'run',run

    if framecount/(framecount+missed_frame)>=0.9:

        #Se a qualidade transmissao tiver sido boa, gera as stats


        ondas,mycursor = retorna_ondas('arpoador',dt_query_inicio,dt_query_fim,run)

        ondasDF = pd.DataFrame(ondas,columns=mycursor.column_names)
        ondasDF = convert_start_and_tracing_in_lista(ondasDF)
        print ondasDF
        long,short = ondas_longas(ondasDF)
        surfable_waves= long

        print 'surfable_waves',surfable_waves

        left_waves,right_waves = wave_direction(ondasDF)
        print 'direction',left_waves,right_waves

        #print ondas_longas['tracing']


        ondas_da_serie = ondas_da_serie(ondasDF)
        #print ondas_da_serie

        set_interval = int(intervalo_series(ondas_da_serie,ondasDF))

        print 'set_interval',set_interval

        waves_per_10min = ondas_por_tempo(ondasDF,prev_hour+':00:00',date)
        print 'waves_per_10min',waves_per_10min


        height=720 #dimensao y da imagem

        avg_wave_distance = int(distancia_das_ondas(ondasDF,height))
        print 'avg_wave_distance',avg_wave_distance
        #print 'distancia_media',distancia_media

        avg_wave_duration = int(duracao_da_onda(ondasDF))
        print 'avg_wave_duration',avg_wave_duration
        #print 'media',duracao_da_onda

        distance_outside = int(distancia_arrebentacao(ondasDF,height))
        print 'distance_outside',distance_outside



        #insere as stats no banco


        insere_latest_stats(spot,run,surfable_waves,left_waves,right_waves,set_interval,waves_per_10min,avg_wave_distance,avg_wave_duration,distance_outside)

