import sys
import os
import openpyxl
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
from utils import *
from datetime import datetime, date
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings

# Account List View
@login_required
def printAll(request):  
    today                   = date.today()
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today.strftime("%Y-%m-%d")).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today.strftime("%Y-%m-%d")).count()

    users = SpUsers.objects.filter(user_type=2, status=1).values('id', 'first_name', 'middle_name', 'last_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today.strftime("%Y-%m-%d"), user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                order_detail.hsn_code       = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                order_detail.no_of_pouches  = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            users_list['orders']    = order_details
            user_list.append(users_list)

    context = {}
    context['user_list']                    = user_list  
    context['today_date']                   = today.strftime("%d/%m/%Y")
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Accounts"

    template = 'accounts/index.html'
    return render(request, template, context)

def getFlatBulkSchemeIncentiveOrderWise(order_id, scheme_type):
    try:
        free_scheme = SpOrderSchemes.objects.filter(order_id=order_id, scheme_type=scheme_type).aggregate(Sum('incentive_amount'))['incentive_amount__sum']
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = free_scheme
    else:
        free_scheme = 0
    return free_scheme
    
def getFlatBulkSchemeIncentive(user_id, scheme_type, today):
    order_id = SpOrders.objects.get(order_date__icontains=today, user_id=user_id)
    try:
        free_scheme = SpOrderSchemes.objects.filter(order_id=order_id.id, scheme_type=scheme_type, user_id=user_id).aggregate(Sum('incentive_amount'))['incentive_amount__sum']
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = free_scheme
    else:
        free_scheme = 0
    return free_scheme

def getFreeScheme(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, free_variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = (int(getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'no_of_pouch'))*int(free_scheme.container_quantity))+int(free_scheme.pouch_quantity)  
    else:
        free_scheme = 0
    return free_scheme

def getFlatScheme(product_variant_id, order_id, user_id):
    try:
        flat_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='flat', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        flat_scheme = None
    if flat_scheme:
        flat = flat_scheme.incentive_amount
        flat_scheme = flat
    else:
        flat_scheme = 0  
    return flat_scheme
    
def getOrderFreeSchemes(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free = 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')+'-'
        if free_scheme.container_quantity>0:
            product_id             = getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'product_id')
            free += str(free_scheme.container_quantity)+' free '+getModelColumnById(SpProducts, product_id, 'container_name')+''
        if free_scheme.container_quantity>0:
            free += ' and '     
        if free_scheme.pouch_quantity>0:
            if free_scheme.pouch_quantity == 1:
                free += ' '+str(free_scheme.pouch_quantity)+' free Pouch'
            else:    
                free += ' '+str(free_scheme.pouch_quantity)+' free Pouches'
              
        free_scheme = free
    else:
        free_scheme = None  
    return free_scheme

def getFreeSchemeInLtr(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = str(float(free_scheme.quantity_in_ltr)) 
    else:
        free_scheme = 0
    return free_scheme 
    
def getOrderFreeScheme(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = (int(getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'no_of_pouch'))*int(free_scheme.container_quantity))+int(free_scheme.pouch_quantity)  
    else:
        free_scheme = 0
    return free_scheme

def getOrderFreeSchemePackagingType(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = str(free_scheme.free_variant_packaging_type)
    else:
        free_scheme = 0
    return free_scheme    

def getOrderFreeSchemeContainerSize(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        container_size = free_scheme.free_variant_container_size 
        per_ltr_kg = container_size.split()
        unit_name = per_ltr_kg[1].split('/')
        free_scheme = unit_name[0]
    else:
        free_scheme = 0
    return free_scheme
    
def getOrderFreeSchemeText(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')
    else:
        free_scheme = 0
    return free_scheme

def getFreeSchemeText(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, free_variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free_scheme = 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')
    else:
        free_scheme = 0
    return free_scheme


# Account List View
@login_required
def invoiceList(request):
    start_date                 = datetime.today().strftime('%Y-%m-%d')
    # end_date                   = datetime.today() + timedelta(days=1)
    # end_date                   = end_date.strftime('%Y-%m-%d')
    today_order_status            = SpOrders.objects.filter(indent_status=1,block_unblock=1, order_date__icontains=start_date).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0,order_date__icontains=start_date).count()
    orders_lists = SpOrders.objects.filter( indent_status=1,block_unblock=1, order_date__icontains=start_date).values('id', 'order_code','user_id', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count','tcs_value','production_unit_id').order_by('-id')
    
    user_list = []   
    if orders_lists:
        for order_list in orders_lists:
            users = SpUsers.objects.get(id=order_list['user_id'])
            try:
                address = SpAddresses.objects.get(user_id=order_list['user_id'], type='correspondence')
            except SpAddresses.DoesNotExist:
                address = None
            if address:
                order_list['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
            else:
                users['address'] = ''
            try:
                basic_details = SpBasicDetails.objects.get(user_id=order_list['user_id'])
            except SpBasicDetails.DoesNotExist:
                basic_details = None     

            if basic_details:
                order_list['cin']     = basic_details.cin
                order_list['gstin']   = basic_details.gstin
                order_list['fssai']   = basic_details.fssai
            else:
                order_list['cin']     = ''
                order_list['gstin']   = ''
                order_list['fssai']   = ''
            try:
                route_name = SpUserAreaAllocations.objects.get(user_id=order_list['user_id'])
            except SpUserAreaAllocations.DoesNotExist:
                route_name = None
            if route_name:
                order_list['route_name']     = route_name.route_name
            else:
                order_list['route_name']     = ''
            users_detail_list={}
            total_incentive = float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat'))+float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack'))
            
            invoice_amount = float(order_list['order_total_amount'])-total_incentive
            users_detail_list['id']                    = order_list['id']
            users_detail_list['user_id']               = order_list['user_id']
            users_detail_list['production_unit_id']    = order_list['production_unit_id']
            users_detail_list['user_name']             = users.first_name +' '+users.middle_name +' '+users.last_name
            users_detail_list['store_name']            = users.store_name
            users_detail_list['emp_sap_id']            = users.emp_sap_id
            users_detail_list['address']               = order_list['address']
            users_detail_list['cin']                   = order_list['cin']
            users_detail_list['gstin']                 = order_list['gstin']
            users_detail_list['fssai']                 = order_list['fssai']
            users_detail_list['route_name']            = order_list['route_name']
            users_detail_list['order_date']            = order_list['order_date'].strftime("%Y-%m-%d")
            users_detail_list['formate_order_date']    = order_list['order_date'].strftime("%d/%m/%Y")
            users_detail_list['order_code']            = order_list['order_code']
            users_detail_list['order_amount']          = order_list['order_total_amount']
            users_detail_list['flat_incentive']        = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat')
            users_detail_list['bulkpack_incentive']    = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack')
            tcs=order_list['tcs_value']
            if tcs:
                totalsum =round((invoice_amount*tcs/100),2)
                total= round(invoice_amount,2)+totalsum
                users_detail_list['invoice_amount']  = total
            else:
                users_detail_list['invoice_amount']   = round(invoice_amount,2)

            if SpOrderDetails.objects.filter(order_id=order_list['id']).exclude(gst=None):
                users_detail_list['withgst']=1 
            else:
                users_detail_list['withgst']=0
            if SpOrderDetails.objects.filter(order_id=order_list['id'],gst=None):
                users_detail_list['withoutgst']=1
            else:
                users_detail_list['withoutgst']=0
            if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').exists():
                invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').first()
                bill_invoice_pdf = invoices['invoice_path']
            else:
                bill_invoice_pdf = ''
            users_detail_list['bill_invoice_pdf']=bill_invoice_pdf

            if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').exists():
                invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').first()
                tax_invoice_pdf = invoices['invoice_path']
            else:
                tax_invoice_pdf = ''
            users_detail_list['tax_invoice_pdf']=tax_invoice_pdf
            user_list.append(users_detail_list)

    
    cdate = date.today().strftime("%d/%m/%Y")
    organizations=SpOrganizations.objects.all()
    
    context = {}
    context["organizations"]                = organizations
    context["cdate"]                        = cdate
    context['user_list']                    = user_list  
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Invoice List"
    template='accounts/invoice-list.html'
    return render(request, template, context) 

# Account List View
@login_required
def ajaxInvoiceList(request):
    start_date  = request.GET['start_date']
    # end_date    = datetime.strptime(request.GET['end_date'], "%Y-%m-%d")
    # end_date    = end_date + timedelta(days=1)
    
    today_order_status      = SpOrders.objects.filter(indent_status=1,block_unblock=1, order_date__icontains=start_date).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=start_date).count()
    orders_lists            = SpOrders.objects.filter(indent_status=1,block_unblock=1, order_date__icontains=start_date)
    if request.GET['id']:
        orders_lists = orders_lists.filter(user_id=request.GET['id']).values('id', 'order_code','user_id', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count','tcs_value','production_unit_id').order_by('-id')
    orders_lists = orders_lists.values('id', 'order_code','user_id', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count','tcs_value','production_unit_id').order_by('-id') 
    
    user_list = []   
    if orders_lists:
        for order_list in orders_lists:
            if request.GET['organization_id']:
                try:
                    users = SpUsers.objects.get(id=order_list['user_id'],organization_id=request.GET['organization_id'])
                    try:
                        address = SpAddresses.objects.get(user_id=order_list['user_id'], type='correspondence')
                    except SpAddresses.DoesNotExist:
                        address = None
                    if address:
                        order_list['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
                    else:
                        users['address'] = ''
                    try:
                        basic_details = SpBasicDetails.objects.get(user_id=order_list['user_id'])
                    except SpBasicDetails.DoesNotExist:
                        basic_details = None     

                    if basic_details:
                        order_list['cin']     = basic_details.cin
                        order_list['gstin']   = basic_details.gstin
                        order_list['fssai']   = basic_details.fssai
                    else:
                        order_list['cin']     = ''
                        order_list['gstin']   = ''
                        order_list['fssai']   = ''
                    try:
                        route_name = SpUserAreaAllocations.objects.get(user_id=order_list['user_id'])
                    except SpUserAreaAllocations.DoesNotExist:
                        route_name = None
                    if route_name:
                        order_list['route_name']     = route_name.route_name
                    else:
                        order_list['route_name']     = ''
                    
                    users_detail_list={}
                    total_incentive = float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat'))+float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack'))
                    invoice_amount = float(order_list['order_total_amount'])-total_incentive
                    users_detail_list['id']                    = order_list['id']
                    users_detail_list['user_id']               = order_list['user_id']
                    users_detail_list['production_unit_id']    = order_list['production_unit_id']
                    users_detail_list['user_name']             = users.first_name +' '+users.middle_name +' '+users.last_name
                    users_detail_list['store_name']            = users.store_name
                    users_detail_list['emp_sap_id']            = users.emp_sap_id
                    users_detail_list['address']               = order_list['address']
                    users_detail_list['cin']                   = order_list['cin']
                    users_detail_list['gstin']                 = order_list['gstin']
                    users_detail_list['fssai']                 = order_list['fssai']
                    users_detail_list['route_name']            = order_list['route_name']
                    users_detail_list['order_date']            = order_list['order_date'].strftime("%Y-%m-%d")
                    users_detail_list['formate_order_date']    = order_list['order_date'].strftime("%d/%m/%Y")
                    users_detail_list['order_code']            = order_list['order_code']
                    users_detail_list['order_amount']          = order_list['order_total_amount']
                    users_detail_list['flat_incentive']        = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat')
                    users_detail_list['bulkpack_incentive']    = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack')
                    tcs=order_list['tcs_value']
                    if tcs:
                        totalsum =round((invoice_amount*tcs/100),2)
                        total= round(invoice_amount,2)+totalsum
                        users_detail_list['invoice_amount']  = total
                    else:
                        users_detail_list['invoice_amount']   = round(invoice_amount,2)
                    if SpOrderDetails.objects.filter(order_id=order_list['id']).exclude(gst=None):
                        users_detail_list['withgst']=1 
                        # print(users_detail_list['withgst'])
                    else:
                        users_detail_list['withgst']=0
                        # print(users_detail_list['withgst'])
                    if SpOrderDetails.objects.filter(order_id=order_list['id'],gst=None):
                        users_detail_list['withoutgst']=1
                        # print(users_detail_list['withoutgst'])
                    else:
                        users_detail_list['withoutgst']=0
                        # print(users_detail_list['withoutgst'])
                    if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').exists():
                        invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').first()
                        bill_invoice_pdf = invoices['invoice_path']
                    else:
                        bill_invoice_pdf = ''
                    users_detail_list['bill_invoice_pdf']=bill_invoice_pdf
                    if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').exists():
                        invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').first()
                        tax_invoice_pdf = invoices['invoice_path']
                    else:
                        tax_invoice_pdf = ''
                    users_detail_list['tax_invoice_pdf']=tax_invoice_pdf
                    user_list.append(users_detail_list)
                except SpUsers.DoesNotExist:
                    users= ''
            else:
                users = SpUsers.objects.get(id=order_list['user_id'])
                try:
                    address = SpAddresses.objects.get(user_id=order_list['user_id'], type='correspondence')
                except SpAddresses.DoesNotExist:
                    address = None
                if address:
                    order_list['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
                else:
                    users['address'] = ''
                try:
                    basic_details = SpBasicDetails.objects.get(user_id=order_list['user_id'])
                except SpBasicDetails.DoesNotExist:
                    basic_details = None     

                if basic_details:
                    order_list['cin']     = basic_details.cin
                    order_list['gstin']   = basic_details.gstin
                    order_list['fssai']   = basic_details.fssai
                else:
                    order_list['cin']     = ''
                    order_list['gstin']   = ''
                    order_list['fssai']   = ''
                try:
                    route_name = SpUserAreaAllocations.objects.get(user_id=order_list['user_id'])
                except SpUserAreaAllocations.DoesNotExist:
                    route_name = None
                if route_name:
                    order_list['route_name']     = route_name.route_name
                else:
                    order_list['route_name']     = ''
                
                users_detail_list={}
                total_incentive = float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat'))+float(getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack'))
                invoice_amount = float(order_list['order_total_amount'])-total_incentive
                users_detail_list['id']                    = order_list['id']
                users_detail_list['user_id']               = order_list['user_id']
                users_detail_list['production_unit_id']    = order_list['production_unit_id']
                users_detail_list['user_name']             = users.first_name +' '+users.middle_name +' '+users.last_name
                users_detail_list['store_name']            = users.store_name
                users_detail_list['emp_sap_id']            = users.emp_sap_id
                users_detail_list['address']               = order_list['address']
                users_detail_list['cin']                   = order_list['cin']
                users_detail_list['gstin']                 = order_list['gstin']
                users_detail_list['fssai']                 = order_list['fssai']
                users_detail_list['route_name']            = order_list['route_name']
                users_detail_list['order_date']            = order_list['order_date'].strftime("%Y-%m-%d")
                users_detail_list['order_code']            = order_list['order_code']
                users_detail_list['order_amount']          = order_list['order_total_amount']
                users_detail_list['flat_incentive']        = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'flat')
                users_detail_list['bulkpack_incentive']    = getFlatBulkSchemeIncentiveOrderWise(order_list['id'], 'bulkpack')
                tcs=order_list['tcs_value']
                if tcs:
                    totalsum =round((invoice_amount*tcs/100),2)
                    total= round(invoice_amount,2)+totalsum
                    users_detail_list['invoice_amount']  = total
                else:
                    users_detail_list['invoice_amount']   = round(invoice_amount,2)
                if SpOrderDetails.objects.filter(order_id=order_list['id']).exclude(gst=None):
                    users_detail_list['withgst']=1 
                    # print(users_detail_list['withgst'])
                else:
                    users_detail_list['withgst']=0
                    # print(users_detail_list['withgst'])
                if SpOrderDetails.objects.filter(order_id=order_list['id'],gst=None):
                    users_detail_list['withoutgst']=1
                    # print(users_detail_list['withoutgst'])
                else:
                    users_detail_list['withoutgst']=0
                    # print(users_detail_list['withoutgst'])
                if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').exists():
                    invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='bill').values('invoice_path').first()
                    bill_invoice_pdf = invoices['invoice_path']
                else:
                    bill_invoice_pdf = ''
                users_detail_list['bill_invoice_pdf']=bill_invoice_pdf

                if SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').exists():
                    invoices = SpInvoices.objects.filter(created_date=start_date,user_id=order_list['user_id'],invoice_type='tax').values('invoice_path').first()
                    tax_invoice_pdf = invoices['invoice_path']
                else:
                    tax_invoice_pdf = ''
                users_detail_list['tax_invoice_pdf']=tax_invoice_pdf
                user_list.append(users_detail_list)
           
   
    context = {}
    context['user_list']                    = user_list  
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Invoice List"
    template='accounts/ajax-invoice-list.html'
    return render(request, template, context) 

#genrate and save invoice
@login_required
def genrateInvoiceTemplate(request):
    order_date          = request.POST['order_date']
    user_id             = request.POST['user_id']
    production_unit_id  = request.POST['production_unit_id']
    invoice_type        = request.POST['invoice_type']
    login_user          =request.user.id
    today                   = order_date
    today_order_status      = SpOrders.objects.filter(indent_status=1,block_unblock=1,order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    plant_id = getModelColumnByColumnId(SpBasicDetails, 'user_id', user_id, 'production_unit_id')
    today_date = datetime.now().strftime('%Y')+'-'+'04'+'-'+'01'
    if order_date == today_date:
        plant_invoice_serial_no = datetime.now().strftime('%Y')+''+getModelColumnById(SpProductionUnit, plant_id, 'invoice_serial_no')
        invoice_no = int(plant_invoice_serial_no)+1
    else:
        if SpInvoices.objects.filter(production_unit_id=plant_id,user_id=user_id).exists():
            invoice_serial_no = SpInvoices.objects.filter(production_unit_id=plant_id,user_id=user_id).order_by('-id').values('invoice_no').first()
            invoice_serial_no = int(invoice_serial_no['invoice_no'])+1
        else:
            plant_invoice_serial_no = datetime.now().strftime('%Y')+''+getModelColumnById(SpProductionUnit, plant_id, 'invoice_serial_no')
            invoice_serial_no = int(plant_invoice_serial_no)+1
        invoice_no = invoice_serial_no

    user_list = []
    distinct_user = user_id
    order_ids = SpOrders.objects.filter(user_id=distinct_user, order_date__icontains=today,production_unit_id=production_unit_id,block_unblock=1).values_list('id', flat=True)
    order_details = SpOrders.objects.filter(order_date__icontains=today, user_id=distinct_user,production_unit_id=production_unit_id,block_unblock=1).values('id', 'user_id', 'user_name', 'route_id', 'order_date', 'order_status', 'dispatch_order_status', 'tcs_value').first()
    
    organization_id   = getModelColumnById(SpUsers, user_id, 'organization_id')
    organization = SpOrganizations.objects.get(id=organization_id)
    user_dict = {}
    try:
        address = SpAddresses.objects.get(user_id=distinct_user, type='correspondence')
    except SpAddresses.DoesNotExist:
        address = None
    if address:
        user_dict['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
    else:
        user_dict['address'] = ''
    try:
        basic_details = SpBasicDetails.objects.get(user_id=user_id)
    except SpBasicDetails.DoesNotExist:
        basic_details = None    
    if basic_details:
        user_dict['cin']     = basic_details.cin
        user_dict['gstin']   = basic_details.gstin
        user_dict['fssai']   = basic_details.fssai
    else:
        user_dict['cin']     = ''
        user_dict['gstin']   = ''
        user_dict['fssai']   = ''
    
    user_dict['primary_contact_number'] = getModelColumnById(SpUsers, user_id, 'primary_contact_number')
    if user_dict['primary_contact_number']:
        contact_no = user_dict['primary_contact_number']
    else:
        contact_no = ''
    try:
        route_name = SpUserAreaAllocations.objects.get(user_id=user_id)
    except SpUserAreaAllocations.DoesNotExist:
        route_name = None  
    if route_name:
        user_dict['route_name']     = route_name.route_name
        user_dict['route_no']       = getModelColumnById(SpRoutes, route_name.route_id, 'route_code')
        user_dict['state_name']     = getModelColumnById(SpRoutes, route_name.route_id, 'state_name')
        state_id = getModelColumnById(SpRoutes, route_name.route_id, 'state_id')
        user_dict['inter_state']    = getModelColumnById(SpStates, state_id, 'inter_state')
        user_dict['state_code']     = getModelColumnById(SpStates, state_id, 'state_code')
    else:
        user_dict['route_name']     = ''
        user_dict['route_no']       = ''
        user_dict['state_name']     = ''
        user_dict['inter_state']    = ''
        user_dict['state_code']     = '' 

    user_list       = []
    no_of_pouches   = []
    quantity        = []
    rate            = []
    amount          = []
    cgst            = []
    sgst            = []
    total_amount    = []
    incentive_amount    = []

    users_list = {}
    taxable_bifurcations= []
    rate_bifurcations= []
    cgst_bifurcations= []
    sgst_bifurcations= []
    if order_ids:
        if invoice_type=='tax':
            order_details           = SpOrderDetails.objects.filter(order_id__in=order_ids).exclude(gst=None)
        else:
            order_details           = SpOrderDetails.objects.filter(order_id__in=order_ids,gst=None)
        for order_detail in order_details:
                
            taxable_bifurcation = {}
            rate_bifurcation    = {}
            cgst_bifurcation    = {}
            sgst_bifurcation    = {}   

            if order_detail.gst: 
                variant_gst = order_detail.gst
                half_of_gst = order_detail.gst/2
                hsn_code    = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
            else:
                variant_gst = 0

            quantity_in_ltr     = order_detail.quantity_in_ltr 
                
            order_detail.per_ltr_kg          = round((order_detail.amount/order_detail.quantity_in_ltr),2)
                
            order_detail.discount_per_unit   = float(getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user_id))/float(quantity_in_ltr)
                
            order_detail.net_price           = round((float(order_detail.per_ltr_kg)-float(order_detail.discount_per_unit)), 2)
                
            order_detail.basic_price         = round(((float(order_detail.net_price)/(1+float(variant_gst)/100))+float(order_detail.discount_per_unit)),2)
                
            order_detail.gross_amount        = round((float(quantity_in_ltr)*float(order_detail.basic_price)),2)
                
            order_detail.discount_amount     = round((float(quantity_in_ltr)*float(order_detail.discount_per_unit)),2)
            
            order_detail.net_amount          = round((float(order_detail.gross_amount)-float(order_detail.discount_amount)),2)
            
            order_detail.gst_amount         = round((float(order_detail.net_amount)*float(variant_gst)/100),2)
            gst  = float(order_detail.gst_amount)/2
            gst_cal = float(variant_gst)/2
            cgst_amount = round((float(order_detail.net_amount)*float(gst_cal)/100),2)
            cgst.append(cgst_amount)
            sgst.append(cgst_amount)
            
            if order_detail.gst:
                taxable_bifurcation[hsn_code] = order_detail.net_amount 
                taxable_bifurcations.append(taxable_bifurcation)
                cgst_bifurcation[hsn_code]  = cgst_amount
                cgst_bifurcations.append(cgst_bifurcation)
                sgst_bifurcation[hsn_code]  = cgst_amount
                sgst_bifurcations.append(sgst_bifurcation)
                rate_bifurcation[hsn_code]  = half_of_gst
                rate_bifurcations.append(rate_bifurcation)

            order_detail.hsn_code           = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
            order_detail.no_of_pouches      = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            order_detail.free_scheme        = getOrderFreeScheme(order_detail.product_variant_id, order_detail.order_id, user_id)
            order_detail.free_scheme_packaging_type = getOrderFreeSchemePackagingType(order_detail.product_variant_id, order_detail.order_id, user_id)
            order_detail.free_scheme_container_size = getOrderFreeSchemeContainerSize(order_detail.product_variant_id, order_detail.order_id, user_id)
            order_detail.discount        = getFlatScheme(order_detail.product_variant_id, order_detail.order_id,user_id)
            order_detail.free_scheme_text   = getOrderFreeSchemeText(order_detail.product_variant_id, order_detail.order_id, user_id)
            order_detail.free_scheme_in_ltr = getFreeSchemeInLtr(order_detail.product_variant_id, order_detail.order_id, user_id)
            order_code                      = getModelColumnById(SpOrders, order_detail.order_id, 'order_code')
            
            per_ltr_kg = order_detail.product_container_size.split()
            unit_name = per_ltr_kg[1].split('/')
            if unit_name[0] == 'L':
                order_detail.unit_name = 'LTR'
            else:
                order_detail.unit_name = unit_name[0]
            
            order_detail.final_amount        = round(float(order_detail.amount)-float(getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user_id)),2)
            
            no_of_pouches.append(order_detail.no_of_pouches)
            no_of_pouches.append(order_detail.free_scheme)
            quantity.append(order_detail.quantity)
            rate.append(order_detail.rate)
            amount.append(order_detail.amount)
            total_amount.append(order_detail.net_amount)
        users_list['id']                = user_id
        users_list['user_name']         = getUserName(distinct_user)
        users_list['contact_no']        = contact_no
        users_list['sap_code']          = getModelColumnByColumnId(SpUsers, 'id',distinct_user, 'emp_sap_id')
        users_list['store_name']        = getModelColumnById(SpUsers, distinct_user, 'store_name')
        users_list['address']           = user_dict['address']
        users_list['cin']               = user_dict['cin']
        users_list['gstin']             = user_dict['gstin']
        users_list['fssai']             = user_dict['fssai']
        users_list['state_name']        = user_dict['state_name']
        users_list['state_code']        = user_dict['state_code']
        users_list['inter_state']       = user_dict['inter_state']
        users_list['route_no']          = user_dict['route_no']
        users_list['route_name']        = user_dict['route_name']
        transporter_name = SpOrders.objects.get(id=order_detail.order_id)
        if transporter_name.transporter_name:
            users_list['transporter_name']           = transporter_name.transporter_name
        else:
            users_list['transporter_name']           = ''
        if transporter_name.transporter_details:
            users_list['transporter_details']        = transporter_name.transporter_details
        else:
            users_list['transporter_details']        = ''
        if transporter_name.vehicle_no:
            users_list['vehicle_no']                 = transporter_name.vehicle_no
        else:
            users_list['vehicle_no']                 = ''
        users_list['orders']            = order_details
        users_list['flat_incentive']    = getFlatBulkSchemeIncentive(user_id, 'flat', today)
        users_list['bulkpack_incentive']= getFlatBulkSchemeIncentive(user_id, 'bulkpack', today)
        users_list['total_incentive']   = float(users_list['flat_incentive'])+float(users_list['bulkpack_incentive'])
        
        incentive_amount.append(users_list['total_incentive'])
        user_list.append(users_list)

    today_date              = datetime.strptime(str(today), '%Y-%m-%d').strftime('%d/%m/%Y')
    co_name                 = getConfigurationResult('org_name')
    co_state_name           = getConfigurationResult('org_state_name')
    co_state_code           = getConfigurationResult('org_state_code')
    co_fssai                = getConfigurationResult('fssai')
    co_pan                  = getConfigurationResult('org_pan')
    co_footer_name          = getConfigurationResult('org_footer_name')
    co_address              = getConfigurationResult('org_address')
    co_gstin                = getConfigurationResult('gstin')
    co_cin                  = getConfigurationResult('cin')
    baseurl                 = settings.BASE_URL

    # sum the values with same keys
    taxable_values = {}
    taxable_value_total = 0
    if len(taxable_bifurcations) > 0:
        for d in taxable_bifurcations:
            for k in d.keys():
                taxable_values[k] = round((taxable_values.get(k, 0) + d[k]) ,2)
        taxable_value_total = taxable_values.values()
        taxable_value_total = round(sum(taxable_value_total),2)  
            
    cgst_values = {}
    cgst_value_total = 0
    if len(cgst_bifurcations) > 0:
        for d in cgst_bifurcations:
            for k in d.keys():
                cgst_values[k] = round((cgst_values.get(k, 0) + d[k]) ,2)
        cgst_value_total = cgst_values.values()
        cgst_value_total = round(sum(cgst_value_total),2)

    sgst_values = {}
    sgst_value_total = 0
    if len(sgst_bifurcations) > 0:
        for d in sgst_bifurcations:
            for k in d.keys():
                sgst_values[k] = round((sgst_values.get(k, 0) + d[k]) ,2)
        sgst_value_total = sgst_values.values()
        sgst_value_total = round(sum(sgst_value_total),2)

    rate_values = {}
    if len(rate_bifurcations) > 0:
        for d in rate_bifurcations:
            for k in d.keys():
                rate_values[k] = d[k]

    cgst                    = round(sum(cgst),2)
    sgst                    = round(sum(sgst),2)
    total_gst               = round((float(cgst)+float(sgst)),2)
    total_amount            = sum(total_amount)
    final_amount            = round((total_amount+float(cgst)+float(sgst)),2)
    
    total_gst_value         = str(total_gst).split('.')
    total_gst_value_in_words= convertToWords(int(total_gst_value[1]))
    gst_amount_in_words     = convertToWords(int(round(total_gst,0)))  
    if int(total_gst_value[1]) > 0:
        total_gst_value = '1'
    else:
        total_gst_value = '0'    
    order_details = SpOrders.objects.get(id=order_detail.order_id)
    if order_details.tcs_value:
        tcs_amount = round((float(final_amount)*(float(order_details.tcs_value)/100)),2)
    else:
        tcs_amount = 0
    
    grand_total = float(tcs_amount)+float(final_amount)    
    
    billing_amount          = normal_round(grand_total)
    final_amount            = billing_amount
    billing_amount_in_words = convertToWords(int(round(billing_amount,0)))
    context                     = {}
    context['organization']        = organization
    context['user_list']        = user_list
    context['quantity']         = sum(quantity)
    context['no_of_pouches']    = sum(no_of_pouches)
    context['rate']             = sum(rate)
    context['amount']           = sum(amount)
    context['grand_total']      = round(grand_total,2)
    context['tcs_amount']       = round(tcs_amount,2)
    context['net_amount']       = round(total_amount,2)
    context['total_amount']     = round(final_amount,2)
    context['total_gst_value']  = total_gst_value
    context['gst_amount_in_words'] = gst_amount_in_words
    context['total_gst_value_in_words'] = total_gst_value_in_words
    context['final_amount']     = normal_round(final_amount)
    context['billing_amount']   = billing_amount_in_words
    context['taxable_values']   = taxable_values
    context['cgst_values']      = cgst_values
    context['sgst']             = sgst
    context['cgst']             = cgst
    context['sgst_values']      = sgst_values
    context['rate_values']      = rate_values
    context['taxable_value_total'] = taxable_value_total
    context['cgst_value_total'] = cgst_value_total
    context['sgst_value_total'] = sgst_value_total
    context['url']              = baseurl
    context['today_date']       = today_date
    context['co_name']          = co_name
    context['co_state_name']    = co_state_name
    context['co_state_code']    = co_state_code
    context['co_fssai']         = co_fssai
    context['co_pan']           = co_pan
    context['co_footer_name']   = co_footer_name
    context['co_address']       = co_address
    template    = 'accounts/genrate-invoice-template.html'
    baseurl     = settings.BASE_URL
    response = {}
    filename = invoice_type+'_'+str(user_id)+'_'+str(order_date)
    pdf = save_invoice_pdf(filename, invoice_type,  template, context)
    if pdf:
        path = '/media/invoice_pdf/'+filename+'.pdf'
        invoice = SpInvoices()
        invoice.production_unit_id = plant_id
        invoice.invoice_no       = invoice_no
        invoice.user_id          = user_id
        invoice.invoice_type     = invoice_type
        invoice.invoice_path     = path
        invoice.created_date     = order_date
        invoice.status           = 0
        invoice.save()
        user_ledger=SpUserLedger()
        last_balance=SpUserLedger.objects.filter(user_id=user_id).values('balance').last()
        user_ledger.user_id=user_id
        user_ledger.order_id=getModelColumnByColumnId(SpOrders, 'user_id', user_id, 'id')
        user_ledger.invoice_no=invoice_no
        user_ledger.particulars=invoice_type
        user_ledger.debit=final_amount
        if last_balance:
            user_ledger.balance=final_amount+float(last_balance['balance'])
        else:
            user_ledger.balance=final_amount
        user_ledger.created_by=login_user
        user_ledger.save()
        response['error'] = True
        response['message'] = 'success'
        response['baseurl'] = baseurl
        response['filename'] = filename
    else:
        response['error'] = False
        response['message'] = 'error'    
    return JsonResponse(response)

def save_invoice_pdf(file_name, type, template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
    try:
        with open(str(settings.BASE_DIR)+f'/media/invoice_pdf/{file_name}.pdf','wb+') as output :
           pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),output)
    except Exception as e:
        print(e)

    if pdf.err:
        return '', False
    return file_name, True





@login_required
def printInvoice(request, order_date, invoice_id):
    today                   = order_date
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1, id=invoice_id).values('id', 'first_name', 'middle_name', 'last_name', 'store_name')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
        else:
            user['route_name']     = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today, user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                order_detail.hsn_code       = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                order_detail.no_of_pouches  = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
            users_list['id']        = user['id']
            users_list['user_name'] = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['store_name'] = user['store_name']
            users_list['address']   = user['address']
            users_list['cin']       = user['cin']
            users_list['gstin']     = user['gstin']
            users_list['fssai']     = user['fssai']
            users_list['route_name']= user['route_name']
            users_list['orders']    = order_details
            user_list.append(users_list)

    context = {}
    context['user_list']                    = user_list  
    context['today_order_status']           = today_order_status
    context['order_regenerate_status']      = order_regenerate_status
    context['invoice_id']                   = invoice_id
    context['page_title']                   = "Print Invoice"

    template = 'accounts/print-invoice.html'
    return render(request, template, context)

