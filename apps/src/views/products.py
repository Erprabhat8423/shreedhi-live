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
from ..models import *
from django.db.models import Q
from utils import *
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter
from django.forms.models import model_to_dict
import time
from PIL import Image

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from ..decorators import has_par

# Create your views here.

# products View
@login_required
@has_par(sub_module_id=17,permission='list')
def index(request):
    context = {}
    page = request.GET.get('page')
    products = SpProducts.objects.all().order_by('-id')
    
    last_product = SpProducts.objects.order_by('-id').first()
    if last_product:
        product_variants = SpProductVariants.objects.filter(product_id=last_product.id).order_by('-id')
        page = request.GET.get('page')
        variant_paginator = Paginator(product_variants, getConfigurationResult('page_limit'))
        try:
            product_variants = variant_paginator.page(page)
        except PageNotAnInteger:
            product_variants = variant_paginator.page(1)
        except EmptyPage:
            product_variants = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
            total_variant_pages = 0
        else:
            page = 1
            total_variant_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_variant_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
            total_variant_pages = total_variant_pages+1
        else:
            total_variant_pages = total_variant_pages

        context['total_variant_pages']            = total_variant_pages
    else:
        product_variants = {}
        context['total_variant_pages']            = 0

    
    context['products']          = products
    context['page_limit']             = getConfigurationResult('page_limit')
    context['product_variants']   = product_variants
    context['page_title'] = "Product & Variant Management"
    context['product_classes']          = SpProductClass.objects.filter(status=1)
    context['product_containers']          = SpContainers.objects.all()

    template = 'products/products.html'
    return render(request, template, context)


@login_required
@has_par(sub_module_id=17,permission='list')
def getProductVariants(request,product_id):
    if SpProducts.objects.filter(id=product_id).exists() :
        product_variants = SpProductVariants.objects.filter(product_id=product_id).order_by('order_of')
        page = request.GET.get('page')
        variant_paginator = Paginator(product_variants, getConfigurationResult('page_limit'))
        try:
            product_variants = variant_paginator.page(page)
        except PageNotAnInteger:
            product_variants = variant_paginator.page(1)
        except EmptyPage:
            product_variants = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
        else:
            page = 1
        total_variant_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_variant_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= variant_paginator.count):
            total_variant_pages = total_variant_pages+1
        else:
            total_variant_pages = total_variant_pages
        
        context = {}
        context['page_limit']             = getConfigurationResult('page_limit')
        context['total_variant_pages']     = total_variant_pages
        context['product_variants']   = product_variants
        template = 'products/product-variants.html'
        return render(request, template, context)
        
    else:
        return HttpResponse('Not found')



@login_required
@has_par(sub_module_id=17,permission='list')
def ajaxProductList(request):
    page = request.GET.get('page')
    organizations = SpOrganizations.objects.all().order_by('-id')
    paginator = Paginator(organizations, getConfigurationResult('page_limit'))

    try:
        organizations = paginator.page(page)
    except PageNotAnInteger:
        organizations = paginator.page(1)
    except EmptyPage:
        organizations = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1

    total_pages = int(paginator.count/getConfigurationResult('page_limit'))   
    
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    organization_details = SpOrganizations.objects.order_by('-id').first()
    
    context = {}
    context['organizations']          = organizations
    context['total_pages']            = total_pages
    context['organization_details']   = organization_details

    template = 'role-permission/ajax-products.html'
    return render(request, template, context)


@login_required
@has_par(sub_module_id=17,permission='list')
def ajaxProductVariantLists(request,product_id):
    if SpProducts.objects.filter(id=product_id).exists() :

        product_variants = SpProductVariants.objects.filter(product_id=product_id).order_by('-id')
        page = request.GET.get('page')
        variant_paginator = Paginator(product_variants, getConfigurationResult('page_limit'))
        try:
            product_variants = variant_paginator.page(page)
        except PageNotAnInteger:
            product_variants = variant_paginator.page(1)
        except EmptyPage:
            product_variants = variant_paginator.page(variant_paginator.num_pages)  
        if page is not None:
            page = page
        else:
            page = 1
        total_variant_pages = int(variant_paginator.count/getConfigurationResult('page_limit')) 
        
        if(variant_paginator.count == 0):
            variant_paginator.count = 1

        temp = total_variant_pages%variant_paginator.count
        if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
            total_variant_pages = total_variant_pages+1
        else:
            total_variant_pages = total_variant_pages
        
        context = {}
        context['page_limit']             = getConfigurationResult('page_limit')
        context['total_variant_pages']     = total_variant_pages
        context['product_variants']   = product_variants
        template = 'products/ajax-product-variant-lists.html'
        return render(request, template, context)

    else:
        return HttpResponse('Not found')

    





@login_required
@has_par(sub_module_id=17,permission='add')
def addProduct(request):
    template = 'products/add-product.html'
    context = {}
    context['product_classes']          = SpProductClass.objects.filter(status=1)
    context['product_containers']          = SpContainers.objects.all()
    context['color_codes']          = SpColorCodes.objects.filter(status=1)
    return render(request, template,context)


