import sys
import os
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ...models import *
from django.db.models import Q
from utils import *
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.forms.models import model_to_dict
import time


from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Create your views here.

# products View
@login_required
def index(request):
    context = {}
    context['page_title'] = "Master management"
    context['zones'] = SpZones.objects.all()
    template = 'master/masters.html'
    return render(request, template, context)

@login_required
def ajaxtcs(request):
    context = {}
    context['tcss'] = SpTcsMaster.objects.all().order_by('-id')
    template = 'master/tcs/ajax-tcs-list.html'
    return render(request, template, context)

@login_required
def addTcs(request):
    if request.method == "POST":
        response = {}
        tcs = request.POST['tcs']
        if tcs.isdigit():
            if SpTcsMaster.objects.filter(tcs_value=request.POST['tcs']).exists():
                response['flag'] = False
                response['message'] = "TCS Value already exists."
            elif SpTcsMaster.objects.filter(tcs_percentage=request.POST['tcs_persent']).exists() and request.POST['tcs_persent']!='':
                response['flag'] = False
                response['message'] = "TCS Percentage value already exists."
            else:
                tcs = SpTcsMaster()
                tcs.tcs_value = int(request.POST['tcs'])
                tcs.tcs_percentage = request.POST['tcs_persent']
                tcs.status = 1
                tcs.save()
                
                response['flag'] = True
                response['message'] = "Record has been saved successfully."
            return JsonResponse(response)
        else:
                response['flag'] = False
                response['message'] = "Please enter the only digits number."
                return JsonResponse(response)
    else:
        context = {}
        template = 'master/tcs/add-tcs.html'
        return render(request, template)

@login_required
def editTcs(request,id):
    if request.method == "POST":
        response = {}
        if request.POST['tcs'].isdigit():  
            tcs = SpTcsMaster.objects.get(id=id)
            tcs.tcs_value = int(request.POST['tcs'])
            tcs.tcs_percentage = request.POST['tcs_persent']
            tcs.save() 
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
            return JsonResponse(response)
        else:
            response['flag'] = False
            response['message'] = "Please enter the only digits number."
            return JsonResponse(response)
    else:
        context = {}
        context['tcs'] = SpTcsMaster.objects.get(id=id)
        template = 'master/tcs/edit-tcs.html'
        return render(request, template, context)





