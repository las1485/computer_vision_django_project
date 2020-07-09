# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework import generics
from .models import LastestStats
from .serializers import StatsSerializer
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import render
import requests
from datetime import datetime, timedelta
import os
import time
import json
from models import Validation
import pytz
import glob
import convert_mp4
from pathlib import Path


#import datetime


# Create your views here.

tz_Br = pytz.timezone('Brazil/East')
fuso = 0
def index(request):
    return HttpResponse("Hello, world. You're at the PRO Site index.")



# Create your views here.
class StatsList(generics.ListCreateAPIView):
    queryset = LastestStats.objects.all().order_by('-id')[:1]
    serializer_class = StatsSerializer



def home(request):
    today = datetime.today()
    response = requests.get('http://165.227.87.19/prorest/?format=json')
    latest_stats = response.json()
    date_posted = (latest_stats[0]['created_at'])
    date_posted = date_posted[0:10]
    date_posted = datetime.strptime(date_posted,'%Y-%m-%d')
    year, month, day = map(str, time.strftime("%Y %m %d").split(' '))
    path2 = '/home/django/pro/prosite/static/waves/' + year + '/' + month + '/' + day + '/*.mp4'
    path1 = 'waves/' + year + '/' + month + '/' + day + '/'
    list_of_files = glob.glob(path2)  # * means all if need specific format then *.csv
    path_prefix = '/home/django/pro/prosite/static/'
    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        latest_file_name =(os.path.basename(latest_file))
        latest_file =path1+latest_file_name
    else:
        latest_file =None


    if date_posted.date() == datetime.today().date():
        return render(request, 'templates/basico.html', {
            'data': latest_stats[0]['created_at'],
            'spot': latest_stats[0]['spot'],
            'surfaveis': latest_stats[0]['surfable_waves'],
            'esquerdas': latest_stats[0]['left_waves'],
            'direitas': latest_stats[0]['right_waves'],
            'intervalo_series': latest_stats[0]['set_interval'],
            'waves_per_10min': latest_stats[0]['waves_per_10min'],
            'percurso_medio': latest_stats[0]['avg_wave_distance'],
            'duracao_media': latest_stats[0]['avg_wave_duration'],
            'diatancia_outside': latest_stats[0]['distance_outside'],
            'video':latest_file,

        })

    else:
        return render(request, 'templates/failure.html')




def gallery(request):
    year, month, day = map(str, time.strftime("%Y %m %d").split(' '))
    path='/home/django/pro/prosite/static/waves/' + year + '/' + month + '/' + day+'/'+'waves_original'+'/' # insert the path to your directory
    path2='waves/' + year + '/' + month + '/' + day+'/'+'waves_original'+'/'
    img_list =os.listdir(path)
    img_list2 = []
    for img in img_list:
        img = path2 + img
        img_list2.append(img)

    list_json = json.dumps(img_list2)
    teste = 100

    return render(request,'templates/gallery.html', {'images': img_list2,'list_json':list_json,'teste':teste})


def receive_coords(request):
    if request.method == 'POST' and request.is_ajax():
        #print request.POST
        if 'coords' in request.POST:
            today = datetime.today()
            #print 'coords in..'
            coords = request.POST['coords']
            file = request.POST['file']
            email = request.POST['email']
            print 'email',email,'file',file,'coords',coords

            dados = Validation.objects.create(
                created_at=today, spot='arpoador', email=email,
                file=file,coords=coords)
            dados.save()


            # doSomething with pieFact here...
            response ='ok'
            return JsonResponse({'response':'ok sim'})  # if everything is OK
        #nothing went well
    print 'fail'
    return JsonResponse({'response':'falhou'})