@login_required
@has_par(sub_module_id=17,permission='add')
def saveProduct(request):
    if request.method == "POST":
        response = {}
        try:
            product_class_id = request.POST.get('product_class_id')
            product_name = request.POST.get('product_name')
            product_container_id = request.POST.get('product_container_id')

            
            if product_class_id == '':
                response['flag'] = False
                response['message'] = "Please select product class"
            elif product_name == '':
                response['flag'] = False
                response['message'] = "Please enter product name"
            elif SpProducts.objects.filter(product_name=product_name).exists():
                response['flag'] = False
                response['message'] = "Product name already exists"
            
            elif product_container_id == '':
                response['flag'] = False
                response['message'] = "Please select container"   
            
            else:
                product = SpProducts()
                product.product_class_id = request.POST['product_class_id']
                product.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
                product.product_hsn = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_hsn')
                product.product_name = request.POST['product_name']
                product.product_color_code = request.POST['product_color_code']
                product.description = request.POST['description']
                product.status  = 1
                product.save()

                if product.id :

                    #Save Activity
                    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    heading     = 'New product created'
                    activity    = 'New product created by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                    saveActivity('Product & Variant Management', 'Create Product', heading, activity, request.user.id, user_name, 'addProduct.png', '1', 'web.png')
                    
                    response['flag'] = True
                    response['message'] = "Record has been saved successfully."
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"

            return JsonResponse(response)
        
        except Exception as e:
            response['flag'] = False
            response['message'] = str(e)
            return JsonResponse(response)
    else:
        response = {}
        response['error'] = False
        response['message'] = "Method not allowed"
        return JsonResponse(response)


@login_required
@has_par(sub_module_id=17,permission='edit')
def editProduct(request,product_id):
    if request.method == "POST":
        response = {}
        try:
            if SpProducts.objects.filter(product_name=request.POST['product_name']).exclude(id=request.POST['product_id']).exists():
                response['flag'] = False
                response['message'] = "Product name already exist"
            else:
                product = SpProducts.objects.get(id=request.POST['product_id'])
                product.product_class_id = request.POST['product_class_id']
                product.product_class_name = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_class')
                product.product_hsn = getModelColumnById(SpProductClass,request.POST['product_class_id'],'product_hsn')
                product.product_name = request.POST['product_name']
                product.product_color_code = request.POST['product_color_code']
                product.description = request.POST['description']
                product.status  = 1
                product.save()

                if product.id :

                    #Save Activity
                    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    heading     = 'Product edited'
                    activity    = 'Product edited by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                    saveActivity('Product & Variant Management', 'Edit Product', heading, activity, request.user.id, user_name, 'edit_product.png', '1', 'web.png')

                    response['flag'] = True
                    response['message'] = "Record has been saved successfully."
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['product']     = SpProducts.objects.get(id=product_id)
        context['product_classes']        = SpProductClass.objects.filter(status=1)
        context['product_containers']     = SpContainers.objects.all()
        context['product_units']          = SpProductUnits.objects.filter(status=1)
        context['color_codes']          = SpColorCodes.objects.filter(status=1)
        template = 'products/edit-product.html'
        return render(request, template, context)

