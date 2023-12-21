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
from django.contrib.auth.hashers import make_password,check_password
from django.apps import apps
from ..models import *
from django.db.models import Q
from utils import getConfigurationResult,getModelColumnById
from datetime import datetime,date
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from ..decorators import *



# Create your views here.
#Home View
@login_required
def index(request):
    context = {}
    today   = date.today()
    current_month = today.strftime("%m")
    current_year = today.strftime("%Y")
    todayDate = today.strftime("%Y-%m-%d")
    present_day = today.strftime("%d")
    current_month = today.strftime("%m")
    year = today.strftime("%Y")
    prevMonth = datetime.now() - timedelta(28)
    prev_month = datetime.strftime(prevMonth, '%m')
    yesterday = datetime.now() - timedelta(1)
    yesterdayDate = datetime.strftime(yesterday, '%Y-%m-%d')
    previous_month = datetime.strftime(prevMonth, '%Y-%m')
    productIds=""
    unit_name=""
    sevenDayData = []
    tempSevenDayData = []
    product_class = SpProductClass.objects.filter().all().order_by('order_of')
    product_class.todayDate = todayDate
    for productClass in product_class:
        today_total = []
        yesterday_total=0
        month_total=0
        month_data = []
        prev_month_total=0
        prev_month_data = []
        
        last_week_data = []

        temp_last_week_total=0
        temp_last_week_data = []

        for i in range(7):                    
            lastSevenDays = datetime.now() - timedelta(i)
            lastSevenDays = datetime.strftime(lastSevenDays, '%Y-%m-%d')
            lastSevenDay = datetime.now() - timedelta(i)
            year = datetime.strftime(lastSevenDay, '%Y')
            month = datetime.strftime(lastSevenDay, '%m')
            day = datetime.strftime(lastSevenDay, '%d')

            free_scheme_in_ltr = getSummaryFreeSchemeInLiterKg(productClass.id, lastSevenDays)
            
            temp = {}
            temp['year'] = year
            temp['month'] = str(int(month)-1)
            temp['day'] = str(day)
            temp['date'] = str(day)+"/"+str(int(month)-1)+"/"+str(year)
            
            product_ids    = SpProducts.objects.filter(product_class_id=productClass.id).values_list('id', flat=True)
            
            lastWeek = SpOrderDetails.objects.raw('''SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id left join sp_products p on p.id = od.product_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id IN(SELECT id FROM `sp_products` WHERE product_class_id=%s) group by p.product_class_id ''',[lastSevenDays,productClass.id])
            if len(lastWeek):
                lastWeek = lastWeek[0].quantity_in_ltr
            else:
                lastWeek = 0    
            
            last_week_total=float(lastWeek)+float(free_scheme_in_ltr)
            temp['last_week_total'] = round(last_week_total,2)
            temp['product_class'] = productClass.product_class
            last_week_data.append(last_week_total)
            
            sevenDayData.append(temp)
            # last_week_data.clear()
            tmp = {}
            tmp['year'] = year
            tmp['month'] = str(int(month)-1)
            tmp['day'] = str(day)
            tmp['date'] = str(day)+"/"+str(int(month)-1)+"/"+str(year)
            planned_sale = expectedSale(int(year),int(month),productClass.id)
            if planned_sale != 0:
                tmp['temp_last_week_total'] = round(expectedSale(int(year),int(month),productClass.id)/(numberOfDays(int(year),int(month))),2)
                tmp['product_class'] = productClass.product_class
            else:
                tmp['temp_last_week_total'] = 0
                tmp['product_class'] = productClass.product_class
                        
            tempSevenDayData.append(tmp)
            temp_last_week_data.clear()
        if len(tempSevenDayData)>0:
            tempSevenDayData.reverse()
            productClass.tempSevenDayData = tempSevenDayData
        
        if len(sevenDayData)>0:
            sevenDayData.reverse()
            productClass.sevenDayData = sevenDayData
               
        product_Ids  = SpProducts.objects.raw(''' SELECT DISTINCT id as "productIds", id FROM `sp_products` WHERE product_class_id=%s''',[productClass.id])
        product_name = []
        product_name_color = []
        product_sale = []
        
        product_name_quantity = []
        
        i = 0
        for product_Id in product_Ids:
            if (product_Id.productIds is not None):
                productIds=productIds+str(product_Id.productIds)+","
                p_id=product_Id.id
                p_name = getModelColumnById(SpProducts,p_id,'product_name')

                product_name.append(p_name)
                product_name_color.append(product_Id.product_color_code)
                
                #current_day data
                temp = {}
                tempPro = []
                tempVal = []
                tempPro.append(p_name)
                
                actual_data_today=SpOrderDetails.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id=%s group by od.product_id  ''',[todayDate,p_id])
                
                if len(actual_data_today):
                    actual_data_today = actual_data_today[0].quantity_in_ltr
                else:
                    actual_data_today = 0
                    
                product_free_scheme_pouches_ltr = float(getSummaryProductFreeSchemeInLiterKg(p_id, todayDate))
                
                temp['product_name'] = p_name
                temp['quantity'] = float(actual_data_today)+float(product_free_scheme_pouches_ltr)
                temp['color'] = product_Id.product_color_code
                i = i+1
                
                product_sale.append(actual_data_today)
                if p_name == tempPro[-1]:
                    tempVal.append(actual_data_today)
                    
                today_total.append(round(temp['quantity'],2))
                    
                   
                if len(temp) !=0:
                    product_name_quantity.append(temp)
                    productClass.product_name_quantities = product_name_quantity
                
                        
                #current month data
                abc = productClass.id
                monthlyDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and od.product_id=%s ''',[current_month,p_id]))
                productClass.current_month_date = str(year)+"-"+str(month)
                if len(monthlyDataCheck) > 0:
                    monthlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and od.product_id=%s ''',[current_month,p_id])
                    
                    for data in monthlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        month_total=float(month_total)+float(x)
                        # month_data.append(month_total)
                    productClass.month_data =  round(month_total,2)
                    productClass.month_data_avg =  round(month_total/int(present_day),2)

                #previuos month data
                prev_date = None
                previuosMonthDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and year(o.order_date)=%s and od.product_id=%s ''',[current_month,int(current_year)-1,p_id]))
                productClass.prev_date = str(int(current_year)-1)+"-"+str(current_month)
                if len(previuosMonthDataCheck) > 0:
                    prevMonthlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and year(o.order_date)=%s and od.product_id=%s ''',[current_month,int(current_year)-1,p_id])
                    
                    for data in prevMonthlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        prev_month_total=float(prev_month_total)+float(x)
                        prev_month_data.append(prev_month_total)
                        productClass.prev_month_data = round(prev_month_total,2)

                profitloss = profitLoss(month_total,prev_month_total)
                productClass.monthly_profit_loss_status = profitloss[0]
                productClass.monthly_profit_loss_percentage = profitloss[1]

                #current year data
                current_year_data = []
                yearlyDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-1,year,p_id]))
                productClass.current_year = str(int(current_year) -1)+"-"+str(int(current_year))[2:4]
                productClass.current_date = today.strftime("%Y-%m")
                current_year_total=0
                if len(yearlyDataCheck) > 0:
                    yearlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-1,year,p_id])
                    for data in yearlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        current_year_total=float(current_year_total)+float(x)
                        current_year_data.append(current_year_total)
                        productClass.current_year_data = round(current_year_total,2)

                #previous year data
                prev_year_data = []
                prev_year = None
                previuosYearDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-2,int(year)-1,p_id]))
                productClass.prev_year = str(int(current_year) -2)+"-"+str(int(current_year)-1)[2:4]
                prev_year_total=0
                if len(previuosYearDataCheck) > 0:
                    prevYearlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-2,int(year)-1,p_id])
                    for data in prevYearlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        prev_year_total=float(prev_year_total)+float(x)
                        prev_year_data.append(prev_year_total)
                    if len(prev_year_data) > 0:
                        productClass.prev_year_data = round(prev_year_total,2)
                
                if len(current_year_data) >0 or len(prev_year_data) > 0:
                    profitloss = profitLoss(float(current_year_total),float(prev_year_total))
                    productClass.yearly_profit_loss_status = profitloss[0]
                    productClass.yearly_profit_loss_percentage = profitloss[1]
        
        #yesterday data
        today_total   = sum(today_total)
        productClass.today_total = round(today_total, 2)
        actual_data_yesterday=SpOrderDetails.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id left join sp_products p on p.id = od.product_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id IN(SELECT id FROM `sp_products` WHERE product_class_id=%s) group by p.product_class_id  ''',[yesterdayDate,productClass.id])
                
        if len(actual_data_yesterday):
            actual_data_yesterday = actual_data_yesterday[0].quantity_in_ltr
        else:
            actual_data_yesterday = 0
        
        yesterday_total=float(actual_data_yesterday)+float(getSummaryFreeSchemeInLiterKg(productClass.id, yesterdayDate))
        productClass.yesterday_total = round(yesterday_total,2)
        profitloss = profitLossByDay(productClass.today_total,yesterday_total)
        productClass.daily_profit_loss_status = profitloss[0]
        productClass.daily_profit_loss_percentage = profitloss[1]
        productClass.daily_profit_loss_bar_percentage = profitloss[2]
        
        product_array = []
        for i in range(len(product_name)):
            product_dict = {}
            
            product_dict['product_name'] = product_name[i]
            product_dict['product_color'] = product_name_color[i]
            product_array.append(product_dict)
        

        productClass.product_names = product_array
    
    order_intitate_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=1).count()
    order_forwarded_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=2).count()
    order_approved_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=3).count()
    order_delivered_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=4).count()
    total_user = SpUsers.objects.filter(user_type=1,device_id__isnull=False).exclude(role_id=0).count()
    today_attendance = SpUserAttendance.objects.raw(''' SELECT id, COUNT(DISTINCT(user_id)) as today_attendance
     FROM sp_user_attendance WHERE DATE(attendance_date_time) = CURDATE() ''' )
     
    context['order_intitate_count']     = order_intitate_count
    context['order_forwarded_count']    = order_forwarded_count
    context['order_approved_count']     = order_approved_count
    context['order_delivered_count']    = order_delivered_count
    context['total_user']               = total_user
    context['today_attendance']         = today_attendance[0].today_attendance    
    context['product_class'] = product_class

    
    template = 'profile/dashboard-monthly-sale.html'
    return render(request, template,context)

