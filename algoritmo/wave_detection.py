# Projeto final de Programacao
# Autor: Lauro Henriko Garcia Alves de Souza.
# Matricula: 1912713
# Orientador: Waldemar Celes

# ==============================================================================

"""Detecta e Rastreia as ondas.


1. Redimensiona a imagem.
2. Identifica as bordas acima do threshold.
3. Rastreia as ondas atraves da clusterizacao.
4. Aprende o threshold automaticamente

Este e o arquivo principal no programa do PFP e e executado por um cron diariamente toda hora entre 6-16h.
"""

# ==============================================================================


import cv2
from skimage import io, color
import numpy as np
import time
from scipy.spatial import distance
import pandas as pd
import pytz
from conectadb import insere_ondas,insere_rodada,retorna_ultima_rodada,insere_controle_conexao
import os
import datetime


def rebin(a, new_shape):
    M, N = a.shape
    m, n = new_shape
    if m < M:
        return a.reshape((m, M / m, n, N / n)).mean(3).mean(1)
    else:
        return np.repeat(np.repeat(a, m / M, axis=0), n / N, axis=1)



def make_grid(x,y,step,im,dist):
    """desenha os grids na imagem"""
    if dist == 'longe':
        #desenhando linhas verticais
        #Ate o final da width
        while x < im.shape[1]:
            #desenha a linha da coluna tal ate o final do height #line_color
            cv2.line(im, (x, 0), (x, fronteira*boxlonge), color=(0,255,0), lineType=type_, thickness=thickness)
            x += step

        while y <= fronteira*boxlonge:
            # desenhando linhas horizontais
            # Ate o final da zona longe

            cv2.line(im, (0, y), (im.shape[1], y), color=(0,255,0), lineType=type_, thickness=thickness)
            y += step

    if dist == 'perto':
        while x < im.shape[1]:
            cv2.line(im, (x, fronteira*boxlonge), (x, im.shape[0]), color=(0,255,0), lineType=type_, thickness=thickness)
            x += step

        y = fronteira*boxlonge + boxperto
        while fronteira*boxlonge + boxperto <= y < im.shape[0]:
            cv2.line(im, (0, y), (im.shape[1], y), color=(0,255,0), lineType=type_, thickness=thickness)
            y += step


def show_ruler(img,step):
    """Exibe a coordenada do pixel a cada step"""
    x=0
    y=0
    while x < im.shape[1]:
        #desenha a linha da coluna tal ate o final do height
        #cv2.line(im, (x, 0), (x, fronteira*boxlonge), color=line_color, lineType=type_, thickness=thickness)
        cv2.putText(img, str(x), (x, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
        x += step

    while y < im.shape[0]:
        # desenha a linha da coluna tal ate o final do height
        # cv2.line(im, (x, 0), (x, fronteira*boxlonge), color=line_color, lineType=type_, thickness=thickness)
        cv2.putText(img, str(y), (5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))
        y += step



def desenha_ult_ondas(ondas_esquerda,ondas_direita):
    """Desenha o percurso das ultimas ondas"""
    if ondas_esquerda:

        ult_esq = ondas_esquerda[ondas_esquerda.keys()[-1]]

        if len(ult_esq[1]) > 3:
            cv2.line(frame, (int(ult_esq[1][0][0]), int(ult_esq[1][0][1])),
                     (int(ult_esq[1][-1][0]), int(ult_esq[1][-1][1])), (255, 127, 0), 3)

            print 'ult esq', ult_esq

    if ondas_direita:
        ult_dir = ondas_direita[ondas_direita.keys()[-1]]

        if len(ult_dir[1]) > 3:
            cv2.line(frame, (int(ult_dir[1][0][0]), int(ult_dir[1][0][1])),
                     (int(ult_dir[1][-1][0]), int(ult_dir[1][-1][1])), (255, 127, 0), 3)

            print 'ult_dir', ult_dir

def desenha_todas_ondas(ondas_esquerda,ondas_direita):
    """Desenha todas as ondas"""
    esquerdas_keys= ondas_esquerda.keys()
    esquerdas_keys=ondas_direita.keys()

    for key,value in ondas_esquerda.iteritems():
                if len(value[1])>=3:
                    #total_esquerdas += 1
                    #print int(value[1][0][0])
                    #print ((value[1][0][0]), (value[1][0][1])), ((value[1][-1][0]),(value[1][-1][1]))

                    cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])), (int(value[1][-1][0]),int(value[1][-1][1])), (255, 127, 0), 3)

    for key,value in ondas_direita.iteritems():
        if len(value[1])>=3:
            #total_direitas += 1
            #print int(value[1][0][0])
            #print ((value[1][0][0]), (value[1][0][1])), ((value[1][-1][0]),(value[1][-1][1]))

            cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])), (int(value[1][-1][0]),int(value[1][-1][1])), (255, 127, 0), 3)