@login_required
@has_par(sub_module_id=17,permission='add')
def addProductVariant(request,product_id):
    if request.method == "POST":
        response = {}
        try:
            if SpProductVariants.objects.filter(item_sku_code=request.POST['item_code']).exists():
                response['flag'] = False
                response['confirm'] = True
                response['message'] = request.POST['item_code']+" Item code already exists."
            else:
                production_unit_ids = request.POST.getlist('production_unit_id[]')
                product_variant = SpProductVariants()
                product_variant.product_id = request.POST['product_id']
                product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
                product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
                product_variant.container_id  = request.POST['container_id']
                product_variant.container_name  = getModelColumnById(SpContainers,request.POST['container_id'],'container')
                product_variant.packaging_type_id  = request.POST['packaging_type_id']
                product_variant.packaging_type_name  = getModelColumnById(SpPackagingType,request.POST['packaging_type_id'],'packaging_type')
                # product_variant.sales_leger  = getModelColumnById(SalesLedger,request.POST['leadger_name'],'leadger_name')
                product_variant.item_sku_code = request.POST['item_code']
                product_variant.variant_quantity = request.POST['variant_qty']
                product_variant.variant_unit_id  = request.POST['variant_unit']
                product_variant.variant_name  = request.POST['variant_name']
                product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
                product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
                product_variant.variant_size  = request.POST['variant_size']
                product_variant.no_of_pouch  = request.POST['no_of_pouch']
                product_variant.container_size  = request.POST['container_size']
                product_variant.is_bulk_pack  = request.POST['variant_type']
                product_variant.is_allow_in_packaging  = request.POST['is_allow_in_packaging']
                product_variant.mrp  = request.POST['mrp']
                product_variant.sp_distributor  = request.POST['sp_distributor']
                product_variant.sp_superstockist  = request.POST['sp_superstockist']
                product_variant.sp_employee  = request.POST['sp_employee']
                product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_distributor  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_superstockist  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_employee  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])
                product_variant.valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
                product_variant.valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
                product_variant.production_unit_id   = ','.join([str(elem) for elem in production_unit_ids ]) 
                if request.POST['gst']:
                    product_variant.gst  = request.POST['gst']
                product_variant.status  = 1
                product_variant.save()
                if product_variant.id:
                    users_details     = SpBasicDetails.objects.filter(production_unit_id__in = production_unit_ids)
                    operational_users = SpUsers.objects.filter(Q(is_distributor=1) | Q(is_super_stockist=1),id__in=users_details.values('user_id')).values('id','user_type','is_distributor','is_super_stockist')
                    
                    if len(operational_users) :
                        for operational_user in operational_users :
                            user_product_variant                    = SpUserProductVariants()
                            user_product_variant.user_id            = operational_user['id']
                            user_product_variant.product_id         = request.POST['product_id']
                            user_product_variant.product_name       = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
                            user_product_variant.product_variant_id = product_variant.id
                            user_product_variant.product_class_id   = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
                            user_product_variant.item_sku_code      = request.POST['item_code']
                            user_product_variant.variant_quantity   = request.POST['variant_qty']
                            user_product_variant.variant_unit_id    = request.POST['variant_unit']
                            user_product_variant.variant_name       = request.POST['variant_name']
                            user_product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
                            user_product_variant.largest_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
                            user_product_variant.variant_size       = request.POST['variant_size']
                            user_product_variant.no_of_pouch        = request.POST['no_of_pouch']
                            user_product_variant.container_size     = request.POST['container_size']
                            user_product_variant.is_bulk_pack       = request.POST['variant_type']
                            # user_product_variant.included_in_scheme  = request.POST['included_in_scheme']
                            user_product_variant.mrp  = request.POST['mrp']
                            user_product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])

                            if operational_user['user_type'] == 1 :
                                user_product_variant.sp_user  = request.POST['sp_employee']
                                user_product_variant.container_sp_user  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])
                            else:
                                if operational_user['is_distributor'] == 1:
                                    user_product_variant.sp_user = request.POST['sp_distributor']
                                    user_product_variant.container_sp_user  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
                                else:
                                    user_product_variant.sp_user = request.POST['sp_superstockist']
                                    user_product_variant.container_sp_user  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
                            

                            user_product_variant.valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
                            user_product_variant.valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
                            user_product_variant.status  = 1
                            user_product_variant.save()

                    variant_images       = request.FILES.getlist('variantImage[]')
                    i = 0 
                    for variant_image in variant_images:
                        folder='media/product_variant_images/' 
                        storage = FileSystemStorage(location=folder)
                        timestamp = int(time.time())
                        variant_image_name = variant_image.name
                        temp = variant_image_name.split('.')
                        variant_image_name = str(product_variant.id) + "_"+str(timestamp)+"_"+str(i)+"."+temp[(len(temp) - 1)]
                        
                        uploaded_variant_image = storage.save(variant_image_name, variant_image)
                        product_variant_image = SpProductVariantImages()
                        product_variant_image.product_variant_id = product_variant.id
                        product_variant_image.image_url = folder+variant_image_name
                    
                        # create thumbnail
                        image_file = str(settings.MEDIA_ROOT) + '/product_variant_images/'+variant_image_name
                        size = 300, 300
                        im = Image.open(image_file)

                        if im.mode in ("RGBA", "P"):
                            im = im.convert("RGB")

                        im.thumbnail(size, Image.ANTIALIAS)
                        thumbnail_image = str(settings.MEDIA_ROOT) + '/product_variant_images/thumbnail/'+variant_image_name
                        im.save(thumbnail_image, "JPEG",quality=100)

                        product_variant_image.thumbnail_url = 'media/product_variant_images/thumbnail/'+variant_image_name
                        product_variant_image.save()

                        i = i+1
                        
                    #Save Activity
                    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    heading     = 'Product variant created'
                    activity    = 'Product variant created by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                    saveActivity('Product & Variant Management', 'Add Product Variant', heading, activity, request.user.id, user_name, 'addProduct.png', '1', 'web.png')

                    response['flag'] = True
                    response['message'] = "Record has been saved successfully."
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"

        except Exception as e:
            response['flag'] = False
            response['message'] = str(e)
        return JsonResponse(response)

    else:
        template = 'products/add-product-variant.html'
        context = {}
        context['products']         = SpProducts.objects.filter(status=1)
        context['product']          = SpProducts.objects.get(id=product_id)
        context['product_units']    = SpProductUnits.objects.filter(status=1)
        context['gst_list']         = SpGst.objects.filter()
        context['product_containers']     = SpContainers.objects.filter(status=1)
        context['packaging_types']     = SpPackagingType.objects.filter(status=1)
        context['production_unit']  = SpProductionUnit.objects.all()
        # context['sales_ledger']     = SalesLedger.objects.all().distinct()

    return render(request, template,context)


# @login_required
# @has_par(sub_module_id=17,permission='add')
# def addProductVariant(request,product_id):
#     if request.method == "POST":
#         response = {}
#         try:
#             if SpProductVariants.objects.filter(item_sku_code=request.POST['item_code']).exists():
#                 response['flag'] = False
#                 response['confirm'] = True
#                 response['message'] = request.POST['item_code']+" Item code already exists."
#             else:
#                 product_variant = SpProductVariants()
#                 product_variant.product_id = request.POST['product_id']
#                 product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
#                 product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
#                 product_variant.container_id  = request.POST['container_id']
#                 product_variant.container_name  = getModelColumnById(SpContainers,request.POST['container_id'],'container')
#                 product_variant.packaging_type_id  = request.POST['packaging_type_id']
#                 product_variant.packaging_type_name  = getModelColumnById(SpPackagingType,request.POST['packaging_type_id'],'packaging_type')
#                 product_variant.item_sku_code = request.POST['item_code']
#                 product_variant.variant_quantity = request.POST['variant_qty']
#                 product_variant.variant_unit_id  = request.POST['variant_unit']
#                 product_variant.variant_name  = request.POST['variant_name']
#                 product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
#                 product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
#                 product_variant.variant_size  = request.POST['variant_size']
#                 product_variant.no_of_pouch  = request.POST['no_of_pouch']
#                 product_variant.container_size  = request.POST['container_size']
#                 product_variant.is_bulk_pack  = request.POST['variant_type']
#                 product_variant.is_allow_in_packaging  = request.POST['is_allow_in_packaging']
#                 product_variant.mrp  = request.POST['mrp']
#                 product_variant.sp_distributor  = request.POST['sp_distributor']
#                 product_variant.sp_superstockist  = request.POST['sp_superstockist']
#                 product_variant.sp_employee  = request.POST['sp_employee']
#                 product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
#                 product_variant.container_sp_distributor  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
#                 product_variant.container_sp_superstockist  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
#                 product_variant.container_sp_employee  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])
#                 product_variant.valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                 product_variant.valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                 product_variant.production_unit_id   = ','.join([str(elem) for elem in request.POST.getlist('production_unit_id[]')]) 
#                 if request.POST['gst']:
#                     product_variant.gst  = request.POST['gst']
#                 product_variant.status  = 1
#                 product_variant.save()
#                 if product_variant.id:
#                     operational_users = SpUsers.objects.filter(Q(is_distributor=1) | Q(is_super_stockist=1)).values('id','user_type','is_distributor','is_super_stockist')
#                     if len(operational_users) :
#                         for operational_user in operational_users :
#                             user_product_variant = SpUserProductVariants()
#                             user_product_variant.user_id = operational_user['id']
#                             user_product_variant.product_id = request.POST['product_id']
#                             user_product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
#                             user_product_variant.product_variant_id = product_variant.id
#                             user_product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
#                             user_product_variant.item_sku_code = request.POST['item_code']
#                             user_product_variant.variant_quantity = request.POST['variant_qty']
#                             user_product_variant.variant_unit_id  = request.POST['variant_unit']
#                             user_product_variant.variant_name  = request.POST['variant_name']
#                             user_product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
#                             user_product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
#                             user_product_variant.variant_size  = request.POST['variant_size']
#                             user_product_variant.no_of_pouch  = request.POST['no_of_pouch']
#                             user_product_variant.container_size  = request.POST['container_size']
#                             user_product_variant.is_bulk_pack  = request.POST['variant_type']
#                             # user_product_variant.included_in_scheme  = request.POST['included_in_scheme']
#                             user_product_variant.mrp  = request.POST['mrp']
#                             user_product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])

