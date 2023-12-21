import sys
import os
import json
from django.core import serializers
from django.shortcuts import render, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.apps import apps
from ..models import *
from django.db.models import *
from utils import getConfigurationResult,getModelColumnById,clean_data
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from django.conf import settings
from ..decorators import *
from datetime import datetime
from calendar import monthrange
from datetime import date
import calendar
from xhtml2pdf import pisa
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.utils.html import strip_tags




@login_required
def index(request):
    page = request.GET.get('page')
    context = {}
    sales_plans = SpSalesPlans.objects.all().order_by('-id')
    context['sales_plans'] = sales_plans
    context['page_title'] = "Manage Sales Plan"
    template = 'sales-plan/index.html'
    return render(request, template, context)


@login_required
def addSalesPlan(request):
    if request.method == "POST":
        response = {}

        if 'session' not in request.POST or request.POST['session'] == "":
            response['flag']    = False
            response['message'] = "Please enter session name"
            return JsonResponse(response)

        if 'plan_interval' not in request.POST or request.POST['plan_interval'] == "":
            response['flag']    = False
            response['message'] = "Please select interval"
            return JsonResponse(response)
        
        if 'financial_year' not in request.POST or request.POST['financial_year'] == "":
            response['flag']    = False
            response['message'] = "Please select financial year"
            return JsonResponse(response)

        if SpSalesPlans.objects.filter(session=clean_data(request.POST['session']),product_class_id=request.POST['product_class_id']).exists():
            response['flag']    = False
            response['message'] = "Session already axists."
            return JsonResponse(response)

        sales_plan = SpSalesPlans()
        sales_plan.session = clean_data(request.POST['session'])
        sales_plan.financial_year_id = clean_data(request.POST['financial_year'])
        sales_plan.financial_year = getModelColumnById(SpFinancialYears,request.POST['financial_year'],'financial_year')
        sales_plan.plan_interval = request.POST['plan_interval']
        sales_plan.product_class_id = clean_data(request.POST['product_class_id'])
        sales_plan.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
        sales_plan.revised_count = 0
        sales_plan.sales_plan_status = 1
        sales_plan.created_by = request.user.id
        sales_plan.status = 1
        sales_plan.save()


        interval = request.POST['plan_interval']

        financial_months = []
        months = [4,5,6,7,8,9,10,11,12,1,2,3]
    
        if interval == "monthly":
            for month in months:
                tmp = {}
                tmp['month'] = month
                tmp['month_name'] = calendar.month_abbr[month]
                financial_months.append(tmp)
            
        elif interval == "quarterly":
            i = 1
            for month in months:
                if(i % 3 == 0):
                    tmp = {}
                    if i < 4:
                        month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[month]
                    else:
                        month_name = str(calendar.month_abbr[int(month)-2])+'-'+calendar.month_abbr[month]
                    tmp['month'] = month
                    tmp['month_name'] = month_name
                    financial_months.append(tmp)

                i = int(i) + 1
        else:
            tmp = {}
            month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[3]
            tmp['month'] = 3
            tmp['month_name'] = month_name
            financial_months.append(tmp)

        towns = SpTowns.objects.all()
        for town in towns:
            
            if interval == "monthly":
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month['month'])
                    if var_name in request.POST and request.POST[var_name] != "":
                        sales_plan_details = SpSalesPlanDetails()
                        sales_plan_details.sales_plan_id = sales_plan.id
                        sales_plan_details.town_id = town.id
                        sales_plan_details.month = financial_month['month']
                        sales_plan_details.total = 0
                        sales_plan_details.quantity = request.POST[var_name]
                        sales_plan_details.save()
                    else:
                        sales_plan_details = SpSalesPlanDetails()
                        sales_plan_details.sales_plan_id = sales_plan.id
                        sales_plan_details.town_id = town.id
                        sales_plan_details.month = financial_month['month']
                        sales_plan_details.total = 0
                        sales_plan_details.quantity = 0
                        sales_plan_details.save()

            elif interval == "quarterly":
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month['month'])
                    if var_name in request.POST and request.POST[var_name] != "":
                        for f_month in range(int(financial_month['month'])-2, int(financial_month['month'])+1):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
                    else:
                        for f_month in range(int(financial_month['month'])-2, int(financial_month['month'])+1):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = 0
                            sales_plan_details.save()
            
            else:
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month['month'])
                    if var_name in request.POST and request.POST[var_name] != "":
                        for f_month in range(4, 13):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
                        
                        for f_month in range(1, 4):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
                    else:
                        for f_month in range(4, 13):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = 0
                            sales_plan_details.save()
                        
                        for f_month in range(1, 4):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = 0
                            sales_plan_details.save()
                    
        
        response['flag']    = True
        response['message'] = "Record has been saved successfully."
        return JsonResponse(response)
        
    else:
        context = {}
        zones = SpZones.objects.all()
        for zone in zones:
            zone.towns = SpTowns.objects.filter(zone_id=zone.id)
        context['zones'] = zones
        financial_months = []
        months = [4,5,6,7,8,9,10,11,12,1,2,3]
        for month in months:
            tmp = {}
            tmp['month'] = month
            tmp['month_name'] = calendar.month_abbr[month]
            financial_months.append(tmp)

        context['financial_months'] = financial_months

        context['financial_years'] = SpFinancialYears.objects.filter(status=1)
        context['product_classes'] = SpProductClass.objects.filter(status=1).order_by('-id')
        template = 'sales-plan/add-sales-plan.html'
        return render(request, template, context)