def getSummaryFreeSchemeInLiterKg(product_class_id, order_date):
    free_scheme = SpOrderSchemes.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_schemes od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and od.product_class_id=%s and DATE(od.created_at)=%s group by od.product_class_id ''',[product_class_id,order_date])
    if len(free_scheme):
        free_scheme = free_scheme[0].quantity_in_ltr
    else:
        free_scheme = 0
    return free_scheme

def getSummaryProductFreeSchemeInLiterKg(product_id, order_date):
    free_scheme = SpOrderSchemes.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_schemes od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and od.product_id=%s and DATE(od.created_at)=%s group by od.product_id ''',[product_id,order_date])
    if len(free_scheme):
        free_scheme = free_scheme[0].quantity_in_ltr
    else:
        free_scheme = 0
    return free_scheme

#Home dashboard monthly sale View
@login_required
def dashboardMonthly(request):
    context = {}
    today   = date.today()
    current_month = today.strftime("%m")
    current_year = today.strftime("%Y")
    todayDate = today.strftime("%Y-%m-%d")
    present_day = today.strftime("%d")
    current_month = today.strftime("%m")
    year = today.strftime("%Y")
    prevMonth = datetime.now() - timedelta(28)
    prev_month = datetime.strftime(prevMonth, '%m')
    yesterday = datetime.now() - timedelta(1)
    yesterdayDate = datetime.strftime(yesterday, '%Y-%m-%d')
    previous_month = datetime.strftime(prevMonth, '%Y-%m')
    productIds=""
    unit_name=""
    sevenDayData = []
    tempSevenDayData = []
    product_class = SpProductClass.objects.filter().all().order_by('-id')
    product_class.todayDate = todayDate
    for productClass in product_class:
        today_total = []
        yesterday_total=0
        month_total=0
        month_data = []
        prev_month_total=0
        prev_month_data = []
        
        last_week_data = []

        temp_last_week_total=0
        temp_last_week_data = []

        for i in range(7):                    
            lastSevenDays = datetime.now() - timedelta(i)
            lastSevenDays = datetime.strftime(lastSevenDays, '%Y-%m-%d')
            lastSevenDay = datetime.now() - timedelta(i)
            year = datetime.strftime(lastSevenDay, '%Y')
            month = datetime.strftime(lastSevenDay, '%m')
            day = datetime.strftime(lastSevenDay, '%d')

            free_scheme_in_ltr = getSummaryFreeSchemeInLiterKg(productClass.id, lastSevenDays)
            
            temp = {}
            temp['year'] = year
            temp['month'] = str(int(month)-1)
            temp['day'] = str(day)
            temp['date'] = str(day)+"/"+str(int(month)-1)+"/"+str(year)
            
            product_ids    = SpProducts.objects.filter(product_class_id=productClass.id).values_list('id', flat=True)
            
            lastWeek = SpOrderDetails.objects.raw('''SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id left join sp_products p on p.id = od.product_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id IN(SELECT id FROM `sp_products` WHERE product_class_id=%s) group by p.product_class_id ''',[lastSevenDays,productClass.id])
            if len(lastWeek):
                lastWeek = lastWeek[0].quantity_in_ltr
            else:
                lastWeek = 0    
            
            last_week_total=float(lastWeek)+float(free_scheme_in_ltr)
            temp['last_week_total'] = round(last_week_total,2)
            temp['product_class'] = productClass.product_class
            last_week_data.append(last_week_total)
            
            sevenDayData.append(temp)
            # last_week_data.clear()
            tmp = {}
            tmp['year'] = year
            tmp['month'] = str(int(month)-1)
            tmp['day'] = str(day)
            tmp['date'] = str(day)+"/"+str(int(month)-1)+"/"+str(year)
            planned_sale = expectedSale(int(year),int(month),productClass.id)
            if planned_sale != 0:
                tmp['temp_last_week_total'] = round(expectedSale(int(year),int(month),productClass.id)/(numberOfDays(int(year),int(month))),2)
                tmp['product_class'] = productClass.product_class
            else:
                tmp['temp_last_week_total'] = 0
                tmp['product_class'] = productClass.product_class
                        
            tempSevenDayData.append(tmp)
            temp_last_week_data.clear()
        if len(tempSevenDayData)>0:
            tempSevenDayData.reverse()
            productClass.tempSevenDayData = tempSevenDayData
        
        if len(sevenDayData)>0:
            sevenDayData.reverse()
            productClass.sevenDayData = sevenDayData
               
        product_Ids  = SpProducts.objects.raw(''' SELECT DISTINCT id as "productIds", id FROM `sp_products` WHERE product_class_id=%s''',[productClass.id])
        product_name = []
        product_name_color = []
        product_sale = []
        
        product_name_quantity = []
        
        i = 0
        for product_Id in product_Ids:
            if (product_Id.productIds is not None):
                productIds=productIds+str(product_Id.productIds)+","
                p_id=product_Id.id
                p_name = getModelColumnById(SpProducts,p_id,'product_name')

                product_name.append(p_name)
                product_name_color.append(product_Id.product_color_code)
                
                #current_day data
                temp = {}
                tempPro = []
                tempVal = []
                tempPro.append(p_name)
                
                actual_data_today=SpOrderDetails.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id=%s group by od.product_id  ''',[todayDate,p_id])
                
                if len(actual_data_today):
                    actual_data_today = actual_data_today[0].quantity_in_ltr
                else:
                    actual_data_today = 0
                    
                product_free_scheme_pouches_ltr = float(getSummaryProductFreeSchemeInLiterKg(p_id, todayDate))
                
                temp['product_name'] = p_name
                temp['quantity'] = float(actual_data_today)+float(product_free_scheme_pouches_ltr)
                temp['color'] = product_Id.product_color_code
                i = i+1
                
                product_sale.append(actual_data_today)
                if p_name == tempPro[-1]:
                    tempVal.append(actual_data_today)
                    
                today_total.append(round(temp['quantity'],2))
                    
                   
                if len(temp) !=0:
                    product_name_quantity.append(temp)
                    productClass.product_name_quantities = product_name_quantity
                
                        
                #current month data
                abc = productClass.id
                monthlyDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and od.product_id=%s ''',[current_month,p_id]))
                productClass.current_month_date = str(year)+"-"+str(month)
                if len(monthlyDataCheck) > 0:
                    monthlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and od.product_id=%s ''',[current_month,p_id])
                    
                    for data in monthlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        month_total=float(month_total)+float(x)
                        # month_data.append(month_total)
                    productClass.month_data =  round(month_total,2)
                    productClass.month_data_avg =  round(month_total/int(present_day),2)

                #previuos month data
                prev_date = None
                previuosMonthDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and year(o.order_date)=%s and od.product_id=%s ''',[current_month,int(current_year)-1,p_id]))
                productClass.prev_date = str(int(current_year)-1)+"-"+str(current_month)
                if len(previuosMonthDataCheck) > 0:
                    prevMonthlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and month(o.order_date)=%s and year(o.order_date)=%s and od.product_id=%s ''',[current_month,int(current_year)-1,p_id])
                    
                    for data in prevMonthlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        prev_month_total=float(prev_month_total)+float(x)
                        prev_month_data.append(prev_month_total)
                        productClass.prev_month_data = round(prev_month_total,2)

                profitloss = profitLoss(month_total,prev_month_total)
                productClass.monthly_profit_loss_status = profitloss[0]
                productClass.monthly_profit_loss_percentage = profitloss[1]

                #current year data
                current_year_data = []
                yearlyDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-1,year,p_id]))
                productClass.current_year = str(int(current_year) -1)+"-"+str(int(current_year))[2:4]
                productClass.current_date = today.strftime("%Y-%m")
                current_year_total=0
                if len(yearlyDataCheck) > 0:
                    yearlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-1,year,p_id])
                    for data in yearlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        current_year_total=float(current_year_total)+float(x)
                        current_year_data.append(current_year_total)
                        productClass.current_year_data = round(current_year_total,2)

                #previous year data
                prev_year_data = []
                prev_year = None
                previuosYearDataCheck = list(SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-2,int(year)-1,p_id]))
                productClass.prev_year = str(int(current_year) -2)+"-"+str(int(current_year)-1)[2:4]
                prev_year_total=0
                if len(previuosYearDataCheck) > 0:
                    prevYearlyData = SpOrderDetails.objects.raw(''' SELECT od.* FROM sp_order_details od left join sp_orders o on o.id = od.order_id WHERE o.order_status>=3 and (month(o.order_date)>=04 or month(o.order_date)<=03) and (year(o.order_date)>=%s and year(o.order_date)<=%s) and od.product_id=%s ''',[int(year)-2,int(year)-1,p_id])
                    for data in prevYearlyData:
                        x=float(data.product_variant_size) * float(data.quantity) * float(data.product_no_of_pouch)
                        prev_year_total=float(prev_year_total)+float(x)
                        prev_year_data.append(prev_year_total)
                    if len(prev_year_data) > 0:
                        productClass.prev_year_data = round(prev_year_total,2)
                
                if len(current_year_data) >0 or len(prev_year_data) > 0:
                    profitloss = profitLoss(float(current_year_total),float(prev_year_total))
                    productClass.yearly_profit_loss_status = profitloss[0]
                    productClass.yearly_profit_loss_percentage = profitloss[1]
        
        #yesterday data
        today_total   = sum(today_total)
        productClass.today_total = round(today_total, 2)
        actual_data_yesterday=SpOrderDetails.objects.raw(''' SELECT od.id, SUM(od.quantity_in_ltr) as quantity_in_ltr FROM sp_order_details od left join sp_orders o on o.id = od.order_id left join sp_products p on p.id = od.product_id WHERE o.order_status>=3 and date(o.order_date)=%s and od.product_id IN(SELECT id FROM `sp_products` WHERE product_class_id=%s) group by p.product_class_id  ''',[yesterdayDate,productClass.id])
                
        if len(actual_data_yesterday):
            actual_data_yesterday = actual_data_yesterday[0].quantity_in_ltr
        else:
            actual_data_yesterday = 0
        
        yesterday_total=float(actual_data_yesterday)+float(getSummaryFreeSchemeInLiterKg(productClass.id, yesterdayDate))
        productClass.yesterday_total = round(yesterday_total,2)
        profitloss = profitLossByDay(productClass.today_total,yesterday_total)
        productClass.daily_profit_loss_status = profitloss[0]
        productClass.daily_profit_loss_percentage = profitloss[1]
        productClass.daily_profit_loss_bar_percentage = profitloss[2]
        
        product_array = []
        for i in range(len(product_name)):
            product_dict = {}
            
            product_dict['product_name'] = product_name[i]
            product_dict['product_color'] = product_name_color[i]
            product_array.append(product_dict)
        

        productClass.product_names = product_array
    
    order_intitate_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=1).count()
    order_forwarded_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=2).count()
    order_approved_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=3).count()
    order_delivered_count = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"),order_status=4).count()
    total_user = SpUsers.objects.filter(user_type=1,device_id__isnull=False).exclude(role_id=0).count()
    today_attendance = SpUserAttendance.objects.raw(''' SELECT id, COUNT(DISTINCT(user_id)) as today_attendance
     FROM sp_user_attendance WHERE DATE(attendance_date_time) = CURDATE() ''' )
     
    context['order_intitate_count']     = order_intitate_count
    context['order_forwarded_count']    = order_forwarded_count
    context['order_approved_count']     = order_approved_count
    context['order_delivered_count']    = order_delivered_count
    context['total_user']               = total_user
    context['today_attendance']         = today_attendance[0].today_attendance    
    context['product_class'] = product_class

    
    template = 'profile/dashboard-monthly-sale.html'
    return render(request, template,context)
    
    
def profitLoss(today_total,yesterday_total):
    if today_total == 0 and yesterday_total == 0 :
        profit_loss_status= 0
        profit = today_total - yesterday_total
        profit = 0
        profit_loss = profit
        profit_loss_bar_percentage = 0
    elif yesterday_total == 0 and today_total !=0:
        profit_loss_status= 1
        profit = today_total - yesterday_total
        profit = 100
        profit_loss = profit
        profit_loss_bar_percentage = 100 
    elif today_total == 0 and yesterday_total != 0:
        profit_loss_status = 0
        loss = yesterday_total - today_total
        loss = 100
        profit_loss = loss
        profit_loss_bar_percentage = 100 - loss
    elif (float(yesterday_total) <= float(today_total)):
        profit_loss_status = 1
        profit = today_total - yesterday_total
        if profit != 0:
            profit = (profit/yesterday_total)*100
            profit_loss = profit
            profit_loss_bar_percentage = 100 - profit
        else:
            profit_loss_status = 0
            profit_loss = 0
            profit_loss_bar_percentage = 0
    else:
        profit_loss_status = 0
        loss = today_total - yesterday_total
        if loss != 0 :
            loss = (loss/yesterday_total)*100
            profit_loss = loss
            profit_loss_bar_percentage = loss
        else:
            profit_loss = 0  #default value
            profit_loss_bar_percentage = 0
    result = [profit_loss_status,int(profit_loss),round(profit_loss_bar_percentage,2)]
    return result

def profitLossByDay(today_total,yesterday_total):
    if today_total == 0 and yesterday_total == 0 :
        profit_loss_status= 0
        profit = today_total - yesterday_total
        profit = 0
        profit_loss = profit
        profit_loss_bar_percentage = 0
    elif yesterday_total == 0 and today_total !=0:
        profit_loss_status= 1
        profit = today_total - yesterday_total
        profit = 100
        profit_loss = profit
        profit_loss_bar_percentage = 100 
    elif today_total == 0 and yesterday_total != 0:
        profit_loss_status = 0
        loss = yesterday_total - today_total
        loss = 100
        profit_loss = loss
        profit_loss_bar_percentage = 100 - loss
    elif (float(yesterday_total) <= float(today_total)):
        profit_loss_status = 1
        profit = today_total - yesterday_total
        if profit != 0:
            profit = (profit/yesterday_total)*100
            profit_loss = profit
            profit_loss_bar_percentage = 100 - profit
        else:
            profit_loss_status = 0
            profit_loss = 0
            profit_loss_bar_percentage = 0
    else:
        profit_loss_status = 0
        loss = yesterday_total - today_total
        if loss != 0 :
            loss = (loss/yesterday_total)*100
            profit_loss = loss
            profit_loss_bar_percentage = 100 - loss
        else:
            profit_loss = 0  #default value
            profit_loss_bar_percentage = 0
    result = [profit_loss_status,int(profit_loss),round(profit_loss_bar_percentage,2)]
    return result    


def numberOfDays(y, m):
    leap = 0
    if y% 400 == 0:
        leap = 1
    elif y % 100 == 0:
        leap = 0
    elif y% 4 == 0:
        leap = 1
    if m==2:
        return 28 + leap
    list = [1,3,5,7,8,10,12]
    if m in list:
        return 31
    return 30


def expectedSale(request_year,request_month,product_class_id):
    plan_id=""
    plan_detail_quantity=0
    month_list=['','Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    plan_list=SpSalesPlans.objects.all()
    if plan_list:
        for plan in plan_list:
            financial_year=str(plan.financial_year)
            f_year=financial_year.split(" - ")
            
            start_date=f_year[0]
            start=start_date.split(" ")
            start_month=int(month_list.index(start[0]))
            start_year=int(start[1])
            
            end_date=f_year[1]
            end=end_date.split(" ")
            end_month=int(month_list.index(end[0]))
            end_year=int(end[1])
            
            a = date(start_year,start_month,1)
            b = date(end_year,end_month,1)
            x = date(request_year,request_month,1)
            
            if(x>=a and x<=b):
                plan_id=plan.id
                plan_detail=(SpSalesPlanDetails.objects.filter(sales_plan_id=plan_id,month=request_month,product_class_id=product_class_id).values('quantity').first())
                try:
                    plan_detail_quantity=plan_detail['quantity']
                except:
                    plan_detail_quantity = 0
                return plan_detail_quantity
    else:
        return 0
   
@login_required
def changePassword(request):
    if request.method == "POST":
        response = {}
        if 'old_password' not in request.POST :
            response['flag'] = False
            response['message'] = "Please enter old password"
        elif 'new_password' not in request.POST :
            response['flag'] = False
            response['message'] = "Please enter new password"
        else:
            if check_password(request.POST['old_password'],request.user.password):
                SpUsers.objects.filter(id=request.user.id).update(password=make_password(request.POST['new_password']))
                response['flag'] = True
                response['message'] = "Password Changed Successfully"
            else:
                response['flag'] = False
                response['message'] = "Incorrect Old Password"

        return JsonResponse(response)
    else:
        context = {}
        template = 'profile/change-password.html'
        return render(request,template,context)