#                             if operational_user['user_type'] == 1 :
#                                 user_product_variant.sp_user  = request.POST['sp_employee']
#                                 user_product_variant.container_sp_user  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])
#                             else:
#                                 if operational_user['is_distributor'] == 1:
#                                     user_product_variant.sp_user = request.POST['sp_distributor']
#                                     user_product_variant.container_sp_user  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
#                                 else:
#                                     user_product_variant.sp_user = request.POST['sp_superstockist']
#                                     user_product_variant.container_sp_user  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
                            

#                             user_product_variant.valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                             user_product_variant.valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                             user_product_variant.status  = 1
#                             user_product_variant.save()

#                     variant_images       = request.FILES.getlist('variantImage[]')
#                     i = 0 
#                     for variant_image in variant_images:
#                         folder='media/product_variant_images/' 
#                         storage = FileSystemStorage(location=folder)
#                         timestamp = int(time.time())
#                         variant_image_name = variant_image.name
#                         temp = variant_image_name.split('.')
#                         variant_image_name = str(product_variant.id) + "_"+str(timestamp)+"_"+str(i)+"."+temp[(len(temp) - 1)]
                        
#                         uploaded_variant_image = storage.save(variant_image_name, variant_image)
#                         product_variant_image = SpProductVariantImages()
#                         product_variant_image.product_variant_id = product_variant.id
#                         product_variant_image.image_url = folder+variant_image_name
                    
#                         # create thumbnail
#                         image_file = str(settings.MEDIA_ROOT) + '/product_variant_images/'+variant_image_name
#                         size = 300, 300
#                         im = Image.open(image_file)

#                         if im.mode in ("RGBA", "P"):
#                             im = im.convert("RGB")

#                         im.thumbnail(size, Image.ANTIALIAS)
#                         thumbnail_image = str(settings.MEDIA_ROOT) + '/product_variant_images/thumbnail/'+variant_image_name
#                         im.save(thumbnail_image, "JPEG",quality=100)

#                         product_variant_image.thumbnail_url = 'media/product_variant_images/thumbnail/'+variant_image_name
#                         product_variant_image.save()

#                         i = i+1
                        
#                     #Save Activity
#                     user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
#                     heading     = 'Product variant created'
#                     activity    = 'Product variant created by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
#                     saveActivity('Product & Variant Management', 'Add Product Variant', heading, activity, request.user.id, user_name, 'addProduct.png', '1', 'web.png')

#                     response['flag'] = True
#                     response['message'] = "Record has been saved successfully."
#                 else:
#                     response['flag'] = False
#                     response['message'] = "Failed to save"

#         except Exception as e:
#             response['flag'] = False
#             response['message'] = str(e)
#         return JsonResponse(response)

#     else:
#         template = 'products/add-product-variant.html'
#         context = {}
#         context['products']         = SpProducts.objects.filter(status=1)
#         context['product']          = SpProducts.objects.get(id=product_id)
#         context['product_units']    = SpProductUnits.objects.filter(status=1)
#         context['gst_list']         = SpGst.objects.filter()
#         context['product_containers']     = SpContainers.objects.filter(status=1)
#         context['packaging_types']     = SpPackagingType.objects.filter(status=1)
#         context['production_unit']  = SpProductionUnit.objects.all()

#     return render(request, template,context)

# @login_required
# @has_par(sub_module_id=17,permission='edit')
# def editProductVariant(request,product_variant_id):
#     if request.method == "POST":
#         response = {}
#         try:
#             product_variant = SpProductVariants.objects.get(id=request.POST['product_variant_id'])
#             if (int(request.POST['update_confirm']) == 0) and ((float(request.POST['mrp']) !=  float(product_variant.mrp)) or (float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor)) or (float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist))) :
#                 response['flag'] = False
#                 response['confirm'] = True
#                 response['message'] = "MRP/SP.Distributor/SP.Super Stockist has been changed. Do you want save changes?"
#             else:
#                 if SpProductVariants.objects.filter(item_sku_code=request.POST['item_code']).exclude(id=product_variant.id).exists():
#                     response['flag'] = False
#                     response['message'] = request.POST['item_code']+" Item code already exists."
#                 else:
#                     valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                     valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')