@login_required
def editSalesPlan(request,sales_plan_id):
    if request.method == "POST":
        response = {}

        if 'session' not in request.POST or request.POST['session'] == "":
            response['flag']    = False
            response['message'] = "Please enter session name"
            return JsonResponse(response)

        if 'plan_interval' not in request.POST or request.POST['plan_interval'] == "":
            response['flag']    = False
            response['message'] = "Please select interval"
            return JsonResponse(response)
        
        if 'financial_year' not in request.POST or request.POST['financial_year'] == "":
            response['flag']    = False
            response['message'] = "Please select financial year"
            return JsonResponse(response)

        if SpSalesPlans.objects.filter(session=clean_data(request.POST['session']),product_class_id=request.POST['product_class_id']).exists():
            response['flag']    = False
            response['message'] = "Session already axists."
            return JsonResponse(response)

        sales_plan = SpSalesPlans()
        sales_plan.session = clean_data(request.POST['session'])
        sales_plan.financial_year_id = clean_data(request.POST['financial_year'])
        sales_plan.financial_year = getModelColumnById(SpFinancialYears,request.POST['financial_year'],'financial_year')
        sales_plan.plan_interval = request.POST['plan_interval']
        sales_plan.product_class_id = clean_data(request.POST['product_class_id'])
        sales_plan.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
        sales_plan.revised_count = 0
        sales_plan.sales_plan_status = 1
        sales_plan.status = 1
        sales_plan.save()


        interval = request.POST['plan_interval']

        financial_months = []
        months = [4,5,6,7,8,9,10,11,12,1,2,3]
    
        if interval == "monthly":
            for month in months:
                tmp = {}
                tmp['month'] = month
                tmp['month_name'] = calendar.month_abbr[month]
                financial_months.append(tmp)
            
        elif interval == "quarterly":
            i = 1
            for month in months:
                if(i % 3 == 0):
                    tmp = {}
                    if i < 4:
                        month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[month]
                    else:
                        month_name = str(calendar.month_abbr[int(month)-2])+'-'+calendar.month_abbr[month]
                    tmp['month'] = month
                    tmp['month_name'] = month_name
                    financial_months.append(tmp)

                i = int(i) + 1
        else:
            tmp = {}
            month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[3]
            tmp['month'] = 3
            tmp['month_name'] = month_name
            financial_months.append(tmp)

        

        towns = SpTowns.objects.all()
        for town in towns:
            if interval == "monthly":
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month)
                    if var_name in request.POST and request.POST[var_name] != "":
                        sales_plan_details = SpSalesPlanDetails()
                        sales_plan_details.sales_plan_id = sales_plan.id
                        sales_plan_details.town_id = town.id
                        sales_plan_details.month = financial_month['month']
                        sales_plan_details.total = 0
                        sales_plan_details.quantity = request.POST[var_name]
                        sales_plan_details.save()

            elif interval == "quarterly":
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month)
                    if var_name in request.POST and request.POST[var_name] != "":
                        for f_month in range(int(financial_month['month'])-1, financial_month['month']):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
            
            else:
                for financial_month in financial_months:
                    var_name = "quantity_"+str(town.id)+'_'+str(financial_month)
                    if var_name in request.POST and request.POST[var_name] != "":
                        for f_month in range(4, 12):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
                        
                        for f_month in range(1, 3):
                            sales_plan_details = SpSalesPlanDetails()
                            sales_plan_details.sales_plan_id = sales_plan.id
                            sales_plan_details.town_id = town.id
                            sales_plan_details.month = f_month
                            sales_plan_details.total = 0
                            sales_plan_details.quantity = request.POST[var_name]
                            sales_plan_details.save()
        
        response['flag']    = True
        response['message'] = "Record has been saved successfully."
        return JsonResponse(response)
        
    else:
        if SpSalesPlans.objects.filter(id=sales_plan_id).exists():
            context = {}
            sales_plan = SpSalesPlans.objects.get(id=sales_plan_id)
            sales_plan_details = SpSalesPlanDetails.objects.filter(id=sales_plan_id)
            context['sales_plan'] = sales_plan
            context['sales_plan_details'] = sales_plan_details

            current_date = date.today() 
            context['current_month'] = current_month = current_date.month

            interval = sales_plan.plan_interval
            months = [4,5,6,7,8,9,10,11,12,1,2,3]

            zones = SpZones.objects.all()
            for zone in zones:
                # calculate zone month total start here
                zone_month_planned_total = 0
                zone_month_actual_total = 0
                zone_months = []
                if interval == "monthly":
                    for month in months:
                        townIds = SpTowns.objects.filter(zone_id = zone.id).values_list('id',flat=True)
                        if townIds:
                            month_planned_quantity =  SpSalesPlanDetails.objects.filter(town_id__in=townIds).aggregate(Sum('quantity'))
                            month_planned_quantity = month_planned_quantity['quantity__sum']

                            year = getModelColumnById(SpFinancialYears,sales_plan.financial_year_id,'start_year')
                            orderIds = SpOrders.objects.filter(town_id__in=townIds,order_date__month=month,order_date__year=year).values_list('id',flat=True)
                            productIds = SpProducts.objects.filter(product_class_id=sales_plan.product_class_id).values_list('id',flat=True)
                            
                            order_items = SpOrderDetails.objects.filter(order_id__in=orderIds,product_id__in=productIds).aggregate(product_variant_size=Sum(F('product_variant_size')*F('quantity'),output_field=FloatField()))
                            if order_items['product_variant_size'] is not None:
                                month_actual_quantity = order_items['product_variant_size']
                            else:
                                month_actual_quantity = 0
                            
                            tmp = {}
                            tmp['month'] = month
                            tmp['month_planned_quantity'] = month_planned_quantity
                            tmp['month_actual_quantity'] = month_actual_quantity
                            tmp['quantity_difference'] = float(month_actual_quantity) - float(month_planned_quantity)

                            zone_months.append(tmp)
                    zone.months = zone_months

                # calculate zone month total end here


                towns = SpTowns.objects.filter(zone_id=zone.id)
                for town in towns:
                    town_month_planned_total = 0
                    town_month_actual_total = 0

                    town_financial_months = []
                    if interval == "monthly":
                        for month in months:
                            tmp = {}
                            tmp['month'] = month
                            tmp['month_name'] = calendar.month_abbr[month]
                            condition = {}
                            condition['sales_plan_id'] = sales_plan.id
                            condition['town_id'] = town.id
                            month_planned_quantity = getModelColumnByMultiFilter(SpSalesPlanDetails,condition,'quantity')
                            tmp['month_planned_quantity']  = month_planned_quantity 
                            town_month_planned_total = float(town_month_planned_total) + month_planned_quantity

                            year = getModelColumnById(SpFinancialYears,sales_plan.financial_year_id,'start_year')
                            
                            orderIds = SpOrders.objects.filter(town_id=town.id,order_date__month=month,order_date__year=year).values_list('id',flat=True)
                            productIds = SpProducts.objects.filter(product_class_id=sales_plan.product_class_id).values_list('id',flat=True)
                            
                            order_items = SpOrderDetails.objects.filter(order_id__in=orderIds,product_id__in=productIds).aggregate(product_variant_size=Sum(F('product_variant_size')*F('quantity'),output_field=FloatField()))
                            if order_items['product_variant_size'] is not None:
                                month_actual_quantity = order_items['product_variant_size']
                            else:
                                month_actual_quantity = 0

                            tmp['month_actual_quantity'] = month_actual_quantity
                            town_month_actual_total = float(town_month_actual_total) + month_actual_quantity

                            town_financial_months.append(tmp)

                    elif interval == "quarterly":
                        i = 1
                        for month in months:
                            if(i % 3 == 0):
                                tmp = {}
                                if i < 4:
                                    month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[month]
                                else:
                                    month_name = str(calendar.month_abbr[int(month)-2])+'-'+calendar.month_abbr[month]
                                tmp['month'] = month
                                tmp['month_name'] = month_name
                                town_financial_months.append(tmp)
                            i = int(i) + 1
                    else:
                        tmp = {}
                        month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[3]
                        tmp['month'] = 3
                        tmp['month_name'] = month_name
                        town_financial_months.append(tmp)

                    town.town_financial_months = town_financial_months
                    town.town_month_planned_total = town_month_planned_total
                    town.town_month_actual_total = town_month_actual_total
                    town.quantity_difference = float(town_month_actual_total) - float(town_month_planned_total)
                    
                    zone_month_planned_total = float(zone_month_planned_total) + town_month_planned_total
                    zone_month_actual_total = float(zone_month_actual_total) + town_month_actual_total

                zone.towns = towns


            financial_months = []
            if interval == "monthly":
                for month in months:
                    tmp = {}
                    tmp['month'] = month
                    tmp['month_name'] = calendar.month_abbr[month]
                    financial_months.append(tmp)
                
            elif interval == "quarterly":
                i = 1
                for month in months:
                    if(i % 3 == 0):
                        tmp = {}
                        if i < 4:
                            month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[month]
                        else:
                            month_name = str(calendar.month_abbr[int(month)-2])+'-'+calendar.month_abbr[month]
                        tmp['month'] = month
                        tmp['month_name'] = month_name
                        financial_months.append(tmp)
                    i = int(i) + 1

                else:
                    tmp = {}
                    month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[3]
                    tmp['month'] = 3
                    tmp['month_name'] = month_name
                    financial_months.append(tmp)

            
            context['financial_months'] = financial_months
            context['zones'] = zones
            context['financial_years'] = SpFinancialYears.objects.filter(status=1)
            context['product_classes'] = SpProductClass.objects.filter(status=1).order_by('-id')
            template = 'sales-plan/edit-sales-plan.html'
            return render(request, template, context)
        else:
            messages.error(request, 'invalid sales plan', extra_tags='invalid')
            return redirect('/sales-plan')