def desenha_10ult_ondas(ondas_esquerda,ondas_direita):
    """Desenha as ultimas 10 esquerdas e direitas"""
    #esquerdas_keys= ondas_esquerda.keys()
    #direitas_keys=ondas_direita.keys()
    esquerdas_keys=[]
    direitas_keys=[]
    esquerdas_5ult={}
    diretas_5ult = {}
    esq_maior_q5=0
    dir_maior_q5 = 0
    #desenhar as 5 ultimas maiores que 3
    for key, value in sorted(ondas_esquerda.items(), key=lambda item: item[1][2], reverse=True):
        if len(value[1]) >= 3:
            esq_maior_q5=esq_maior_q5+1
            esquerdas_keys.append(key)

    if esq_maior_q5>5:
        for left in esquerdas_keys[:5]:
            esquerdas_5ult[left] = ondas_esquerda[left]

        for key, value in esquerdas_5ult.iteritems():
            cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])),(int(value[1][-1][0]), int(value[1][-1][1])), (0, 0, 0), 3)

    else:
        for key, value in ondas_esquerda.iteritems():
            if len(value[1]) >= 3:
                cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])),
                         (int(value[1][-1][0]), int(value[1][-1][1])), (255, 127, 0), 3)

    for key, value in sorted(ondas_direita.items(), key=lambda item: item[1][2], reverse=True):
        if len(value[1]) >= 3:
            dir_maior_q5 = dir_maior_q5 + 1
            direitas_keys.append(key)

    if dir_maior_q5 > 5:
        for right in direitas_keys[:5]:
            diretas_5ult[right] = ondas_direita[right]

        for key, value in diretas_5ult.iteritems():
            cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])),
                     (int(value[1][-1][0]), int(value[1][-1][1])), (0, 0, 0), 3)

    else:
        for key, value in ondas_direita.iteritems():
            if len(value[1]) >= 3:
                cv2.line(frame, (int(value[1][0][0]), int(value[1][0][1])),
                         (int(value[1][-1][0]), int(value[1][-1][1])), (255, 127, 0), 3)





def cria_directory(waves):
    """Cria diretorio year/month/day para salvar as ondas detectadas"""
    year, month, day = map(str, time.strftime("%Y %m %d").split(' '))

    directory = '/home/django/pro/prosite/static/waves/' + year + '/' + month + '/' + day+'/'+waves+'/'

    if not os.path.exists(directory):
        os.makedirs(directory)
        print 'feito'
    return directory

def ResizeWithAspectRatio(image, width=None, height=None, inter=cv2.INTER_AREA):
    """Muda o tamanho da imagem mantendo a razao altura x largura"""
    dim = None
    (h, w) = image.shape[:2]

    if width is None and height is None:
        return image
    if width is None:
        r = height / float(h)
        dim = (int(w * r), height)
    else:
        r = width / float(w)
        dim = (width, int(h * r))

    return cv2.resize(image, dim, interpolation=inter)


# ==============================================================================
"""Inicializacao de variaveis"""

directory_waves = cria_directory('waves')
directory_flat = cria_directory('flat')
directory_waves_original = cria_directory('waves_original')
year, month, day, hour,minutes = map(str, time.strftime("%Y %m %d %H %M").split(' '))
video_name = '/home/django/pro/prosite/static/waves/'+year + '/' + month + '/' + day+'/'+year+month+day+'_'+hour+minutes+'.avi'