#                     if (str(valid_from) != str(product_variant.valid_from)) or (str(valid_to) != str(product_variant.valid_to)) or  ((float(request.POST['mrp']) !=  float(product_variant.mrp)) or (float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor)) or (float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist))) :
#                             description = ''
#                             if (str(valid_from) != str(product_variant.valid_from)) :
#                                 description += 'From date changed from '+ str(product_variant.valid_from) +' to '+valid_from +'. '
#                             if (str(valid_to) != str(product_variant.valid_to)) :
#                                 description += 'To date changed from '+ str(product_variant.valid_to) +' to '+valid_to +'. '
#                             if float(request.POST['mrp']) !=  float(product_variant.mrp) :
#                                 description += 'MRP changed from '+ str(product_variant.mrp) +' to '+request.POST['mrp'] +'. '
#                             if float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor) :
#                                 description += 'SP Distributor changed from '+ str(product_variant.sp_distributor) +' to '+request.POST['sp_distributor'] +'. '
#                             if float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist) :
#                                 description += 'SP Super Stockist changed from '+ str(product_variant.sp_superstockist) +' to '+request.POST['sp_superstockist'] +'. '
#                             if float(request.POST['sp_employee']) !=  float(product_variant.sp_employee) :
#                                 description += 'SP Employee changed from '+ str(product_variant.sp_employee) +' to '+request.POST['sp_employee'] +'. '

#                             history = SpProductVariantsHistory()
#                             current_user = request.user
#                             history.user_id  = current_user.id
#                             history.user_name  = str(current_user.first_name) + " " + current_user.middle_name+ " " + current_user.last_name
#                             history.product_variant_id  = product_variant.id
#                             history.mrp  = product_variant.mrp
#                             history.sp_distributor  = product_variant.sp_distributor
#                             history.sp_superstockist  = product_variant.sp_superstockist
#                             history.sp_employee  = product_variant.sp_employee

#                             history.container_mrp  = product_variant.container_mrp
#                             history.container_sp_distributor  = product_variant.container_sp_distributor
#                             history.container_sp_superstockist  = product_variant.container_sp_superstockist
#                             history.container_sp_employee  = product_variant.container_sp_employee

#                             history.valid_from = product_variant.valid_from
#                             history.valid_to = product_variant.valid_to
#                             if product_variant.gst:
#                                 history.gst = product_variant.gst
#                             history.description = description
#                             history.save()
                        

#                     product_variant.product_id = request.POST['product_id']
#                     product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
#                     product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
#                     product_variant.item_sku_code = request.POST['item_code']
#                     product_variant.container_id  = request.POST['container_id']
#                     product_variant.container_name  = getModelColumnById(SpContainers,request.POST['container_id'],'container')
#                     product_variant.packaging_type_id  = request.POST['packaging_type_id']
#                     product_variant.packaging_type_name  = getModelColumnById(SpPackagingType,request.POST['packaging_type_id'],'packaging_type')
#                     product_variant.variant_quantity = request.POST['variant_qty']
#                     product_variant.variant_unit_id  = request.POST['variant_unit']
#                     product_variant.variant_name  = request.POST['variant_name']
#                     product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
#                     product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
#                     product_variant.variant_size  = request.POST['variant_size']
#                     product_variant.no_of_pouch  = request.POST['no_of_pouch']
#                     product_variant.container_size  = request.POST['container_size']
#                     product_variant.is_bulk_pack  = request.POST['variant_type']
#                     product_variant.is_allow_in_packaging  = request.POST['is_allow_in_packaging']
#                     product_variant.mrp  = request.POST['mrp']
#                     product_variant.sp_distributor  = request.POST['sp_distributor']
#                     product_variant.sp_superstockist  = request.POST['sp_superstockist']
#                     product_variant.sp_employee  = request.POST['sp_employee']

#                     product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
#                     product_variant.container_sp_distributor  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
#                     product_variant.container_sp_superstockist  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
#                     product_variant.container_sp_employee  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])

#                     product_variant.valid_from = valid_from
#                     product_variant.valid_to = valid_to
#                     product_variant.production_unit_id   = ','.join([str(elem) for elem in request.POST.getlist('production_unit_id[]')]) 
#                     if request.POST['gst']:
#                         product_variant.gst  = request.POST['gst']
#                     product_variant.status  = 1
#                     product_variant.save()

#                     if product_variant.id:
                        
#                         users = SpUsers.objects.raw(''' SELECT id,user_type,is_distributor,is_super_stockist FROM sp_users where 
#                                                     id in (SELECT user_id FROM sp_user_product_variants WHERE product_variant_id=%s)
#                                                     ''', [product_variant.id])
#                         if len(users) :
#                             for user in users :
#                                 user_product_variant = SpUserProductVariants.objects.get(user_id=user.id,product_variant_id=product_variant.id)
#                                 user_product_variant.user_id = user.id
#                                 user_product_variant.product_id = request.POST['product_id']
#                                 user_product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
#                                 user_product_variant.product_variant_id = product_variant.id
#                                 user_product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
#                                 user_product_variant.item_sku_code = request.POST['item_code']
#                                 user_product_variant.variant_quantity = request.POST['variant_qty']
#                                 user_product_variant.variant_unit_id  = request.POST['variant_unit']
#                                 user_product_variant.variant_name  = request.POST['variant_name']
#                                 user_product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
#                                 user_product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
#                                 user_product_variant.variant_size  = request.POST['variant_size']
#                                 user_product_variant.no_of_pouch  = request.POST['no_of_pouch']
#                                 user_product_variant.container_size  = request.POST['container_size']
#                                 user_product_variant.is_bulk_pack  = request.POST['variant_type']
#                                 # user_product_variant.included_in_scheme  = request.POST['included_in_scheme']
#                                 user_product_variant.mrp  = request.POST['mrp']
#                                 user_product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
#                                 # if user.user_type == 1 :
#                                 #     user_product_variant.sp_user  = request.POST['sp_employee']
#                                 #     user_product_variant.container_sp_user  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])
#                                 # else:
#                                 #     if user.is_distributor == 1:
#                                 #         user_product_variant.sp_user = request.POST['sp_distributor']
#                                 #         user_product_variant.container_sp_user  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
#                                 #     else:
#                                 #         user_product_variant.sp_user = request.POST['sp_superstockist']
#                                 #         user_product_variant.container_sp_user  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
                                