def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None

def normal_round(n):
    if n - math.floor(n) < 0.5:
        return math.floor(n)
    return math.ceil(n)
    

#Automaticly downloads to PDF file
@login_required
def printInvoiceTemplate(request, order_date, invoice_id):
    today                   = order_date
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1, id=invoice_id).values('id', 'first_name', 'middle_name', 'last_name', 'store_name', 'emp_sap_id', 'primary_contact_number')
    tcs_value   = SpOrders.objects.filter(order_date__icontains=today, user_id=invoice_id).values('tcs_value').first()

    for user in users:
        production_unit_id   = getModelColumnById(SpBasicDetails, user['id'], 'production_unit_id')
        organization_id   = getModelColumnById(SpUsers, user['id'], 'organization_id')
        organization = SpOrganizations.objects.get(id=organization_id)
        
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        if user['primary_contact_number']:
            contact_no = user['primary_contact_number']
        else:
            contact_no = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            user['route_name']     = route_name.route_name
            user['route_no']       = getModelColumnById(SpRoutes, route_name.route_id, 'route_code')
            user['state_name']     = getModelColumnById(SpRoutes, route_name.route_id, 'state_name')
            state_id = getModelColumnById(SpRoutes, route_name.route_id, 'state_id')
            user['inter_state']    = getModelColumnById(SpStates, state_id, 'inter_state')
            user['state_code']     = getModelColumnById(SpStates, state_id, 'state_code')
        else:
            user['route_name']     = ''
            user['route_no']       = ''
            user['state_name']     = ''
            user['inter_state']    = ''
            user['state_code']     = ''

    user_list       = []
    no_of_pouches   = []
    quantity        = []
    rate            = []
    amount          = []
    cgst            = []
    sgst            = []
    total_amount    = []
    incentive_amount    = []
    for user in users:
        orders      = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today, user_id=user['id']).values_list('id', flat=True)
        
        users_list = {}
        taxable_bifurcations= []
        rate_bifurcations= []
        cgst_bifurcations= []
        sgst_bifurcations= []
        
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            for order_detail in order_details:
                
                taxable_bifurcation = {}
                rate_bifurcation    = {}
                cgst_bifurcation    = {}
                sgst_bifurcation    = {}   

                if order_detail.gst: 
                    variant_gst = order_detail.gst
                    half_of_gst = order_detail.gst/2
                    hsn_code   = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                else:
                    variant_gst = 0

                quantity_in_ltr     = order_detail.quantity_in_ltr 
                   
                order_detail.per_ltr_kg          = round((order_detail.amount/order_detail.quantity_in_ltr),2)
                 
                order_detail.discount_per_unit   = float(getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user['id']))/float(quantity_in_ltr)
                 
                order_detail.net_price           = round((float(order_detail.per_ltr_kg)-float(order_detail.discount_per_unit)), 2)
                 
                order_detail.basic_price         = round(((float(order_detail.net_price)/(1+float(variant_gst)/100))+float(order_detail.discount_per_unit)),2)
                  
                order_detail.gross_amount        = round((float(quantity_in_ltr)*float(order_detail.basic_price)),2)
                 
                order_detail.discount_amount     = round((float(quantity_in_ltr)*float(order_detail.discount_per_unit)),2)
                
                order_detail.net_amount          = round((float(order_detail.gross_amount)-float(order_detail.discount_amount)),2)
                
                order_detail.gst_amount         = round((float(order_detail.net_amount)*float(variant_gst)/100),2)
                gst  = float(order_detail.gst_amount)/2
                gst_cal = float(variant_gst)/2
                cgst_amount = round((float(order_detail.net_amount)*float(gst_cal)/100),2)
                cgst.append(cgst_amount)
                sgst.append(cgst_amount)
                
                if order_detail.gst:
                    taxable_bifurcation[hsn_code] = order_detail.net_amount 
                    taxable_bifurcations.append(taxable_bifurcation)
                    cgst_bifurcation[hsn_code]  = cgst_amount
                    cgst_bifurcations.append(cgst_bifurcation)
                    sgst_bifurcation[hsn_code]  = cgst_amount
                    sgst_bifurcations.append(sgst_bifurcation)
                    rate_bifurcation[hsn_code]  = half_of_gst
                    rate_bifurcations.append(rate_bifurcation)

                order_detail.hsn_code           = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                order_detail.no_of_pouches      = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
                order_detail.free_scheme        = getOrderFreeScheme(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_packaging_type = getOrderFreeSchemePackagingType(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_container_size = getOrderFreeSchemeContainerSize(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.discount        = getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_text   = getOrderFreeSchemeText(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_in_ltr = getFreeSchemeInLtr(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_code                      = getModelColumnById(SpOrders, order_detail.order_id, 'order_code')
                
                per_ltr_kg = order_detail.product_container_size.split()
                unit_name = per_ltr_kg[1].split('/')
                if unit_name[0] == 'L':
                    order_detail.unit_name = 'LTR'
                else:
                    order_detail.unit_name = unit_name[0]
                
                order_detail.final_amount        = round(float(order_detail.amount)-float(getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user['id'])),2)
                
                no_of_pouches.append(order_detail.no_of_pouches)
                no_of_pouches.append(order_detail.free_scheme)
                quantity.append(order_detail.quantity)
                rate.append(order_detail.rate)
                amount.append(order_detail.amount)
                total_amount.append(order_detail.net_amount)
            users_list['id']                = user['id']
            users_list['user_name']         = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['contact_no']        = contact_no
            users_list['sap_code']          = user['emp_sap_id']
            users_list['store_name']        = user['store_name']
            users_list['address']           = user['address']
            users_list['cin']               = user['cin']
            users_list['gstin']             = user['gstin']
            users_list['fssai']             = user['fssai']
            users_list['state_name']        = user['state_name']
            users_list['state_code']        = user['state_code']
            users_list['inter_state']       = user['inter_state']
            users_list['route_no']          = user['route_no']
            users_list['route_name']        = user['route_name']
            users_list['transporter_name']           = getModelColumnById(SpOrders, orders[0], 'transporter_name')
            users_list['transporter_details']        = getModelColumnById(SpOrders, orders[0], 'transporter_details')
            users_list['vehicle_no']                 = getModelColumnById(SpOrders, orders[0], 'vehicle_no')
            users_list['orders']            = order_details
            users_list['flat_incentive']    = getFlatBulkSchemeIncentive(user['id'], 'flat', today)
            users_list['bulkpack_incentive']= getFlatBulkSchemeIncentive(user['id'], 'bulkpack', today)
            users_list['total_incentive']   = float(users_list['flat_incentive'])+float(users_list['bulkpack_incentive'])
            
            incentive_amount.append(users_list['total_incentive'])
            user_list.append(users_list)
          
    today_date              = datetime.strptime(str(today), '%Y-%m-%d').strftime('%d/%m/%Y')
    co_name                 = getConfigurationResult('org_name')
    co_state_name           = getConfigurationResult('org_state_name')
    co_state_code           = getConfigurationResult('org_state_code')
    co_fssai                = getConfigurationResult('fssai')
    co_pan                  = getConfigurationResult('org_pan')
    co_footer_name          = getConfigurationResult('org_footer_name')
    co_address              = getConfigurationResult('org_address')
   
    co_gstin                = getConfigurationResult('gstin')
    co_cin                  = getConfigurationResult('cin')
    baseurl                 = settings.BASE_URL
    
    
    # sum the values with same keys
    taxable_values = {}
    taxable_value_total = 0
    if len(taxable_bifurcations) > 0:
        for d in taxable_bifurcations:
            for k in d.keys():
                taxable_values[k] = round((taxable_values.get(k, 0) + d[k]) ,2)
        taxable_value_total = taxable_values.values()
        taxable_value_total = round(sum(taxable_value_total),2)  
            
    cgst_values = {}
    cgst_value_total = 0
    if len(cgst_bifurcations) > 0:
        for d in cgst_bifurcations:
            for k in d.keys():
                cgst_values[k] = round((cgst_values.get(k, 0) + d[k]) ,2)
        cgst_value_total = cgst_values.values()
        cgst_value_total = round(sum(cgst_value_total),2)

    sgst_values = {}
    sgst_value_total = 0
    if len(sgst_bifurcations) > 0:
        for d in sgst_bifurcations:
            for k in d.keys():
                sgst_values[k] = round((sgst_values.get(k, 0) + d[k]) ,2)
        sgst_value_total = sgst_values.values()
        sgst_value_total = round(sum(sgst_value_total),2)

    rate_values = {}
    if len(rate_bifurcations) > 0:
        for d in rate_bifurcations:
            for k in d.keys():
                rate_values[k] = d[k]

    cgst                    = round(sum(cgst),2)
    sgst                    = round(sum(sgst),2)
    total_gst               = round((float(cgst)+float(sgst)),2)
    total_amount            = sum(total_amount)
    final_amount            = round((total_amount+float(cgst)+float(sgst)),2)
    
    total_gst_value         = str(total_gst).split('.')
    total_gst_value_in_words= convertToWords(int(total_gst_value[1]))
    gst_amount_in_words     = convertToWords(int(round(total_gst,0)))  
    if int(total_gst_value[1]) > 0:
        total_gst_value = '1'
    else:
        total_gst_value = '0'    
    
    if tcs_value['tcs_value']:
        tcs_amount = round((float(final_amount)*(float(tcs_value['tcs_value'])/100)),2)
    else:
        tcs_amount = 0
    
    grand_total = float(tcs_amount)+float(final_amount)    
    
    billing_amount          = normal_round(grand_total)
    final_amount            = billing_amount
    billing_amount_in_words = convertToWords(int(round(billing_amount,0)))
    
    context                     = {}
    context['organization']        = organization
    context['user_list']        = user_list
    context['quantity']         = sum(quantity)
    context['no_of_pouches']    = sum(no_of_pouches)
    context['rate']             = sum(rate)
    context['amount']           = sum(amount)
    context['grand_total']      = round(grand_total,2)
    context['tcs_amount']       = round(tcs_amount,2)
    context['net_amount']       = round(total_amount,2)
    context['total_amount']     = round(final_amount,2)
    context['total_gst_value']  = total_gst_value
    context['gst_amount_in_words'] = gst_amount_in_words
    context['total_gst_value_in_words'] = total_gst_value_in_words
    context['final_amount']     = normal_round(final_amount)
    context['billing_amount']   = billing_amount_in_words
    context['taxable_values']   = taxable_values
    context['cgst_values']      = cgst_values
    context['sgst_values']      = sgst_values
    context['rate_values']      = rate_values
    context['taxable_value_total'] = taxable_value_total
    context['cgst_value_total'] = cgst_value_total
    context['sgst_value_total'] = sgst_value_total
    context['url']              = baseurl
    context['today_date']       = today_date
    context['co_name']          = co_name
    context['co_state_name']    = co_state_name
    context['co_state_code']    = co_state_code
    context['co_fssai']         = co_fssai
    context['co_pan']           = co_pan
    context['co_footer_name']   = co_footer_name
    context['co_address']       = co_address
    
    context['gstin']            = co_gstin
    context['cin']              = co_cin
    context['order_code']       = order_code
    context['cgst']             = cgst
    context['sgst']             = sgst
    context['total_gst']        = total_gst

    pdf         = render_to_pdf('accounts/print-invoice-template.html', context)
    response    = HttpResponse(pdf, content_type='application/pdf')
    filename    = 'Invoice.pdf'
    content     = "attachment; filename=%s" %(filename)
    response['Content-Disposition'] = content
    return response

#Automaticly downloads to PDF file
@login_required
def printAllInvoiceTemplate(request, order_date):
    today                   = order_date
    today_order_status      = SpOrders.objects.filter(indent_status=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()

    users = SpUsers.objects.filter(user_type=2, status=1).values('id', 'first_name', 'middle_name', 'last_name', 'store_name', 'emp_sap_id')
    for user in users:
        try:
            address = SpAddresses.objects.get(user_id=user['id'], type='correspondence')
        except SpAddresses.DoesNotExist:
            address = None
        if address:
            user['address'] = str(address.address_line_1)+', '+str(address.address_line_2)+', '+str(address.city_name)+', '+str(address.state_name)+', '+str(address.country_name)+', '+str(address.pincode)
        else:
            user['address'] = ''

        try:
            basic_details = SpBasicDetails.objects.get(user_id=user['id'])
        except SpBasicDetails.DoesNotExist:
            basic_details = None     

        if basic_details:
            user['cin']     = basic_details.cin
            user['gstin']   = basic_details.gstin
            user['fssai']   = basic_details.fssai
        else:
            user['cin']     = ''
            user['gstin']   = ''
            user['fssai']   = ''
        try:
            route_name = SpUserAreaAllocations.objects.get(user_id=user['id'])
        except SpUserAreaAllocations.DoesNotExist:
            route_name = None
        if route_name:
            if route_name.route_id:
                user['route_name']     = route_name.route_name
                user['route_no']       = getModelColumnById(SpRoutes, route_name.route_id, 'route_code')
                user['state_name']     = getModelColumnById(SpRoutes, route_name.route_id, 'state_name')
                state_id = getModelColumnById(SpRoutes, route_name.route_id, 'state_id')
                user['inter_state']    = getModelColumnById(SpStates, state_id, 'inter_state')
            else:
                user['route_name']     = ''
                user['route_no']       = ''
                user['state_name']     = ''
                user['inter_state']    = ''
        else:
            user['route_name']     = ''
            user['route_no']       = ''
            user['state_name']     = ''
            user['inter_state']    = ''

    user_list = []
    for user in users:
        orders  = SpOrders.objects.all().order_by('-id').filter(order_date__icontains=today, user_id=user['id']).values_list('id', flat=True)
        users_list = {}
        taxable_bifurcations= []
        rate_bifurcations= []
        cgst_bifurcations= []
        sgst_bifurcations= []
        incentive_amount = 0
        if orders:
            order_details           = SpOrderDetails.objects.filter(order_id__in=orders)
            no_of_pouches = 0
            cgst = 0
            sgst = 0
            total_amount = 0
            
            for order_detail in order_details:
                taxable_bifurcation = {}
                rate_bifurcation    = {}
                cgst_bifurcation    = {}
                sgst_bifurcation    = {}
                
                if order_detail.gst: 
                    variant_gst = order_detail.gst
                    half_of_gst = order_detail.gst/2
                    hsn_code   = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                else:
                    variant_gst = 0

                quantity_in_ltr     = order_detail.quantity_in_ltr 
                   
                order_detail.per_ltr_kg          = round((order_detail.amount/order_detail.quantity_in_ltr),2)
                 
                order_detail.discount_per_unit   = float(getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user['id']))/float(quantity_in_ltr)
                 
                order_detail.net_price           = round((float(order_detail.per_ltr_kg)-float(order_detail.discount_per_unit)), 2)
                 
                order_detail.basic_price         = round(((float(order_detail.net_price)/(1+float(variant_gst)/100))+float(order_detail.discount_per_unit)),2)
                 
                order_detail.gross_amount        = round((float(quantity_in_ltr)*float(order_detail.basic_price)),2)
                 
                order_detail.discount_amount     = round((float(quantity_in_ltr)*float(order_detail.discount_per_unit)),2)
                
                order_detail.net_amount          = round((float(order_detail.gross_amount)-float(order_detail.discount_amount)),2)
                
                order_detail.gst_amount         = round((float(order_detail.net_amount)*float(variant_gst)/100),2)
                gst  = float(order_detail.gst_amount)/2
                gst_cal = float(variant_gst)/2
                cgst_amount = round((float(order_detail.net_amount)*float(gst_cal)/100),2)
                cgst       = cgst+cgst_amount
                sgst       = sgst+cgst_amount
                    
                if order_detail.gst:
                    taxable_bifurcation[hsn_code] = order_detail.net_amount 
                    taxable_bifurcations.append(taxable_bifurcation)
                    cgst_bifurcation[hsn_code]  = cgst_amount
                    cgst_bifurcations.append(cgst_bifurcation)
                    sgst_bifurcation[hsn_code]  = cgst_amount
                    sgst_bifurcations.append(sgst_bifurcation)
                    rate_bifurcation[hsn_code]  = half_of_gst
                    rate_bifurcations.append(rate_bifurcation)
                    
                total_amount                    = total_amount + order_detail.net_amount
                
                order_detail.hsn_code           = getModelColumnById(SpProducts, order_detail.product_id, 'product_hsn')
                order_detail.no_of_pouches      = int(order_detail.product_no_of_pouch)*int(order_detail.quantity)
                order_detail.free_scheme        = getOrderFreeScheme(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_packaging_type = getOrderFreeSchemePackagingType(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_container_size = getOrderFreeSchemeContainerSize(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.discount        = getFlatScheme(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_detail.free_scheme_text   = getOrderFreeSchemeText(order_detail.product_variant_id, order_detail.order_id, user['id'])
                order_code                      = getModelColumnById(SpOrders, order_detail.order_id, 'order_code')
                order_detail.free_scheme_in_ltr = getFreeSchemeInLtr(order_detail.product_variant_id, order_detail.order_id, user['id'])
                
                per_ltr_kg = order_detail.product_container_size.split()
                unit_name = per_ltr_kg[1].split('/')
                order_detail.unit_name = unit_name[0]
                
                no_of_pouches                   = no_of_pouches+order_detail.no_of_pouches+order_detail.free_scheme
            
            # sum the values with same keys
            taxable_values = {}
            taxable_value_total = 0
            if len(taxable_bifurcations) > 0:
                for d in taxable_bifurcations:
                    for k in d.keys():
                        taxable_values[k] = round((taxable_values.get(k, 0) + d[k]) ,2)
                taxable_value_total = taxable_values.values()
                taxable_value_total = round(sum(taxable_value_total),2)  
                    
            cgst_values = {}
            cgst_value_total = 0
            if len(cgst_bifurcations) > 0:
                for d in cgst_bifurcations:
                    for k in d.keys():
                        cgst_values[k] = round((cgst_values.get(k, 0) + d[k]) ,2)
                cgst_value_total = cgst_values.values()
                cgst_value_total = round(sum(cgst_value_total),2)
        
            sgst_values = {}
            sgst_value_total = 0
            if len(sgst_bifurcations) > 0:
                for d in sgst_bifurcations:
                    for k in d.keys():
                        sgst_values[k] = round((sgst_values.get(k, 0) + d[k]) ,2)
                sgst_value_total = sgst_values.values()
                sgst_value_total = round(sum(sgst_value_total),2)
        
            rate_values = {}
            if len(rate_bifurcations) > 0:
                for d in rate_bifurcations:
                    for k in d.keys():
                        rate_values[k] = d[k]
                
            users_list['id']                = user['id']
            users_list['user_name']         = user['first_name']+' '+user['middle_name']+' '+user['last_name']
            users_list['sap_code']          = user['emp_sap_id']
            users_list['store_name']        = user['store_name']
            users_list['address']           = user['address']
            users_list['cin']               = user['cin']
            users_list['gstin']             = user['gstin']
            users_list['fssai']             = user['fssai']
            users_list['state_name']        = user['state_name']
            users_list['inter_state']       = user['inter_state']
            users_list['route_no']          = user['route_no']
            users_list['route_name']        = user['route_name']
            users_list['order_code']        = order_code
            users_list['orders']            = order_details
            users_list['transporter_name']           = getModelColumnById(SpOrders, order_detail.order_id, 'transporter_name')
            users_list['transporter_details']        = getModelColumnById(SpOrders, order_detail.order_id, 'transporter_details')
            users_list['vehicle_no']                 = getModelColumnById(SpOrders, order_detail.order_id, 'vehicle_no')
            users_list['flat_incentive']    = getFlatBulkSchemeIncentive(user['id'], 'flat', today)
            users_list['bulkpack_incentive']= getFlatBulkSchemeIncentive(user['id'], 'bulkpack', today)
            users_list['total_incentive']   = float(users_list['flat_incentive'])+float(users_list['bulkpack_incentive'])
            users_list['no_of_pouches']     = no_of_pouches
            users_list['cgst']              = round(cgst,2)
            users_list['sgst']              = round(sgst,2)
            users_list['total_gst']         = round((float(cgst)+float(sgst)),2)
            users_list['net_amount']        = round(total_amount, 2)
            final_amount = float(total_amount)+users_list['cgst']+users_list['sgst']
            users_list['total_amount']      = round(final_amount, 2)
            users_list['final_amount']      = normal_round(round(final_amount,2))
            billing_amount                  = users_list['final_amount']
            users_list['billing_amount']    = convertToWords(int(round(billing_amount,0)))
            total_gst_value                 = str(users_list['total_gst']).split('.')
            total_gst_value_in_words        = convertToWords(int(total_gst_value[1]))
            gst_amount_in_words             = convertToWords(int(round(users_list['total_gst'],0)))  
            if int(total_gst_value[1]) > 0:
                users_list['total_gst_value'] = '1'
            else:
                users_list['total_gst_value'] = '0'
            users_list['gst_amount_in_words'] = gst_amount_in_words
            users_list['total_gst_value_in_words'] = total_gst_value_in_words
            
            users_list['taxable_values']   = taxable_values
            users_list['cgst_values']      = cgst_values
            users_list['sgst_values']      = sgst_values
            users_list['rate_values']      = rate_values
            users_list['taxable_value_total'] = taxable_value_total
            users_list['cgst_value_total'] = cgst_value_total
            users_list['sgst_value_total'] = sgst_value_total
            
            users_list['quantity']          = SpOrderDetails.objects.filter(order_id=order_detail.order_id).aggregate(Sum('quantity'))['quantity__sum']
            users_list['rate']              = SpOrderDetails.objects.filter(order_id=order_detail.order_id).aggregate(Sum('rate'))['rate__sum']
            users_list['amount']            = SpOrderDetails.objects.filter(order_id=order_detail.order_id).aggregate(Sum('amount'))['amount__sum']
            user_list.append(users_list)
           
    today_date              = datetime.strptime(str(today), '%Y-%m-%d').strftime('%d/%m/%Y')
    co_name                 = getConfigurationResult('org_name')
    co_footer_name          = getConfigurationResult('org_footer_name')
    co_address              = getConfigurationResult('org_address')
    co_bank_account_no      = getConfigurationResult('org_bank_account_no')
    co_bank_name            = getConfigurationResult('org_bank_name')
    co_bank_branch_name     = getConfigurationResult('org_bank_branch_name')
    co_bank_ifsc            = getConfigurationResult('org_bank_ifsc')
    co_gstin                = getConfigurationResult('gstin')
    co_cin                  = getConfigurationResult('cin')
    baseurl                 = settings.BASE_URL
    context                 = {}
    context['user_list']                = user_list
    context['url']                      = baseurl
    context['today_date']               = today_date
    context['co_name']                  = co_name
    context['co_footer_name']           = co_footer_name
    context['co_address']               = co_address
    context['co_bank_account_no']       = co_bank_account_no
    context['co_bank_name']             = co_bank_name
    context['co_bank_branch_name']      = co_bank_branch_name
    context['co_bank_ifsc']             = co_bank_ifsc
    context['gstin']                    = co_gstin
    context['cin']                      = co_cin

    pdf         = render_to_pdf('accounts/print-all-invoice-template.html', context)
    response    = HttpResponse(pdf, content_type='application/pdf')
    filename    = 'Invoice.pdf'
    content     = "attachment; filename=%s" %(filename)
    response['Content-Disposition'] = content
    return response    




#gatepass and challan
@login_required
def gatePassAndChallan(request):
    today = date.today()
    today_order_status = SpOrders.objects.filter(indent_status=1,block_unblock=1,order_date__icontains=today.strftime("%Y-%m-%d")).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today.strftime("%Y-%m-%d")).count()
    production_units  = SpProductionUnit.objects.filter().order_by('production_unit_name')
    user_order_list = SpOrders.objects.filter(order_date__icontains=today, indent_status=1,block_unblock=1).values('id', 'order_code', 'user_id', 'user_sap_id', 'order_date', 'order_status', 'order_shift_id', 'production_unit_id').order_by('-id')
    users_list = []
    for user_list in user_order_list:
        user_list['user_id'] = user_list['user_id']
        user_list['name'] = getUserName(user_list['user_id'])
        user_list['user_sap_id'] = user_list['user_sap_id']
        user_list['store_name'] = getModelColumnById(SpUsers, user_list['user_id'], 'store_name')
        user_list['order_date'] = today.strftime('%Y-%m-%d')
        vehicle_ids = SpLogisticPlanDetail.objects.filter(order_id=user_list['id']).values_list('vehicle_id',flat=True).distinct()
        vehicle_detail=[]
        for vehicle_id in vehicle_ids:
            vehicle={}
            vehicle['vehicle_id']          =vehicle_id
            vehicle['registration_number'] =getModelColumnById(SpVehicles, vehicle_id, 'registration_number') 
            vehicle['route_name']          =getModelColumnById(SpVehicles, vehicle_id, 'route_name')
            if SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').exists():
                invoices = SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').first()
                challan_invoice_pdf = invoices['invoice_path']
            else:
                challan_invoice_pdf = ''
            vehicle['challan_invoice_pdf']=challan_invoice_pdf
            vehicle_detail.append(vehicle)
        user_list['vehicle_detail'] = vehicle_detail
        users_list.append(user_list)    
    organizations=SpOrganizations.objects.all()
    
    context = {}
    context["organizations"]                = organizations
    context['today_date']                   = today.strftime("%d/%m/%Y")
    context['users_list']                   = users_list
    context['production_units']             = production_units
    context['today_order_status']           = today_order_status
    # context['all_challan_invoice_pdf'] = all_challan_invoice_pdf
    context['order_regenerate_status']      = order_regenerate_status
    context['page_title']                   = "Manage Challans"
    template = 'accounts/gatepass-and-challan.html'
    return render(request, template, context)  
@login_required
def ajexGatePassAndChallan(request):
    today_date = request.GET['order_date']
    today = datetime.strptime(str(today_date), '%d/%m/%Y').strftime('%Y-%m-%d')
    today_order_status = SpOrders.objects.filter(indent_status=1,block_unblock=1, order_date__icontains=today).count()
    order_regenerate_status = SpOrders.objects.filter(indent_status=0, order_date__icontains=today).count()
    users_list = []
    if request.GET['organization_id']: 
        user=SpUsers.objects.filter(organization_id=request.GET['organization_id'])
        for i in user:
            try:
                user_order_list=SpOrders.objects.filter(user_id=i.id,order_date__icontains=today, indent_status=1,block_unblock=1).values('id', 'order_code', 'user_id', 'user_sap_id', 'order_date', 'order_status', 'order_shift_id', 'production_unit_id').order_by('-id')
                for user_list in user_order_list:
                    
                    user_list['user_id'] = user_list['user_id']
                    user_list['name'] = getUserName(user_list['user_id'])
                    user_list['user_sap_id'] = user_list['user_sap_id']
                    user_list['store_name'] = getModelColumnById(SpUsers, user_list['user_id'], 'store_name')
                    user_list['order_date'] = today
                    vehicle_ids = SpLogisticPlanDetail.objects.filter(order_id=user_list['id']).values_list('vehicle_id',flat=True).distinct()
                    vehicle_detail=[]
                    for vehicle_id in vehicle_ids:
                        vehicle={}
                        vehicle['vehicle_id']          =vehicle_id
                        vehicle['registration_number'] =getModelColumnById(SpVehicles, vehicle_id, 'registration_number') 
                        vehicle['route_name']          =getModelColumnById(SpVehicles, vehicle_id, 'route_name')
                        if SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').exists():
                            invoices = SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').first()
                            challan_invoice_pdf = invoices['invoice_path']
                        else:
                            challan_invoice_pdf = ''
                        vehicle['challan_invoice_pdf']=challan_invoice_pdf
                        vehicle_detail.append(vehicle)
                    user_list['vehicle_detail'] = vehicle_detail
                    users_list.append(user_list) 
            except SpOrders.DoesNotExist:
                user_list=''       
    else:
        user_order_list = SpOrders.objects.filter(order_date__icontains=today, indent_status=1,block_unblock=1).values('id', 'order_code', 'user_id', 'user_sap_id', 'order_date', 'order_status', 'order_shift_id', 'production_unit_id').order_by('-id')
        for user_list in user_order_list:
            user_list['user_id'] = user_list['user_id']
            user_list['name'] = getUserName(user_list['user_id'])
            user_list['user_sap_id'] = user_list['user_sap_id']
            user_list['store_name'] = getModelColumnById(SpUsers, user_list['user_id'], 'store_name')
            user_list['order_date'] = today
            vehicle_ids = SpLogisticPlanDetail.objects.filter(order_id=user_list['id']).values_list('vehicle_id',flat=True).distinct()
            vehicle_detail=[]
            for vehicle_id in vehicle_ids:
                vehicle={}
                vehicle['vehicle_id']          =vehicle_id
                vehicle['registration_number'] =getModelColumnById(SpVehicles, vehicle_id, 'registration_number') 
                vehicle['route_name']          =getModelColumnById(SpVehicles, vehicle_id, 'route_name')
                if SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').exists():
                    invoices = SpChallans.objects.filter(created_date=today,user_id=user_list['user_id'],vehicle_id=vehicle_id).values('invoice_path').first()
                    challan_invoice_pdf = invoices['invoice_path']
                else:
                    challan_invoice_pdf = ''
                vehicle['challan_invoice_pdf']=challan_invoice_pdf
                vehicle_detail.append(vehicle)
            user_list['vehicle_detail'] = vehicle_detail
            users_list.append(user_list) 
    context = {}
    context['users_list'] = users_list
    context['today_order_status'] = today_order_status
    context['order_regenerate_status'] = order_regenerate_status
    context['page_title'] = "Manage Gatepass & Challans"
    template = 'accounts/ajex-gatepass-and-challan.html'
    return render(request, template, context)

def save_challan_pdf(file_name, type, template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    response = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
    try:
        with open(str(settings.BASE_DIR)+f'/media/challan_pdf/{file_name}.pdf','wb+') as output :
           pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),output)
    except Exception as e:
        print(e)

    if pdf.err:
        return '', False
    return file_name, True
    
@login_required
def printGatepassAndChallan(request):
    user_ids = request.POST['user_id']
    order_date = request.POST['order_date']
    production_unit_id = request.POST['production_unit_id']
    invoice_type = request.POST['invoice_type']
    vehicle_id = request.POST['vehicle_id']
    plant_id = getModelColumnByColumnId(SpBasicDetails, 'user_id', user_ids, 'production_unit_id')

    today_date = datetime.now().strftime('%Y')+'-'+'04'+'01'
    if order_date == today_date:
        plant_invoice_serial_no = datetime.now().strftime('%Y')+''+getModelColumnById(SpProductionUnit, plant_id, 'invoice_serial_no')
        invoice_no = int(plant_invoice_serial_no)+1
    else:
        if SpChallans.objects.filter(production_unit_id=plant_id,user_id=user_ids).exists():
            invoice_serial_no = SpChallans.objects.filter(production_unit_id=plant_id,user_id=user_ids).order_by('-id').values('invoice_no').first()
            invoice_serial_no = int(invoice_serial_no['invoice_no'])+1
        else:
            plant_invoice_serial_no = datetime.now().strftime('%Y')+''+getModelColumnById(SpProductionUnit, plant_id, 'invoice_serial_no')
            invoice_serial_no = int(plant_invoice_serial_no)+1
        invoice_no = invoice_serial_no
    
    from .orders import getlogFreeSchemes
    from .orders import getcratetotal
    orderIds     = SpOrders.objects.filter(order_date__icontains=order_date,user_id=user_ids).values_list('id', flat=True)
   
    dis= SpUserCrateLedger.objects.filter(user_id=user_ids, normal_debit__gt=0, updated_datetime__icontains=order_date).order_by('-id').values('normal_debit','jumbo_debit').first()
    rec= SpUserCrateLedger.objects.filter(user_id=user_ids, normal_credit__gt=0, updated_datetime__icontains=order_date).order_by('-id').values('normal_credit','jumbo_credit').first()

    gatePassList = []
    for orderId in orderIds:
        distributor = {}
        productLists = SpLogisticPlanDetail.objects.filter(order_id=orderId,vehicle_id=vehicle_id).values('product_id','product_variant_id')
        allProducts = []
        total_issue_list = []
        schemecrate=0
        for product in productLists:
            productVariantList = SpProductVariants.objects.filter(product_id=product['product_id'],id=product['product_variant_id'])
            all_product_total_quantity = 0
            all_product_total_amount = 0
            product_total_quantity = 0   
            for productVariant in productVariantList:
                itemList = SpLogisticPlanDetail.objects.filter(order_id=orderId, product_variant_id=productVariant.id,vehicle_id=vehicle_id).distinct()
                if itemList:
                    quantity = 0
                    total_issue = {}
                    for item in itemList:
                        if item.packaging_type == "0":
                            quantity += item.quantity
                        elif item.packaging_type == "1":
                            quantity += (item.quantity /item.product_no_of_pouch)

                    container_type = item.product_container_type
                    if container_type in total_issue:
                        total_issue[item.product_container_type] += quantity
                    else:
                        total_issue[item.product_container_type] = quantity

                    if getModelColumnByColumnId(SpContainers,'container' , item.product_container_type, 'container'):
                        all_product_total_quantity += quantity
                        all_product_total_amount += item.amount

                    if item.tally_export_type == 0:
                        quantity = quantity
                        uom = item.product_container_type
                    else:
                        quantity = (quantity*item.product_no_of_pouch)
                        uom = item.product_packaging_type_name
                    if quantity > 0:
                        variantList = {}
                        variantList['product_name'] = itemList[0].product_name
                        variantList['variant_name'] = itemList[0].product_variant_name
                        variantList['uom'] = uom
                        variantList['quantity'] = quantity
                        product_total_quantity += quantity
                        variantList['amount'] = item.amount
                        variantList['scheme'] = getlogFreeSchemes(item.product_variant_id, item.order_id, user_ids,vehicle_id)
                        if container_type=='CRATE':
                            schemecrates = getcratetotal(item.product_variant_id, item.order_id, user_ids,vehicle_id)
                            if schemecrates is not None:
                                schemecrate=schemecrate+int(schemecrates)
                        total_issue_list.append(total_issue)
                        allProducts.append(variantList)
            crates_total_values = {}
            crates_total_value_total = 0
            if len(total_issue_list) > 0:
                for d in total_issue_list:
                    for k in d.keys():
                        crates_total_values[k] = round((crates_total_values.get(k, 0) + d[k]) ,2)
                crates_total_value_total = crates_total_values.values()
                crates_total_value_total = round(sum(crates_total_value_total),2)  
                
            containers = SpContainers.objects.all()
            new_crates_total_value_total = {}
            for container in containers:
                container_name=container.container
                if container_name in crates_total_values:
                    new_crates_total_value_total[container_name] = crates_total_values[container_name]
                else:
                    new_crates_total_value_total[container_name] = ""
            
            # order_total_amount = SpOrders.objects.filter(order_date__icontains=order_date,user_id=user_ids).values('order_total_amount').first() 
            distributor['order_date']           = datetime.strptime(str(order_date), '%Y-%m-%d').strftime('%d/%m/%Y')
            distributor['emp_sap_id']           = getModelColumnById(SpUsers, user_ids, 'emp_sap_id')
            distributor['store_name']           = getModelColumnById(SpUsers, user_ids, 'store_name')
            distributor['distributor_name']     = getUserName(user_ids)
            # distributor['order_total_amount']   = order_total_amount['order_total_amount']
            distributor['gstin']                = getModelColumnByColumnId(SpBasicDetails, 'user_id', user_ids, 'gstin')
            distributor['city_name']            = getModelColumnByColumnId(SpAddresses, 'user_id', user_ids, 'city_name')
            distributor['allProducts']          = allProducts
            distributor['crates_total_values']  = new_crates_total_value_total
            distributor['schemecrate']          = schemecrate
        gatePassList.append(distributor)
    context = {}
    try:
        challan_no  = SpChallans.objects.all().last()
        challan_no  = challan_no.id
    except SpChallans.DoesNotExist:
        challan_no = 0
    organization_id   = getModelColumnById(SpUsers, user_ids, 'organization_id')
    organization = SpOrganizations.objects.get(id=organization_id)
    context['organization']         = organization
    context['challan_no']           = 'PP' + str(challan_no + 1)
    context['vehicle__number']         = getModelColumnByColumnId(SpVehicles, 'id', vehicle_id, 'registration_number')
    context['dis']                  = dis
    context['rec']                  = rec
    context['fssai']                = getConfigurationResult('fssai')
    context['cin']                 = getConfigurationResult('cin')
    context['url']                  = settings.BASE_URL
    context['gatePassList']         = gatePassList
    context['superstockist_sap_id'] = getModelColumnById(SpUsers, user_ids, 'emp_sap_id')
    context['superstockist_name']   = getModelColumnById(SpUsers, user_ids, 'store_name')
    template    = 'accounts/distributor-gatepass-to-pdf-report.html'
    baseurl     = settings.BASE_URL
    response = {}
    filename = 'CHALLAN'+'_'+str(user_ids)+'_'+str(order_date)+'_'+str(vehicle_id)
    pdf = save_challan_pdf(filename, 'challan',  template, context)
    if pdf:
        path = '/media/challan_pdf/'+filename+'.pdf'
        invoice = SpChallans()
        invoice.production_unit_id = plant_id
        invoice.vehicle_id         = vehicle_id
        invoice.invoice_no       = invoice_no
        invoice.user_id          = user_ids
        invoice.invoice_type     = invoice_type
        invoice.invoice_path     = path
        invoice.created_date     = order_date
        invoice.status           = 0
        invoice.save()
        response['error'] = True
        response['message'] = 'success'
        response['baseurl'] = baseurl
        response['filename'] = filename
    else:
        response['error'] = False
        response['message'] = 'error'    
    return JsonResponse(response)
      