#alterei aqui
#x = 28
#y = 16
borda = 20 #boxe com a pedra do arpoador
height = 720
width = 1280
xl = 35
yl = 20
fronteira =11
xp = 28
yp = 16
boxlonge = height/yl
boxperto = height/yp
maxx=0
minn=999999
tempodezeragemstats = 10000 #numero de frames para reavaliar a diff_energia 108000= 1 hora
tam_tabela = 2000

col_names = ['min','max', 'mean','perc_90']
stats_df = pd.DataFrame(columns = col_names)

pxstepl = (width-borda)/xl
pystepl = height/yl

pxstepp = (width-borda)/xp
pystepp = height/yp
all_diffs =[]
centroboxl= pxstepl/2
centroboxp= pxstepp/2
dist_min_agrup_perto = 100
dist_min_agrup_longe = 72
frames_passados = 60
diff_energia = 0.15
diff_energia_min = 0.05

spot ='arpoador'
line_color = (255, 255, 255)
thickness = 1
tz_Br = pytz.timezone('Brazil/East')
#definicao do passo -> pxstep = width/numero de boxes e pystep= height/numero de boxes


type_ = cv2.LINE_AA
fpsLimit = 1 # throttle limit
startTime = time.time()
out = cv2.VideoWriter(video_name,cv2.VideoWriter_fourcc('M','J','P','G'), 10, (480,270))
cap = cv2.VideoCapture('rtsp://rtsa:emailarpex@arpex2.homeip.net:554/cam/realmonitor?channel=1&subtype=0')

framecount = 0
missed_frame = 0


#estrutura para guardar as ondas
ondas_esquerda ={}
ondas_direita ={}
clusters_esq={}
clusters_dir={}
#contador de ondas
wavecountleft =0
wavecountright =0

#definicao do periodo de analise
PERIOD_OF_TIME = 50*60
startTime = time.time()
fuso =1
horario_start = 0
horario_end = 0
frames_sem_ondas=0


# ==============================================================================