#                                 user_product_variant.valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                                 user_product_variant.valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
#                                 user_product_variant.status  = 1
#                                 user_product_variant.save()

#                         if(len(request.FILES.getlist('variantImage[]'))) :
#                             variant_images       = request.FILES.getlist('variantImage[]')
#                             i = 0 
#                             SpProductVariantImages.objects.filter(product_variant_id=request.POST['product_variant_id']).delete()

#                             for variant_image in variant_images:

                                
#                                 folder='media/product_variant_images/' 
#                                 storage = FileSystemStorage(location=folder)
#                                 timestamp = int(time.time())
#                                 variant_image_name = variant_image.name
#                                 temp = variant_image_name.split('.')
#                                 variant_image_name = str(product_variant.id) + "_"+str(timestamp)+"_"+str(i)+"."+temp[(len(temp) - 1)]
                                
#                                 uploaded_variant_image = storage.save(variant_image_name, variant_image)
#                                 product_variant_image = SpProductVariantImages()
#                                 product_variant_image.product_variant_id = product_variant.id
#                                 product_variant_image.image_url = folder+variant_image_name
                                
#                                 # create thumbnail
#                                 image_file = str(settings.MEDIA_ROOT) + '/product_variant_images/'+variant_image_name
#                                 size = 300, 300
#                                 im = Image.open(image_file)

#                                 if im.mode in ("RGBA", "P"):
#                                     im = im.convert("RGB")

#                                 im.thumbnail(size, Image.ANTIALIAS)
#                                 thumbnail_image = str(settings.MEDIA_ROOT) + '/product_variant_images/thumbnail/'+variant_image_name
#                                 im.save(thumbnail_image, "JPEG",quality=100)

#                                 product_variant_image.thumbnail_url = 'media/product_variant_images/thumbnail/'+variant_image_name
#                                 product_variant_image.save()

#                                 i = i+1

#                         #Save Activity
#                         user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
#                         heading     = 'Product variant edited'
#                         activity    = 'Product variant edited by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
#                         saveActivity('Product & Variant Management', 'Edit Product Variant', heading, activity, request.user.id, user_name, 'edit_product.png', '1', 'web.png')

#                         response['flag'] = True
#                         response['message'] = "Record has been saved successfully."
#                     else:
#                         response['flag'] = False
#                         response['message'] = "Failed to save"

#         except Exception as e:
#             response['flag'] = False
#             response['message'] = str(e)
#         return JsonResponse(response)

#     else:
#         template = 'products/edit-product-variant.html'
#         context = {}
#         context['products']     = SpProducts.objects.filter(status=1)
#         context['product_variant'] = product_variant = SpProductVariants.objects.get(id=product_variant_id)
#         context['product_variant_unit']          = SpProductUnits.objects.get(id=product_variant.variant_unit_id)
#         context['product'] = SpProducts.objects.get(id=product_variant.product_id)
#         context['product_units']          = SpProductUnits.objects.filter(status=1)
#         context['color_codes']          = SpColorCodes.objects.filter(status=1)
#         context['product_variant_images'] = SpProductVariantImages.objects.filter(product_variant_id=product_variant_id)
#         context['gst_list']         = SpGst.objects.filter()
#         context['product_containers']     = SpContainers.objects.filter(status=1)
#         context['packaging_types']     = SpPackagingType.objects.filter(status=1)
#         context['production_unit']  = SpProductionUnit.objects.all()

#     return render(request, template,context)