def renderIntervalAddView(request,interval):
    context = {}
    financial_months = []
    months = [4,5,6,7,8,9,10,11,12,1,2,3]
    if interval == "monthly":
        template = 'sales-plan/partials/add-monthly-view.html'
        for month in months:
            tmp = {}
            tmp['month'] = month
            tmp['month_name'] = calendar.month_abbr[month]
            financial_months.append(tmp)
        
    elif interval == "quarterly":
        template = 'sales-plan/partials/add-quarterly-view.html'
        i = 1
        for month in months:
            if(i % 3 == 0):
                tmp = {}
                if i < 4:
                    month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[month]
                else:
                    month_name = str(calendar.month_abbr[int(month)-2])+'-'+calendar.month_abbr[month]
                tmp['month'] = month
                tmp['month_name'] = month_name
                financial_months.append(tmp)

            i = int(i) + 1
    else:
        template = 'sales-plan/partials/add-yearly-view.html'
        tmp = {}
        month_name = str(calendar.month_abbr[4])+'-'+calendar.month_abbr[3]
        tmp['month'] = 3
        tmp['month_name'] = month_name
        financial_months.append(tmp)
    
    zones = SpZones.objects.all()
    for zone in zones:
        zone.towns = SpTowns.objects.filter(zone_id=zone.id)
    context['zones'] = zones
    context['financial_months'] = financial_months
    return render(request, template, context)


@login_required
def updateSalesPlanStatus(request):
    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpSalesPlans.objects.get(id=id)
            data.status = is_active
            data.save()
            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