while True:
    """Inicio do Algoritmo"""
    frame_com_onda = False
    avg_diff = []
    total_ondas_fechando=0
    total_ondas_abrindo=0
    total_ondas_fechando=0
    total_esquerdas=0
    total_direitas=0
    continuacao_de_esquerda=False
    continuacao_de_direita=False

    ret, frame = cap.read()
    if ret == True:  #and framecount%30==0
        copia = frame.copy()
        lina_gray = color.rgb2gray(frame)
        im = lina_gray[:, :frame.shape[1]-borda]

        # ==========================
        """chama a funcao de downsampling"""

        c = rebin(im, (20, 35))

        # ==========================


        x = 0
        y = 0

        #show_ruler(frame, pystepl)

        #make_grid(x, y, pystepl, copia,'longe')

        #make_grid(x, y, pystepp, copia,'perto')

        resize_original = ResizeWithAspectRatio(copia, width=480)

        #cv2.line(frame, (80,80), (80+dist_min_agrup_longe,80),(255, 127, 0), 3)

        #longe
        nxl = 35
        nyl = 20

        #perto
        nxp = 28
        nyp = 16

        """Inicia a convolucao nos boxes do grid buscando bordas acima do threshold e clusterizando"""

        # ==========================

        #AVALIACAO DE LONGE - GRID 1
        for j in range(fronteira):
            #para cada linha
            y = int(pystepl / 2 + j * pystepl)-8

            for i in range(nxl):
                #para cada coluna
                x = int(pxstepl / 2. + i * pxstepl)-8
                #cv2.putText(frame, str(round(c[j][i],2)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))

                #se estiver no intervalo da arrebentacao ate a areia
                if j > 6 and 0< i < (nxl-2):
                    if len(stats_df) <= tam_tabela:
                        avg_diff.append(round(abs(c[j][i] - c[j][i + 1]),4))

                    #all_diffs.append(round(abs(c[j][i] - c[j][i + 1]),4))

                    #olhando as esquerdas
                    if c[j][i] - c[j][i+1]> diff_energia:
                        """Se tiver acima do threshold"""
                        frame_com_onda = True
                        w = i * pxstepl #x
                        z = j * pystepl #y
                        #cv2.putText(frame, str((w+22.5,z+22.5)), (w, z-45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                        cv2.rectangle(frame, (w, z), (w + pxstepl, z + pxstepl), (1.0, 0, 0), -1)
                        cv2.circle(frame, (w + centroboxl, z + centroboxl), 5, (0,255,0), -1)

                        #print 'ondas_esquerda',ondas_esquerda
                        
                       
                        #Se nao houverem esquerdas registradas, vai entrar nesse if
                        if not len(ondas_esquerda):
                            #moment = time.time()
                            horario_start = time.time()
                            horario_end = time.time()

                            moment = framecount
                            #ondas_esquerda[qual onda que eh] = [(seu inicio),[(sau ultima cordenada)],quandoocorreu]
                            ondas_esquerda[wavecountleft] = [(w+centroboxl,z+centroboxl),[(w+centroboxl,z+centroboxl)],moment,horario_start,horario_end]
                            #clusters_esq[wavecountleft] = [(w+centroboxl,z+centroboxl,moment)]
                            wavecountleft += 1
                            resize = ResizeWithAspectRatio(frame, width=480)
                            cv2.imwrite(directory_waves+str(horario_start)+'.jpg',resize)
                            cv2.imwrite(directory_waves_original + str(horario_start) +'.jpg', resize_original)
                            #print wavecountleft,'new wave esquerda'

                        else:
                            for key, value in sorted(ondas_esquerda.items(), key=lambda item: item[1][2], reverse=True):
                                #if w+22.5 == 832.5 and framecount >=940:
                                 #   print ''
                                dist = distance.euclidean((w+centroboxl,z+centroboxl),value[1][-1])
                                #moment = time.time()
                                moment = framecount

                                """Decide Cluestrizacao"""

                                # Se a marcacao estiver a distancia e estiver ocorrido a pouco tempo, entra nesse if
                                if dist < dist_min_agrup_longe and moment - value[2] < frames_passados:
                                    ondas_esquerda[key][2] = moment
                                    ondas_esquerda[key][4] = time.time()
                                    if ondas_esquerda[key][1][-1] == (w+centroboxl,z+centroboxl):
                                        continuacao_de_esquerda = True
                                        #clusters_esq[wavecountleft-1].append((w+centroboxl,z+centroboxl,moment))
                                        break
                                    else:
                                        #se o y atual eh maior que o ult y adicionado a lista do trajeto
                                        if z+centroboxl >= ondas_esquerda[key][1][-1][1] or z+centroboxl + pystepl >= ondas_esquerda[key][1][-1][1]:
                                            ondas_esquerda[key][1].append((w+centroboxl,z+centroboxl))
                                            #clusters_esq[wavecountleft-1].append((w + centroboxl, z + centroboxl, moment))
                                            #print 'atualizacao onda esquerda',key
                                            continuacao_de_esquerda =True
                                            break

                            if continuacao_de_esquerda ==False:
                                horario_start = time.time()
                                horario_end = time.time()
                                ondas_esquerda[wavecountleft] = [(w + centroboxl, z + centroboxl),[(w+centroboxl,z+centroboxl)],moment,horario_start,horario_end]
                                #clusters_esq[wavecountleft] = [(w + centroboxl, z + centroboxl, moment)]
                                wavecountleft = wavecountleft +1
                                resize = ResizeWithAspectRatio(frame, width=480)
                                cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                                cv2.imwrite(directory_waves_original + str(horario_start) +'.jpg', resize_original)
                                #print wavecountleft,'new wave esquerda',(w + centroboxl, z + centroboxl)
                                #cv2.imshow('Grid', frame)
                                #time.sleep(10)


                    # olhando as direitas
                    if c[j][i] - c[j][i+1]< -diff_energia:
                        frame_com_onda = True
                        l = i * pxstepl  #x
                        k = j * pystepl #y

                        cv2.rectangle(frame, (l, k), (l + pxstepl, k + pxstepl), (1.0, 0, 0), -1)
                        cv2.circle(frame, (l + centroboxl, k + centroboxl), 5, (0,255,0), -1)

                        #print 'ondas_direita', ondas_direita

                        # Se nao houverem direitas registradas, vai entrar nesse if
                        if not len(ondas_direita):
                            horario_start = time.time()
                            horario_end = time.time()
                            moment = framecount
                            ondas_direita[wavecountright] = [(l+centroboxl,k+centroboxl),[(l+centroboxl,k+centroboxl)],moment,horario_start,horario_end]
                            #clusters_dir[wavecountright] = [(l + centroboxl, k + centroboxl, moment)]
                            wavecountright += 1
                            resize = ResizeWithAspectRatio(frame, width=480)
                            cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                            cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                            #print wavecountright,'new wave direita'

                        else:
                            for key, value in sorted(ondas_direita.items(), key=lambda item: item[1][2], reverse=True):
                            #for key,value in ondas_esquerda.copy().iteritems():
                                dist = distance.euclidean((l+centroboxl,k+centroboxl),value[1][-1])
                                #moment = time.time()
                                moment = framecount
                                if dist < dist_min_agrup_longe and moment - value[2] < frames_passados:
                                    ondas_direita[key][2] = moment
                                    ondas_direita[key][4] = time.time()
                                    if ondas_direita[key][1][-1] == (l+centroboxl,k+centroboxl):
                                        continuacao_de_direita = True
                                        #clusters_dir[wavecountright-1].append((l + centroboxl, k + centroboxl, moment))
                                        break
                                    else:
                                        if k+centroboxl >= ondas_direita[key][1][-1][1]  or k+centroboxl+ pystepl >= ondas_direita[key][1][-1][1]+pxstepl:
                                            ondas_direita[key][1].append((l+centroboxl,k+centroboxl))
                                            #clusters_dir[wavecountright-1].append((l + centroboxl, k + centroboxl, moment))
                                            #print 'atualizacao onda direita',key
                                            continuacao_de_direita =True
                                            break

                            if continuacao_de_direita ==False:
                                horario_start = time.time()
                                horario_end = time.time()
                                #ondas_esquerda[wavecountleft] = (w + 22.5, z + 22.5)
                                ondas_direita[wavecountright] = [(l + centroboxl, k + centroboxl),[(l+centroboxl,k+centroboxl)],moment,horario_start,horario_end]
                                #clusters_dir[wavecountright] = [(l + centroboxl, k + centroboxl, moment)]
                                wavecountright = wavecountright +1
                                resize = ResizeWithAspectRatio(frame, width=480)
                                cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                                cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                                #print wavecountright,'new wave direita',(l + centroboxl, k + centroboxl)
                                #cv2.imshow('Grid', frame)
                                #time.sleep(10)

        # AVALIACAO DE PERTO - GRID 2
        
        im2 = lina_gray[396:666, :frame.shape[1]-borda] # selecionando a parte inferior da imagem

        # ==========================
        """chama a funcao de downsampling na parte inferior da imagem"""

        c = rebin(im2, (6, 28))
        # ==========================


        for j in range(6):
            # para cada linha
            y = (int(pystepp / 2 + j * pystepp) - 8) + 396 # somando 396 pois eh aonde comeca o grid perto

            for i in range(nxp):
                # para cada coluna
                x = int(pxstepp / 2. + i * pxstepp) - 8
                #cv2.putText(frame, str(round(c[j][i],2)), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255))

                # se estiver no intervalo da arrebentacao ate a areia
                if i < (nxp - 2):
                    if len(stats_df) <= tam_tabela:
                        avg_diff.append(round(abs(c[j][i] - c[j][i + 1]),4))

                    #all_diffs.append(round(abs(c[j][i] - c[j][i + 1]),4))


                    # olhando as esquerdas
                    if c[j][i] - c[j][i + 1] > diff_energia:
                        """Se tiver acima do threshold"""

                        frame_com_onda = True
                        z = j * pystepp + 396 # somando 396 pois eh aonde comeca o grid perto
                        w = i * pxstepp
                        #cv2.putText(frame, str((w+22.5,z+22.5)), (w, z-45), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
                        cv2.rectangle(frame, (w, z), (w + pxstepp, z + pxstepp), (1.0, 0, 0), -1)
                        cv2.circle(frame, (w+centroboxl,z+centroboxl), 5, (0,255,0), -1)

                        #print 'ondas_esquerda', ondas_esquerda

                        #Se nao houverem esquerdas registradas, vai entrar nesse if
                        if not len(ondas_esquerda):
                            horario_start = time.time()
                            horario_end = time.time()
                            #moment = time.time()
                            moment = framecount
                            #ondas_esquerda[qual onda que eh] = [(seu inicio),[(sau ultima cordenada)],quandoocorreu]
                            ondas_esquerda[wavecountleft] = [(w+centroboxl,z+centroboxl),[(w+centroboxl,z+centroboxl)],moment,horario_start,horario_end]
                            #clusters_esq[wavecountleft] = [(w + centroboxl, z + centroboxl, moment)]
                            wavecountleft += 1
                            resize = ResizeWithAspectRatio(frame, width=480)
                            cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                            cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                            #print wavecountleft,'new wave esquerda'

                        else:
                            for key, value in sorted(ondas_esquerda.items(), key=lambda item: item[1][2], reverse=True):
                                #if w+22.5 == 832.5 and framecount >=940:
                                 #   print ''
                                dist = distance.euclidean((w+centroboxl,z+centroboxl),value[1][-1])
                                #moment = time.time()
                                moment = framecount

                                """Decide Cluestrizacao"""


                                # Se a marcacao estiver a distancia e estiver ocorrido a pouco tempo, entra nesse if
                                if dist < dist_min_agrup_perto and moment - value[2] < frames_passados:
                                    ondas_esquerda[key][2] = moment
                                    ondas_esquerda[key][4] = time.time()
                                    if ondas_esquerda[key][1][-1] == (w+centroboxl,z+centroboxl):
                                        continuacao_de_esquerda = True
                                        #clusters_esq[wavecountleft-1].append((w + centroboxl, z + centroboxl, moment))
                                        break
                                    else:
                                        #se o y atual eh maior que o ult y adicionado a lista do trajeto
                                        if z+centroboxl >= ondas_esquerda[key][1][-1][1] or z+centroboxl + pystepl >= ondas_esquerda[key][1][-1][1]:
                                            ondas_esquerda[key][1].append((w+centroboxl,z+centroboxl))
                                            #print 'atualizacao onda esquerda',key
                                            continuacao_de_esquerda =True
                                            #clusters_esq[wavecountleft-1].append((w + centroboxl, z + centroboxl, moment))
                                            break

                            if continuacao_de_esquerda ==False:
                                horario_start = time.time()
                                horario_end = time.time()
                                #ondas_esquerda[wavecountleft] = (w + 22.5, z + 22.5)
                                ondas_esquerda[wavecountleft] = [(w + centroboxl, z + centroboxl),[(w+centroboxl,z+centroboxl)],moment,horario_start,horario_end]
                                #clusters_esq[wavecountleft] = [(w + centroboxl, z + centroboxl, moment)]
                                wavecountleft = wavecountleft +1
                                resize = ResizeWithAspectRatio(frame, width=480)
                                cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                                cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                                #print wavecountleft,'new wave esquerda',(w + centroboxl, z + centroboxl)
                                #cv2.imshow('Grid', frame)
                                #time.sleep(10)


                    # olhando as direitas
                    if c[j][i] - c[j][i+1]< -diff_energia:
                        frame_com_onda = True
                        l = i * pxstepp  # x
                        k = j * pystepp + 396 #y # somando 396 pois eh aonde comeca o grid perto

                        cv2.rectangle(frame, (l, k), (l + pxstepp, k + pxstepp), (50.0, 0, 0), -1)
                        cv2.circle(frame, (l + centroboxl, k + centroboxl), 5, (0,255,0), -1)

                        #print 'ondas_direita', ondas_direita

                        # Se nao houverem direitas registradas, vai entrar nesse if
                        if not len(ondas_direita):

                            horario_start = time.time()
                            horario_end = time.time()
                            #moment = time.time()
                            moment = framecount
                            ondas_direita[wavecountright] = [(l+centroboxl,k+centroboxl),[(l+centroboxl,k+centroboxl)],moment,horario_start,horario_end]
                            #clusters_dir[wavecountright] = [(l + centroboxl, k + centroboxl, moment)]
                            wavecountright += 1
                            resize = ResizeWithAspectRatio(frame, width=480)
                            cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                            cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                            #print wavecountright,'new wave direita'

                        else:
                            for key, value in sorted(ondas_direita.items(), key=lambda item: item[1][2], reverse=True):
                            #for key,value in ondas_esquerda.copy().iteritems():
                                dist = distance.euclidean((l+centroboxl,k+centroboxl),value[1][-1])
                                #moment = time.time()
                                moment = framecount
                                if dist < dist_min_agrup_perto and moment - value[2] < frames_passados:
                                    ondas_direita[key][2] = moment
                                    ondas_direita[key][4] = time.time()
                                    if ondas_direita[key][1][-1] == (l+centroboxl,k+centroboxl):
                                        continuacao_de_direita = True
                                        #clusters_dir[wavecountright-1].append((l + centroboxl, k + centroboxl, moment))
                                        break
                                    else:
                                        if k+centroboxl >= ondas_direita[key][1][-1][1]  or k+centroboxl + pxstepp >= ondas_direita[key][1][-1][1]+pxstepl:
                                            ondas_direita[key][1].append((l+centroboxl,k+centroboxl))
                                            #print 'atualizacao onda direita',key
                                            #clusters_dir[wavecountright-1].append((l + centroboxl, k + centroboxl, moment))
                                            continuacao_de_direita =True
                                            break

                            if continuacao_de_direita ==False:
                                horario_start = time.time()
                                horario_end = time.time()
                                # ondas_esquerda[wavecountleft] = (w + 22.5, z + 22.5)
                                ondas_direita[wavecountright] = [(l + centroboxl, k + centroboxl),[(l+centroboxl,k+centroboxl)],moment,horario_start,horario_end]
                                #clusters_dir[wavecountright] = [(l + centroboxl, k + centroboxl, moment)]
                                wavecountright = wavecountright +1
                                resize = ResizeWithAspectRatio(frame, width=480)
                                cv2.imwrite(directory_waves + str(horario_start) + '.jpg', resize)
                                cv2.imwrite(directory_waves_original + str(horario_start) + '.jpg', resize_original)
                                #print wavecountright,'new wave direita',(l + centroboxl, k + centroboxl)
                                #cv2.imshow('Grid', frame)
                                #time.sleep(10)

        #salva frames sem ondas

        if frame_com_onda==False:
            frames_sem_ondas = frames_sem_ondas+1
            if frames_sem_ondas == 1:
                horario_s_onda =time.time()
                resize = ResizeWithAspectRatio(frame, width=480)
                cv2.imwrite(directory_flat + str(horario_s_onda) + '.jpg', resize)
            elif time.time() - horario_s_onda>60:
                resize = ResizeWithAspectRatio(frame, width=480)
                cv2.imwrite(directory_flat + str(horario_s_onda) + '.jpg', resize)
                horario_s_onda = time.time()




        # ==========================
        """Inicia a parte de aprendizado automatico de threshold"""


        #enqto a tabela de statisticas tiver menor que o minimo, vai populando ela
        if len(stats_df)<=tam_tabela:
            """Constroi a tabela com as diferencas entre boxes"""
            np_avg_diff = np.array(avg_diff)
            minn_diff = np_avg_diff.min()
            maxx_diff = np_avg_diff.max()
            mean_diff = np_avg_diff.mean()
            perc_90 = np.percentile(np_avg_diff, 90)
            #print minn_diff,maxx_diff,mean_diff,perc_90
            stats_df.loc[len(stats_df)] = [minn_diff, maxx_diff, mean_diff,perc_90]

        #quando a tabela de statics chegar a 100, calcula o valor da diff energia
        if len(stats_df)==tam_tabela:
            """Pega as 400 maiores diferencaa, faz a media e defini o novo threshold"""
            nlargest = stats_df.nlargest(400,'max')
            print 'nlargest',nlargest
            if nlargest['max'].mean()>diff_energia_min:
                diff_energia = nlargest['max'].mean()
                #print 'nova diff energia',diff_energia

        #zera a tabela a cada aproximadamente 10 minutos, para reiniciar o aprendizado
        if framecount % tempodezeragemstats==0:
            stats_df = stats_df.iloc[0:0]
            #print 'renovou a base stats',stats_df



        # ==========================




        #print diff_energia

        framecount = framecount + 1


        #print 'frame',framecount
        #print 'ondas esq',ondas_esquerda
        #print 'ondas dir',ondas_direita

        #print 'all_diffs',all_diffs

        #desenha_10ult_ondas(ondas_esquerda, ondas_direita)

        #desenha_todas_ondas(ondas_esquerda, ondas_direita)

        for key, value in ondas_esquerda.iteritems():
            if len(value[1]) >= 3:
                total_esquerdas += 1

        for key, value in ondas_direita.iteritems():
            if len(value[1]) >= 3:
                total_direitas += 1


        #print ondas_esquerda,ondas_direita

        #print


        total_ondas_abrindo = total_esquerdas + total_direitas

        total_ondas_fechando = (len(ondas_esquerda) - total_esquerdas) +  (len(ondas_direita) - total_direitas)

        total_ondas = total_ondas_abrindo + total_ondas_fechando


        if total_ondas_abrindo:
            percent_esq = round((float(total_esquerdas) / total_ondas_abrindo)*100,2)
            percent_dir = round((float(total_direitas) / total_ondas_abrindo)*100,2)

            percent_abrindo = round(float(total_ondas_abrindo) / (total_ondas_abrindo + total_ondas_fechando)*100,2)
            percet_fechando = round((1 - percent_abrindo/100)*100,2)

            cv2.putText(frame, 'esq', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
            cv2.putText(frame, 'dir', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

            cv2.putText(frame, str(total_esquerdas), (120,100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))
            cv2.putText(frame, str(total_direitas), (120,150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))

            cv2.putText(frame, 'Num_ond', (200, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))


            cv2.putText(frame, str(total_ondas), (380, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255))


        if framecount%30==0:
            print 'gravei video',framecount
            resize = ResizeWithAspectRatio(frame, width=480)

            out.write(resize)

        #cv2.imshow('Grid', frame)

    else:
        missed_frame = missed_frame + 1

    #print 'framecount'

    
    key = cv2.waitKey(1)
    if key == ord("p"):
        cv2.waitKey(0)

        # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        print 'cluster_dir',clusters_dir
        print 'cluster_esq',clusters_esq

        break

    #==========================
    """Checa se o algoritmo rodou o tempo determinado e se sim, insere no banco e finaliza"""

    if time.time() > startTime + PERIOD_OF_TIME:
        print 'lefts',ondas_esquerda
        print 'rights', ondas_direita
        last_run = retorna_ultima_rodada(spot)

        print last_run
        #print type(last_run)
        #print type(last_run[0][3])

        run = (last_run[0][3])+1
        insere_rodada(spot, run)
        insere_controle_conexao(spot, run,framecount,missed_frame)
        insere_ondas(ondas_esquerda, ondas_direita,run)



        # se nao tiver ondas insere um aviso de "sem ondas" no banco.
        print 'rodei ate os 50 minutos',(datetime.datetime.now())
        break

    # ==========================


    key = cv2.waitKey(1)
    if key == ord("p"):
        cv2.waitKey(0)

    if cv2.waitKey(25) & 0xFF == ord('q'):
        break


cap.release()
out.release()
# Closes all the frames
cv2.destroyAllWindows()