@login_required
@has_par(sub_module_id=17,permission='edit')
def editProductVariant(request,product_variant_id):
    if request.method == "POST":
        response = {}
        product_variant = SpProductVariants.objects.get(id=request.POST['product_variant_id'])
        if (int(request.POST['update_confirm']) == 0) and ((float(request.POST['mrp']) !=  float(product_variant.mrp)) or (float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor)) or (float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist))) :
            response['flag'] = False
            response['confirm'] = True
            response['message'] = "MRP/SP.Distributor/SP.Super Stockist has been changed. Do you want save changes?"
        else:
            if SpProductVariants.objects.filter(item_sku_code=request.POST['item_code']).exclude(id=product_variant.id).exists():
                response['flag'] = False
                response['message'] = request.POST['item_code']+" Item code already exists."
            else:
                valid_from = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
                valid_to = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')

                if (str(valid_from) != str(product_variant.valid_from)) or (str(valid_to) != str(product_variant.valid_to)) or  ((float(request.POST['mrp']) !=  float(product_variant.mrp)) or (float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor)) or (float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist))) :
                        description = ''
                        if (str(valid_from) != str(product_variant.valid_from)) :
                            description += 'From date changed from '+ str(product_variant.valid_from) +' to '+valid_from +'. '
                        if (str(valid_to) != str(product_variant.valid_to)) :
                            description += 'To date changed from '+ str(product_variant.valid_to) +' to '+valid_to +'. '
                        if float(request.POST['mrp']) !=  float(product_variant.mrp) :
                            description += 'MRP changed from '+ str(product_variant.mrp) +' to '+request.POST['mrp'] +'. '
                        if float(request.POST['sp_distributor']) !=  float(product_variant.sp_distributor) :
                            description += 'SP Distributor changed from '+ str(product_variant.sp_distributor) +' to '+request.POST['sp_distributor'] +'. '
                        if float(request.POST['sp_superstockist']) !=  float(product_variant.sp_superstockist) :
                            description += 'SP Super Stockist changed from '+ str(product_variant.sp_superstockist) +' to '+request.POST['sp_superstockist'] +'. '
                        if float(request.POST['sp_employee']) !=  float(product_variant.sp_employee) :
                            description += 'SP Employee changed from '+ str(product_variant.sp_employee) +' to '+request.POST['sp_employee'] +'. '

                        history = SpProductVariantsHistory()
                        current_user = request.user
                        history.user_id  = current_user.id
                        history.user_name  = str(current_user.first_name) + " " + current_user.middle_name+ " " + current_user.last_name
                        history.product_variant_id  = product_variant.id
                        history.mrp  = product_variant.mrp
                        history.sp_distributor  = product_variant.sp_distributor
                        history.sp_superstockist  = product_variant.sp_superstockist
                        history.sp_employee  = product_variant.sp_employee

                        history.container_mrp  = product_variant.container_mrp
                        history.container_sp_distributor  = product_variant.container_sp_distributor
                        history.container_sp_superstockist  = product_variant.container_sp_superstockist
                        history.container_sp_employee  = product_variant.container_sp_employee

                        history.valid_from = product_variant.valid_from
                        history.valid_to = product_variant.valid_to
                        if product_variant.gst:
                            history.gst = product_variant.gst
                        history.description = description
                        history.save()
                    

                product_variant.product_id = request.POST['product_id']
                product_variant.product_name  = getModelColumnById(SpProducts,request.POST['product_id'],'product_name')
                product_variant.product_class_id  = getModelColumnById(SpProducts,request.POST['product_id'],'product_class_id')
                product_variant.item_sku_code = request.POST['item_code']
                product_variant.container_id  = request.POST['container_id']
                product_variant.container_name  = getModelColumnById(SpContainers,request.POST['container_id'],'container')
                product_variant.packaging_type_id  = request.POST['packaging_type_id']
                product_variant.packaging_type_name  = getModelColumnById(SpPackagingType,request.POST['packaging_type_id'],'packaging_type')
                # product_variant.sales_leger  = getModelColumnById(SalesLedger,request.POST['leadger_name'],'leadger_name')
                product_variant.variant_quantity = request.POST['variant_qty']
                product_variant.variant_unit_id  = request.POST['variant_unit']
                product_variant.variant_name  = request.POST['variant_name']
                product_variant.variant_unit_name  = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'unit')
                product_variant.largest_unit_name = getModelColumnById(SpProductUnits,request.POST['variant_unit'],'largest_unit')
                product_variant.variant_size  = request.POST['variant_size']
                product_variant.no_of_pouch  = request.POST['no_of_pouch']
                product_variant.container_size  = request.POST['container_size']
                product_variant.is_bulk_pack  = request.POST['variant_type']
                product_variant.is_allow_in_packaging  = request.POST['is_allow_in_packaging']
                product_variant.mrp  = request.POST['mrp']
                product_variant.sp_distributor  = request.POST['sp_distributor']
                product_variant.sp_superstockist  = request.POST['sp_superstockist']
                product_variant.sp_employee  = request.POST['sp_employee']

                product_variant.container_mrp  = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_distributor  = float(request.POST['sp_distributor']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_superstockist  = float(request.POST['sp_superstockist']) * float(request.POST['no_of_pouch'])
                product_variant.container_sp_employee  = float(request.POST['sp_employee']) * float(request.POST['no_of_pouch'])

                product_variant.valid_from = valid_from
                product_variant.valid_to = valid_to
                product_variant.production_unit_id   = ','.join([str(elem) for elem in request.POST.getlist('production_unit_id[]')]) 
                if request.POST['gst']:
                    product_variant.gst  = request.POST['gst']
                product_variant.status  = 1
                product_variant.save()

                if product_variant.id:
                    user_ids_from_details = SpBasicDetails.objects.filter(production_unit_id__in=request.POST.getlist('production_unit_id[]')).values_list('user_id', flat=True)
                    users                 = SpUsers.objects.filter(id__in=user_ids_from_details,is_distributor=1)
                    users_ids             = [user.id for user in users]
                    SpUserProductVariants.objects.exclude(user_id__in=users_ids).delete()
                    if len(users) :
                        for user in users :
                            # sp_user           = request.POST.get('sp_employee') if user.user_type == 1 else (request.POST.get('sp_distributor') if user.is_distributor == 1 else request.POST.get('sp_superstockist'))
                            # container_sp_user = float(sp_user) * float(request.POST.get('no_of_pouch'))
                            
                            user_product_variant_exists = SpUserProductVariants.objects.filter(user_id=user.id,product_variant_id=product_variant.id).exists()

                            if user_product_variant_exists:
                                # If it exists, get the instance
                                continue;
                                # user_product_variant = SpUserProductVariants.objects.get(user_id=user.id,product_variant_id=product_variant.id)
                            else:
                                # If it doesn't exist, create a new instance
                                user_product_variant                  = SpUserProductVariants()
                            user_product_variant.user_id              = user.id
                            user_product_variant.product_variant_id   = product_variant.id
                            user_product_variant.product_id           = request.POST['product_id']
                            user_product_variant.product_name         = getModelColumnById(SpProducts, request.POST['product_id'], 'product_name')
                            user_product_variant.product_class_id     = getModelColumnById(SpProducts, request.POST['product_id'], 'product_class_id')
                            user_product_variant.item_sku_code        = request.POST['item_code']
                            user_product_variant.variant_quantity     = request.POST['variant_qty']
                            user_product_variant.variant_unit_id      = request.POST['variant_unit']
                            user_product_variant.variant_name         = request.POST['variant_name']
                            user_product_variant.variant_unit_name    = getModelColumnById(SpProductUnits, request.POST['variant_unit'], 'unit')
                            user_product_variant.largest_unit_name    = getModelColumnById(SpProductUnits, request.POST['variant_unit'], 'largest_unit')
                            user_product_variant.variant_size         = request.POST['variant_size']
                            user_product_variant.no_of_pouch          = request.POST['no_of_pouch']
                            user_product_variant.container_size       = request.POST['container_size']
                            user_product_variant.is_bulk_pack         = request.POST['variant_type']
                            user_product_variant.mrp                  = request.POST['mrp']
                            user_product_variant.container_mrp        = float(request.POST['mrp']) * float(request.POST['no_of_pouch'])
                            user_product_variant.valid_from           = datetime.strptime(request.POST['valid_from'], '%d/%m/%Y').strftime('%Y-%m-%d')
                            user_product_variant.valid_to             = datetime.strptime(request.POST['valid_to'], '%d/%m/%Y').strftime('%Y-%m-%d')
                            user_product_variant.status               = 1
                            # user_product_variant.sp_user              = sp_user
                            # user_product_variant.container_sp_user    = container_sp_user
                            user_product_variant.save()
                    if(len(request.FILES.getlist('variantImage[]'))) :
                        variant_images       = request.FILES.getlist('variantImage[]')
                        i = 0 
                        SpProductVariantImages.objects.filter(product_variant_id=request.POST['product_variant_id']).delete()

                        for variant_image in variant_images:

                            
                            folder='media/product_variant_images/' 
                            storage = FileSystemStorage(location=folder)
                            timestamp = int(time.time())
                            variant_image_name = variant_image.name
                            temp = variant_image_name.split('.')
                            variant_image_name = str(product_variant.id) + "_"+str(timestamp)+"_"+str(i)+"."+temp[(len(temp) - 1)]
                            
                            uploaded_variant_image = storage.save(variant_image_name, variant_image)
                            product_variant_image = SpProductVariantImages()
                            product_variant_image.product_variant_id = product_variant.id
                            product_variant_image.image_url = folder+variant_image_name
                            
                            # create thumbnail
                            image_file = str(settings.MEDIA_ROOT) + '/product_variant_images/'+variant_image_name
                            size = 300, 300
                            im = Image.open(image_file)

                            if im.mode in ("RGBA", "P"):
                                im = im.convert("RGB")

                            im.thumbnail(size, Image.ANTIALIAS)
                            thumbnail_image = str(settings.MEDIA_ROOT) + '/product_variant_images/thumbnail/'+variant_image_name
                            im.save(thumbnail_image, "JPEG",quality=100)

                            product_variant_image.thumbnail_url = 'media/product_variant_images/thumbnail/'+variant_image_name
                            product_variant_image.save()

                            i = i+1

                    #Save Activity
                    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                    heading     = 'Product variant edited'
                    activity    = 'Product variant edited by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                    saveActivity('Product & Variant Management', 'Edit Product Variant', heading, activity, request.user.id, user_name, 'edit_product.png', '1', 'web.png')

                    response['flag'] = True
                    response['message'] = "Record has been saved successfully."
                else:
                    response['flag'] = False
                    response['message'] = "Failed to save"

        # except Exception as e:
        #     response['flag'] = False
        #     response['message'] = str(e)
        return JsonResponse(response)

    else:
        template = 'products/edit-product-variant.html'
        context = {}
        context['products']     = SpProducts.objects.filter(status=1)
        context['product_variant'] = product_variant = SpProductVariants.objects.get(id=product_variant_id)
        context['product_variant_unit']          = SpProductUnits.objects.get(id=product_variant.variant_unit_id)
        context['product'] = SpProducts.objects.get(id=product_variant.product_id)
        context['product_units']          = SpProductUnits.objects.filter(status=1)
        context['color_codes']          = SpColorCodes.objects.filter(status=1)
        context['product_variant_images'] = SpProductVariantImages.objects.filter(product_variant_id=product_variant_id)
        context['gst_list']         = SpGst.objects.filter()
        context['product_containers']     = SpContainers.objects.filter(status=1)
        context['packaging_types']     = SpPackagingType.objects.filter(status=1)
        context['production_unit']  = SpProductionUnit.objects.all()
        context['sales_ledger']     = SalesLedger.objects.all().distinct()

    return render(request, template,context)



@login_required
def productUnitDetails(request,unit_id):
    response = {}
    if SpProductUnits.objects.filter(id=unit_id).exists():
        response['flag'] = True
        response['product_unit'] = model_to_dict(SpProductUnits.objects.get(id=unit_id))
    else:
        response['flag'] = False
        response['flag'] = "Unit not found"

    return JsonResponse(response)

@login_required
def productDetails(request,product_id):
    response = {}
    if SpProducts.objects.filter(id=product_id).exists():
        response['flag'] = True
        response['product'] = model_to_dict(SpProducts.objects.get(id=product_id))
    else:
        response['flag'] = False
        response['flag'] = "Product not found"

    return JsonResponse(response)




@login_required
@has_par(sub_module_id=17,permission='delete')
def updateProductStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpProducts.objects.get(id=id)
            data.status = is_active
            data.save()
            
            SpProductVariants.objects.filter(product_id=id).update(status=is_active)
            SpUserProductVariants.objects.filter(product_id=id).update(status=is_active)

            #Save Activity
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Product status changed'
            activity    = 'Product status changed by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Product & Variant Management', 'Edit Product', heading, activity, request.user.id, user_name, 'edit_product.png', '1', 'web.png')

            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/products')



@login_required
@has_par(sub_module_id=17,permission='delete')
def updateProductVariantStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpProductVariants.objects.get(id=id)
            data.status = is_active
            data.save()
            
            SpUserProductVariants.objects.filter(product_variant_id=id).update(status=is_active)
            
            #Save Activity
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Product variant status changed'
            activity    = 'Product variant status changed by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Product & Variant Management', 'Product Variant', heading, activity, request.user.id, user_name, 'edit_product.png', '1', 'web.png')

            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/products')

