import json
import time,timeago
import calendar
import pytz
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK
)
from rest_framework.response import Response
from ...models import *
from django.forms.models import model_to_dict
from django.core import serializers
from utils import *
from datetime import datetime, date
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password
from django.db.models import Q
import re

baseurl = settings.BASE_URL

#get product list
@csrf_exempt
@api_view(["POST"])
def productList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    product_list            = SpProducts.objects.filter(status=1).values('id', 'product_name', 'product_class_name').order_by('product_name')
    
    
    try:
        user_outstanding_amount = SpBasicDetails.objects.get(status=1, user_id=request.data.get("user_id"))
        outstanding_amount      = user_outstanding_amount.outstanding_amount
    except SpBasicDetails.DoesNotExist:
        outstanding_amount = None

    context = {}
    context['product_list']             = product_list
    context['shift_list']               = SpWorkingShifts.objects.filter(status=1).values('id', 'working_shift').order_by('-working_shift')
    context['user_outstanding_amount']  = outstanding_amount
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)   

#get product variant list
@csrf_exempt
@api_view(["POST"])
def productVariantList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("product_id") is None or request.data.get("product_id") == '':
        return Response({'message': 'Product Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    product_variant_list = SpUserProductVariants.objects.filter(product_id=int(request.data.get("product_id")), user_id=request.data.get("user_id"), status=1).extra(select={'rate': 'container_sp_user'}).values('product_variant_id', 'product_id','product_class_id' ,'item_sku_code', 'variant_quantity', 'variant_unit_id', 'variant_unit_name', 'variant_name', 'variant_size', 'no_of_pouch', 'sp_user', 'largest_unit_name', 'is_bulk_pack', 'included_in_scheme', 'container_size', 'rate', 'valid_from', 'valid_to', 'container_sp_user').order_by('variant_name')
    for product_variant in product_variant_list:
        product_variant['id'] = getModelColumnById(SpProductVariants, product_variant['product_variant_id'], 'id')

    context = {}
    context['product_variant_list']     = product_variant_list
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

#get product variant list
@csrf_exempt
@api_view(["POST"])
def productVariantLists(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
   
    product_classes = SpProductClass.objects.filter(status=1).values('id', 'product_class', 'product_hsn').order_by('order_of')
    for product_class in product_classes:
        product_class['products'] = SpProducts.objects.filter(status=1, product_class_id=product_class['id']).values('id', 'product_name').order_by('order_of')
        product_class_variants_data = []
        for product in product_class['products']:
            condition = ''
            if request.data.get("search"):
                search_keyword = str(request.data.get("search")).split()
                if len(search_keyword) == 1:
                    condition += " and sp_user_product_variants.variant_name LIKE '%%"+str(request.data.get("search"))+"%%'"
                else:
                    condition += " and sp_user_product_variants.variant_name LIKE '"+str(request.data.get("search"))+"%%'"

            condition += " and sp_user_product_variants.product_id = %s" % int(product['id'])
            condition += " and sp_user_product_variants.user_id = %s" % request.data.get("user_id")
            condition += " and sp_user_product_variants.status = %s" % 1     
            product_variants    = SpUserProductVariants.objects.raw(''' SELECT sp_user_product_variants.id, sp_user_product_variants.product_variant_id, sp_user_product_variants.product_id, sp_user_product_variants.product_class_id , sp_user_product_variants.item_sku_code, sp_user_product_variants.variant_quantity, sp_user_product_variants.variant_unit_id, sp_user_product_variants.variant_unit_name, sp_user_product_variants.variant_name, sp_user_product_variants.variant_size, sp_user_product_variants.no_of_pouch, sp_user_product_variants.sp_user, sp_user_product_variants.largest_unit_name, sp_user_product_variants.is_bulk_pack, sp_user_product_variants.included_in_scheme, sp_user_product_variants.container_size, sp_user_product_variants.valid_from, sp_user_product_variants.valid_to, sp_user_product_variants.container_sp_user FROM sp_user_product_variants left join sp_product_variants on sp_product_variants.id = sp_user_product_variants.product_variant_id WHERE 1 {condition} order by sp_product_variants.order_of asc '''.format(condition=condition))
            
            product_variants_data = []
            for product_variant in product_variants:
                variants = {}
                product_variant.id = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'id')
                if SpProductVariantImages.objects.filter(product_variant_id = product_variant.id).exists():
                    variant_image = SpProductVariantImages.objects.filter(product_variant_id = product_variant.id).first()
                    if variant_image.image_url:
                        img = baseurl+'/'+str(variant_image.thumbnail_url)
                        product_variant.variant_image   = str(img)
                    else:
                        product_variant.variant_image = ''
                else:
                    product_variant.variant_image = ''

                variants['id']                     = product_variant.id
                variants['variant_image']          = product_variant.variant_image
                variants['rate']                   = product_variant.container_sp_user
                variants['product_variant_id']     = product_variant.product_variant_id 
                variants['product_id']             = product_variant.product_id 
                variants['container_id']           = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'container_id') 
                variants['container_name']         = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'container_name')
                variants['packaging_type_id']      = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'packaging_type_id')
                variants['packaging_type_name']    = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'packaging_type_name')
                variants['product_class_id']       = product_variant.product_class_id 
                variants['item_sku_code']          = product_variant.item_sku_code 
                variants['variant_quantity']       = product_variant.variant_quantity 
                variants['variant_unit_id']        = product_variant.variant_unit_id
                variants['variant_unit_name']      = product_variant.variant_unit_name 
                variants['variant_name']           = product_variant.variant_name 
                variants['variant_size']           = product_variant.variant_size 
                variants['no_of_pouch']            = product_variant.no_of_pouch 
                variants['sp_user']                = product_variant.sp_user 
                variants['largest_unit_name']      = product_variant.largest_unit_name 
                variants['is_bulk_pack']           = product_variant.is_bulk_pack 
                variants['included_in_scheme']     = product_variant.included_in_scheme 
                variants['is_allow_in_packaging'] = getModelColumnById(SpProductVariants, product_variant.product_variant_id, 'is_allow_in_packaging')	 
                variants['container_size']         = product_variant.container_size 
                variants['valid_from']             = product_variant.valid_from 
                variants['valid_to']               = product_variant.valid_to 
                variants['container_sp_user']      = product_variant.container_sp_user    
                product_variants_data.append(variants)
                product_class_variants_data.append(variants)
            product['product_variants']    =  product_variants_data
            product['products_count']      =  len(product_variants_data)
        product_class['products_count'] = len(product_class_variants_data)           
    try:
        user_outstanding_amount = SpBasicDetails.objects.get(status=1, user_id=request.data.get("user_id"))
        outstanding_amount      = user_outstanding_amount.outstanding_amount
    except SpBasicDetails.DoesNotExist:
        outstanding_amount = None
        
    context = {}
    context['product_variant_list']     = product_classes
    context['order_time_slots']         = SpTimeSlots.objects.filter(status=1).values('id', 'start_timing', 'end_timing', 'timing_order').order_by('start_timing')
    context['shift_list']               = SpWorkingShifts.objects.filter(status=1).values('id', 'working_shift').order_by('-working_shift')
    context['user_outstanding_amount']  = outstanding_amount
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 
    
#save order and order details
@csrf_exempt
@api_view(["POST"])
def saveOrder(request):
    today  = date.today()
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_details") is None or request.data.get("order_details") == '':
        return Response({'message': 'Order Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_item_list") is None or request.data.get("order_item_list") == '':
        return Response({'message': 'Order Item Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("mode_of_payment") is None or request.data.get("mode_of_payment") == '':
        return Response({'message': 'Mode of Payment field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("amount_to_be_paid") is None or request.data.get("amount_to_be_paid") == '':
        return Response({'message': 'Amount field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__icontains=today.strftime("%Y-%m-%d")).exists():
        return Response({'message': 'Order already generated', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    order_details   = request.data.get('order_details')
    order_item_list = request.data.get('order_item_list')
    free_scheme_list = request.data.get('free_scheme')
    flat_schemes = request.data.get('flat_scheme')
    bulk_scheme = request.data.get('bulk_scheme')
    quantitative_scheme = request.data.get('quantitative_scheme')

    

    #update user outstanding Amount
    user                        = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    #user.outstanding_amount     = order_details['remaining_outstanding_amount']
    #user.save()
    
    if SpOrders.objects.count() == 0:
        last_order_id = 1
    else:
        last_order_id = SpOrders.objects.order_by('-id').first()
        last_order_id = last_order_id.id+1 

    user_area_details = SpUserAreaAllocations.objects.get(user_id=request.data.get("user_id"))
    
    if user_area_details.route_id:
        transporter_details = SpVehicles.objects.filter(route_id=user_area_details.route_id).order_by('-id').first()    
        if transporter_details:
            transporter_name = ''
            if transporter_details.owner_name:
                transporter_name += transporter_details.owner_name
            if transporter_details.owner_address:
                transporter_name += ', '+str(transporter_details.owner_address)
            transporter_description = ''
            if transporter_details.driver_name:
                transporter_description += 'Driver Name: '+str(transporter_details.driver_name)
            vehicle_no = ''
            if transporter_details.registration_number:
                vehicle_no += transporter_details.registration_number            
        else:
            transporter_name = ''
            transporter_description = ''
            vehicle_no = ''

    else:
        transporter_name = ''
        transporter_description = ''
        vehicle_no = ''
        
    #save order
    order                       = SpOrders()
    order.order_code            =  getConfigurationResult('org_code')+str(last_order_id)
    order.user_id               =  request.data.get("user_id")
    order.user_sap_id           =  getModelColumnById(SpUsers, request.data.get("user_id"), 'emp_sap_id')
    order.user_name             =  getModelColumnById(SpUsers, request.data.get("user_id"), 'first_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'middle_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'last_name')
    order.user_type             =  getUserRole(request.data.get("user_id"))
    order.route_id              =  user_area_details.route_id
    order.route_name            =  user_area_details.route_name
    order.transporter_name      =  transporter_name
    order.transporter_details   =  transporter_description
    order.vehicle_no            =  vehicle_no
    order.town_id               =  user_area_details.town_id
    order.town_name             =  user_area_details.town_name
    order.mode_of_payment       =  request.data.get("mode_of_payment")
    order.amount_to_be_paid     =  request.data.get("amount_to_be_paid")
    order.order_date            =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order.updated_date          =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order.order_status          =  1
    order.order_shift_id        =  order_details['shift_id']
    order.order_shift_name      =  order_details['shift_name']
    if order_details['scheme_id'] is not None and order_details['scheme_id']!= '':
        order.order_scheme_id   =  order_details['scheme_id']
    order.order_total_amount    =  order_details['total_order_amount']
    order.order_items_count     =  order_details['items_count']
    order.outstanding_amount    =  user.outstanding_amount
    production_unit_id          =  getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'production_unit_id')
    order.production_unit_id    =  production_unit_id
    order.production_unit_name  =  getModelColumnById(SpProductionUnit, production_unit_id, 'production_unit_name')
    if getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'tcs_applicable') == 1:
        order.tcs_value      =  getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'tcs_value')
    order.save()

    #save order item details
    for order_item in order_item_list:
        if order_item['packaging_type'] == '0':
            pouch_quantity     = int(order_item['qty'])*int(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'no_of_pouch'))
            quantity_in_ltr    = float(pouch_quantity)*float(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'variant_size'))
        else:
            pouch_quantity     = int(order_item['qty'])
            quantity_in_ltr    =  float(order_item['qty'])*float(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'variant_size'))
            
        item                            = SpOrderDetails()
        item.user_id                    = request.data.get("user_id")
        item.order_id                   = order.id
        item.product_id                 = order_item['product_id']
        item.product_name               = order_item['product_name']
        item.product_variant_id         = order_item['product_variant_id']
        item.product_variant_name       = order_item['product_variant_name']
        item.product_variant_size       = order_item['product_variant_size']
        item.product_no_of_pouch        = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'no_of_pouch')
        item.product_container_size     = order_item['product_container_size']
        item.product_container_type     = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'container_name')
        item.quantity_in_pouch          = pouch_quantity
        item.quantity_in_ltr            = round(quantity_in_ltr,2)
        item.quantity                   = order_item['qty']
        item.rate                       = order_item['rate']
        item.amount                     = order_item['amount']
        item.packaging_type             = order_item['packaging_type']
        item.gst                        = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'gst')
        item.product_packaging_type_name= getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'packaging_type_name')
        item.is_allow                   = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'is_allow_in_packaging')
        item.order_date                 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'New Order('+order.order_code+') has been initiated'
    activity    = 'New Order('+order.order_code+') has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    
    
    if len(free_scheme_list):
        for free_scheme in free_scheme_list:
            order_scheme                    = SpOrderSchemes()
            order_scheme.order_id           = order.id
            order_scheme.user_id            = request.data.get("user_id")
            order_scheme.scheme_id          = free_scheme['scheme_id']
            order_scheme.scheme_type        = "free"
            order_scheme.variant_id         = free_scheme['variant_id']
            order_scheme.on_order_of        = free_scheme['on_order_of']
            order_scheme.free_variant_id = free_scheme['free_variant_id']
            if 'free_variant_container_type' in free_scheme:
                order_scheme.free_variant_container_type = free_scheme['free_variant_container_type']
            order_scheme.container_quantity = free_scheme['free_container_quantity']
            order_scheme.free_variant_packaging_type = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'packaging_type_name')
            order_scheme.free_variant_container_size = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'container_size')
            order_scheme.pouch_quantity     = free_scheme['free_pouch_quantity']
            order_scheme.quantity_in_ltr    = int(free_scheme['free_pouch_quantity'])*float(getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'variant_size'))
            order_scheme.product_id         = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'product_id')
            order_scheme.product_class_id   = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'product_class_id')
            order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order_scheme.save()
        
    if len(quantitative_scheme):
        order_scheme                        = SpOrderSchemes()
        order_scheme.order_id               = order.id
        order_scheme.user_id                = request.data.get("user_id")
        order_scheme.scheme_id              = quantitative_scheme['scheme_id']
        order_scheme.scheme_type            = "quantitative"
        order_scheme.free_variant_id = quantitative_scheme['free_variant_id']
        if 'free_variant_container_type' in quantitative_scheme:
            order_scheme.free_variant_container_type = quantitative_scheme['free_variant_container_type']
        order_scheme.container_quantity     = quantitative_scheme['free_container_quantity']
        order_scheme.pouch_quantity         = quantitative_scheme['free_pouch_quantity']
        order_scheme.quantity_in_ltr        = int(quantitative_scheme['free_pouch_quantity'])*float(getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'variant_size'))
        order_scheme.product_id             = getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'product_id')
        order_scheme.product_class_id       = getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'product_class_id')
        order_scheme.created_at             = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_scheme.save()
        
    if len(flat_schemes):
        for flat_scheme in flat_schemes:
            order_scheme                    = SpOrderSchemes()
            order_scheme.order_id           = order.id
            order_scheme.user_id            = request.data.get("user_id")
            order_scheme.scheme_id          = int(flat_scheme['scheme_id'])
            order_scheme.scheme_type        = "flat"
            order_scheme.incentive_amount   = flat_scheme['incentive_amount']
            order_scheme.variant_id         = flat_scheme['applied_on_variant_id']
            order_scheme.quantity_in_ltr    = flat_scheme['quantity_in_ltr']
            order_scheme.product_id         = getModelColumnById(SpProductVariants,flat_scheme['applied_on_variant_id'],'product_id')
            order_scheme.product_class_id   = getModelColumnById(SpProductVariants,flat_scheme['applied_on_variant_id'],'product_class_id')
            order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order_scheme.save()

    if len(bulk_scheme):
        order_scheme                    = SpOrderSchemes()
        order_scheme.order_id           = order.id
        order_scheme.user_id            = request.data.get("user_id")
        order_scheme.scheme_id          = bulk_scheme['scheme_id']
        order_scheme.scheme_type        = "bulkpack"
        order_scheme.incentive_amount   = bulk_scheme['incentive_amount']
        order_scheme.unit_id            = bulk_scheme['unit_id']
        order_scheme.unit_name          = bulk_scheme['unit_name']
        order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_scheme.save()


    saveActivity('Order Management', 'Order Summary', heading, activity, request.user.id, user_name, 'Orderplaced.png', '2', 'app.png')
    sendNotificationToUsers(order.id, order.order_code, 'add', 8, request.user.id, user_name, 'SpOrders', request.user.role_id)

    context = {}
    context['message']                  = 'Order has been saved successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#update order and order details
@csrf_exempt
@api_view(["POST"])
def updateOrder(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_details") is None or request.data.get("order_details") == '':
        return Response({'message': 'Order Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_item_list") is None or request.data.get("order_item_list") == '':
        return Response({'message': 'Order Item Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("order_id") is None or request.data.get("order_id") == '':
        return Response({'message': 'Order Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("mode_of_payment") is None or request.data.get("mode_of_payment") == '':
        return Response({'message': 'Mode of Payment field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("amount_to_be_paid") is None or request.data.get("amount_to_be_paid") == '':
        return Response({'message': 'Amount field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 


    order_details   = request.data.get('order_details')
    order_item_list = request.data.get('order_item_list')
    free_scheme_list = request.data.get('free_scheme')
    flat_schemes = request.data.get('flat_scheme')
    bulk_scheme = request.data.get('bulk_scheme')
    quantitative_scheme = request.data.get('quantitative_scheme')

    previous_order_list = SpOrderDetails.objects.filter(order_id=request.data.get("order_id")).values_list('id', flat=True)
    
    current_order_item_list = []
    for order_item in order_item_list:
        if "id" in order_item:
            current_order_item_list.append(int(order_item['id']))

    order_item_id = []
    for id, val in enumerate(previous_order_list):
        if val not in current_order_item_list:
            order_item_id.append(val)    

    #update user outstanding Amount
    user                        = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    #user.outstanding_amount     = order_details['remaining_outstanding_amount']
    #user.save()
    
    user_area_details = SpUserAreaAllocations.objects.get(user_id=request.data.get("user_id"))
    if user_area_details.route_id:
        transporter_details = SpVehicles.objects.filter(route_id=user_area_details.route_id).order_by('-id').first()    
        if transporter_details:
            transporter_name = ''
            if transporter_details.owner_name:
                transporter_name += transporter_details.owner_name
            if transporter_details.owner_address:
                transporter_name += ', '+str(transporter_details.owner_address)
            transporter_description = ''
            if transporter_details.driver_name:
                transporter_description += 'Driver Name: '+str(transporter_details.driver_name)
            vehicle_no = ''
            if transporter_details.registration_number:
                vehicle_no += transporter_details.registration_number            
        else:
            transporter_name = ''
            transporter_description = ''
            vehicle_no = ''

    else:
        transporter_name = ''
        transporter_description = ''
        vehicle_no = ''
        
    if SpRoleWorkflowPermissions.objects.filter(permission_slug='edit', sub_module_id=8).exists():
        user_wf_level = SpRoleWorkflowPermissions.objects.filter(permission_slug='edit', sub_module_id=8).values('level_id').distinct().count()
        if user_wf_level == 1:
            order_status = 3
        elif user_wf_level == 2:
            order_status = 2
        else:
            order_status = 1       
    else:
        order_status = 1
        
    #save order
    order                       =  SpOrders.objects.get(id=request.data.get("order_id"))
    order.user_id               =  request.data.get("user_id")
    order.user_sap_id           =  getModelColumnById(SpUsers, request.data.get("user_id"), 'emp_sap_id')
    order.user_name             =  getModelColumnById(SpUsers, request.data.get("user_id"), 'first_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'middle_name')+' '+getModelColumnById(SpUsers, request.data.get("user_id"), 'last_name')
    order.user_type             =  getUserRole(request.data.get("user_id"))
    order.route_id              =  user_area_details.route_id
    order.route_name            =  user_area_details.route_name
    order.transporter_name      =  transporter_name
    order.transporter_details   =  transporter_description
    order.vehicle_no            =  vehicle_no
    order.town_id               =  user_area_details.town_id
    order.town_name             =  user_area_details.town_name
    order.mode_of_payment       =  request.data.get("mode_of_payment")
    order.amount_to_be_paid     =  request.data.get("amount_to_be_paid")
    order.updated_date          =  datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    order.order_status          =  order_status
    order.indent_status         =  0
    order.order_shift_id        =  order_details['shift_id']
    order.order_shift_name      =  order_details['shift_name']
    if order_details['scheme_id'] is not None and order_details['scheme_id']!= '':
        order.order_scheme_id   =  order_details['scheme_id']
    order.order_total_amount    =  order_details['total_order_amount']
    order.order_items_count     =  order_details['items_count']
    order.outstanding_amount    =  user.outstanding_amount
    production_unit_id          =  getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'production_unit_id')
    order.production_unit_id    =  production_unit_id
    order.production_unit_name  =  getModelColumnById(SpProductionUnit, production_unit_id, 'production_unit_name')
    if getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'tcs_applicable') == 1:
        order.tcs_value      =  getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'tcs_value')
    order.save()

    #save order item details
    for order_item in order_item_list:
        if order_item['packaging_type'] == '0':
            pouch_quantity     = int(order_item['qty'])*int(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'no_of_pouch'))
            quantity_in_ltr    = float(pouch_quantity)*float(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'variant_size'))
        else:
            pouch_quantity     = int(order_item['qty'])
            quantity_in_ltr    =  float(order_item['qty'])*float(getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'variant_size'))
            
        if "id" in order_item and int(order_item['id']) in previous_order_list :
            item                            = SpOrderDetails.objects.get(id=int(order_item['id']))
        else:
            item                            = SpOrderDetails()    
        item.user_id                    = request.data.get("user_id")
        item.order_id                   = request.data.get("order_id")
        item.product_id                 = order_item['product_id']
        item.product_name               = order_item['product_name']
        item.product_variant_id         = order_item['product_variant_id']
        item.product_variant_name       = order_item['product_variant_name']
        item.product_variant_size       = order_item['product_variant_size']
        item.product_no_of_pouch        = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'no_of_pouch')
        item.product_container_size     = order_item['product_container_size']
        item.product_container_type     = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'container_name')
        item.quantity_in_pouch          = pouch_quantity
        item.quantity_in_ltr            = round(quantity_in_ltr,2)
        item.quantity                   = order_item['qty']
        item.rate                       = order_item['rate']
        item.amount                     = order_item['amount']
        item.packaging_type             = order_item['packaging_type']
        item.gst                        = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'gst')
        item.product_packaging_type_name= getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'packaging_type_name')
        item.is_allow                   = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'is_allow_in_packaging')
        item.order_date                 = datetime.now().strftime('%Y-%m-%d %H:%M:%S')    
        item.save()

    #delete order items
    for order_item in order_item_id:
        SpOrderDetails.objects.filter(id=order_item).delete()

    SpOrderSchemes.objects.filter(order_id=request.data.get("order_id")).delete()
    if len(free_scheme_list):
        for free_scheme in free_scheme_list:
            order_scheme                    = SpOrderSchemes()
            order_scheme.order_id           = order.id
            order_scheme.user_id            = request.data.get("user_id")
            order_scheme.scheme_id          = free_scheme['scheme_id']
            order_scheme.scheme_type        = "free"
            order_scheme.variant_id         = free_scheme['variant_id']
            order_scheme.on_order_of        = free_scheme['on_order_of']
            order_scheme.free_variant_id = free_scheme['free_variant_id']
            if 'free_variant_container_type' in free_scheme:
                order_scheme.free_variant_container_type = free_scheme['free_variant_container_type']
            order_scheme.container_quantity = free_scheme['free_container_quantity']
            order_scheme.free_variant_packaging_type = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'packaging_type_name')
            order_scheme.free_variant_container_size = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'container_size')
            order_scheme.pouch_quantity     = free_scheme['free_pouch_quantity']
            order_scheme.quantity_in_ltr    = int(free_scheme['free_pouch_quantity'])*float(getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'variant_size'))
            order_scheme.product_id         = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'product_id')
            order_scheme.product_class_id   = getModelColumnById(SpProductVariants,free_scheme['free_variant_id'],'product_class_id')
            order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order_scheme.save()
        
    if len(quantitative_scheme):
        order_scheme                        = SpOrderSchemes()
        order_scheme.order_id               = order.id
        order_scheme.user_id                = request.data.get("user_id")
        order_scheme.scheme_id              = quantitative_scheme['scheme_id']
        order_scheme.scheme_type            = "quantitative"
        order_scheme.free_variant_id = quantitative_scheme['free_variant_id']
        if 'free_variant_container_type' in quantitative_scheme:
            order_scheme.free_variant_container_type = quantitative_scheme['free_variant_container_type']
        order_scheme.container_quantity     = quantitative_scheme['free_container_quantity']
        order_scheme.pouch_quantity         = quantitative_scheme['free_pouch_quantity']
        order_scheme.quantity_in_ltr        = int(quantitative_scheme['free_pouch_quantity'])*float(getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'variant_size'))
        order_scheme.product_id             = getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'product_id')
        order_scheme.product_class_id       = getModelColumnById(SpProductVariants,quantitative_scheme['free_variant_id'],'product_class_id')
        order_scheme.created_at             = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_scheme.save()
        
    if len(flat_schemes):
        for flat_scheme in flat_schemes:
            order_scheme                    = SpOrderSchemes()
            order_scheme.order_id           = order.id
            order_scheme.user_id            = request.data.get("user_id")
            order_scheme.scheme_id          = flat_scheme['scheme_id']
            order_scheme.scheme_type        = "flat"
            order_scheme.incentive_amount   = flat_scheme['incentive_amount']
            order_scheme.variant_id         = flat_scheme['applied_on_variant_id']
            order_scheme.quantity_in_ltr    = flat_scheme['quantity_in_ltr']
            order_scheme.product_id         = getModelColumnById(SpProductVariants,flat_scheme['applied_on_variant_id'],'product_id')
            order_scheme.product_class_id   = getModelColumnById(SpProductVariants,flat_scheme['applied_on_variant_id'],'product_class_id')
            order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            order_scheme.save()

    if len(bulk_scheme):
        order_scheme                    = SpOrderSchemes()
        order_scheme.order_id           = order.id
        order_scheme.user_id            = request.data.get("user_id")
        order_scheme.scheme_id          = bulk_scheme['scheme_id']
        order_scheme.scheme_type        = "bulkpack"
        order_scheme.incentive_amount   = bulk_scheme['incentive_amount']
        order_scheme.unit_id            = bulk_scheme['unit_id']
        order_scheme.unit_name          = bulk_scheme['unit_name']
        order_scheme.created_at         = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        order_scheme.save()
    
    SpApprovalStatus.objects.filter(row_id=order.id).update(status=0)
    
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Order('+order.order_code+') has been updated'
    activity    = 'Order('+order.order_code+') has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Order Management', 'Order Summary', heading, activity, request.user.id, user_name, 'Orderplaced.png', '2', 'app.png')
    context = {}
    context['message']                  = 'Order has been updated successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)    

def getFreeSchemes(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free = 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')+''
        if free_scheme.container_quantity>0:
            product_id             = getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'product_id')
            free += str(free_scheme.container_quantity)+' free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'container_name')+''
        if free_scheme.container_quantity>0:
            free += ' and '     
        if free_scheme.pouch_quantity>0:
            if free_scheme.pouch_quantity == 1:
                free += ' '+str(free_scheme.pouch_quantity)+' free '+str(free_scheme.free_variant_packaging_type)+'.'
            else:    
                free += ' '+str(free_scheme.pouch_quantity)+' free '+str(free_scheme.free_variant_packaging_type)+'.'
              
        free_scheme = free
    else:
        free_scheme = None  
    return free_scheme


def getQuantitativeScheme(order_id, user_id):
    try:
        quantitative_scheme = SpOrderSchemes.objects.get(order_id=order_id, scheme_type='quantitative', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        quantitative_scheme = None
    if quantitative_scheme:
        free = 'Free '+getModelColumnById(SpProductVariants, quantitative_scheme.free_variant_id, 'variant_name')+'-'
        if quantitative_scheme.container_quantity>0:
            product_id             = getModelColumnById(SpProductVariants, quantitative_scheme.free_variant_id, 'product_id')
            free += str(quantitative_scheme.container_quantity)+' free '+getModelColumnById(SpProductVariants, quantitative_scheme.free_variant_id, 'container_name')+''
        if quantitative_scheme.pouch_quantity>0:
            free += ' and '+str(quantitative_scheme.pouch_quantity)+' free Pouches'
        free += ' under the '+getModelColumnById(SpSchemes, quantitative_scheme.scheme_id, 'name')+' Scheme.'      
        quantitative_scheme = free
    else:
        quantitative_scheme = None  
    return quantitative_scheme

def getFlatScheme(product_variant_id, order_id, user_id):
    try:
        flat_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='flat', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        flat_scheme = None
    if flat_scheme:
        flat = 'Discount of Rs. '+str(flat_scheme.incentive_amount)+' applied.'
        flat_scheme = flat
    else:
        flat_scheme = None  
    return flat_scheme   

def getBulkpackScheme(order_id, user_id):
    try:
        bulk_pack_scheme = SpOrderSchemes.objects.get(order_id=order_id, scheme_type='bulkpack', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        bulk_pack_scheme = None
    if bulk_pack_scheme:
        free = ''
        free += str(bulk_pack_scheme.incentive_amount)+' Incentive amount has been applied under the '+getModelColumnById(SpBulkpackSchemes, bulk_pack_scheme.scheme_id, 'name')+' Scheme'      
        bulk_pack_scheme = free
    else:
        bulk_pack_scheme = None  
    return bulk_pack_scheme

#get order details
@csrf_exempt
@api_view(["POST"])
def orderDetails(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if request.data.get("order_id") is None or request.data.get("order_id") == '':
        today   = date.today()
        try:
            order_details               = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__icontains=today.strftime("%Y-%m-%d")).order_by('-id').first()
        except SpOrders.DoesNotExist:
            order_details = None
        if order_details:
            order_date                  = str(order_details.order_date).replace('+00:00', '')
            order_details.order_date    = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')    
        else:
            order_details               = []
    else:
        order = SpOrders.objects.filter(id=request.data.get("order_id")).exists()
        if not  order:
            return Response({'message': 'Order id not exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        order_details               = SpOrders.objects.filter(id=request.data.get("order_id")).order_by('-id').first()
        order_date                  = str(order_details.order_date).replace('+00:00', '')
        order_details.order_date    = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')

    if order_details:
        order_item_list               = SpOrderDetails.objects.filter(order_id=order_details.id).values('id', 'order_id', 'product_id', 'product_name', 'product_variant_id', 'product_variant_name', 'quantity', 'rate', 'amount', 'order_date', 'packaging_type', 'product_packaging_type_name')
        
        bulk_scheme                   = getBulkpackScheme(order_details.id, request.data.get("user_id"))
        quantitative_scheme           = getQuantitativeScheme(order_details.id, request.data.get("user_id"))  
        for order_item in order_item_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            container_name                      = SpProducts.objects.get(id=order_item['product_id'])
            order_item['container_name']        = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'container_name')
            order_item['product_class_name']    = container_name.product_class_name
            order_item['unit_name']             = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'largest_unit_name')
            order_item['order_date']            = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
            order_item['free_scheme']           = getFreeSchemes(order_item['product_variant_id'], order_item['order_id'], request.data.get("user_id"))
            order_item['flat_scheme']           = getFlatScheme(order_item['product_variant_id'], order_item['order_id'], request.data.get("user_id"))
    else:
        order_item_list       = []
        free_scheme_list      = []
        flat_scheme           = []
        bulk_scheme           = []
        quantitative_scheme   = []
    try:
        user_details            = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
        order_timing            = user_details.order_timing
        outstanding_amount      = user_details.outstanding_amount
        opening_crates          = user_details.opening_crates
    except SpBasicDetails.DoesNotExist:
        order_timing = getConfigurationResult('order_timing')
        outstanding_amount      = 0
        opening_crates          = 0

    context = {}
    if order_details:
        context['order_details']        = model_to_dict(order_details)
    else:
        context['order_details']        = order_details   
    context['order_item_list']          = order_item_list
    context['bulk_scheme']              = bulk_scheme
    context['quantitative_scheme']      = quantitative_scheme
    context['order_time']               = order_timing
    context['user_outstanding_amount']  = outstanding_amount
    context['user_opening_crates']      = opening_crates
    context['mode_of_payments']         = Sp_Mode_Of_Payments.objects.all().values('id', 'mode_of_payment').order_by('-mode_of_payment')
    context['order_time_slots']         = SpTimeSlots.objects.filter(status=1).values('id', 'start_timing', 'end_timing', 'timing_order').order_by('start_timing')
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#get order list
@csrf_exempt
@api_view(["POST"])
def orderList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if request.data.get("type") is None or request.data.get("type") == '':
        return Response({'message': 'Type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)


    #Call function to get dates range
    current_date = date.today() 
    if request.data.get("year") is None or request.data.get("year") == '':
        year = current_date.year
    else:
        year = request.data.get("year")

    if request.data.get("month") is None or request.data.get("month") == '':
        month = current_date.month
    else:
        month = request.data.get("month")

    if request.data.get("type") == '0':
        order_list = []
        index = 0
        total_weeks = weeks_in_month(year, month)
        for week in range(total_weeks):
            week_details = {}
            index += 1

            d = date(year,month,1)
            dlt = timedelta(days = (index-1)*7)
            start_date = d + dlt
            end_date = d + dlt + timedelta(days=6)
            total_day = numberOfDays(year,month)

            if month > 9:
                last_date = str(year)+'-'+str(month)+'-'+str(total_day)
            else:
                last_date = str(year)+'-0'+str(month)+'-'+str(total_day)
                
            if str(start_date) <= str(last_date) and (int(end_date.month) == int(month) or int(start_date.month) == int(month)):
                if str(last_date) < str(end_date):
                    end_date = last_date
                elif str(start_date) == str(end_date):
                    end_date = last_date     
                else:
                    end_date = end_date
                    
                week_details['week']            = index
                week_details['start_date']      = start_date
                week_details['end_date']        = end_date
                
                order_list.append(week_details)
    elif request.data.get("type") == '2':
        if request.data.get("start_date") is None or request.data.get("start_date") == '':
            return Response({'message': 'Start date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

        if request.data.get("end_date") is None or request.data.get("end_date") == '':
            return Response({'message': 'End date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

        start_date  = request.data.get("start_date")
        end_date    = datetime.strptime(request.data.get("end_date"), "%Y-%m-%d")
        end_date    = end_date + timedelta(days=1)
        
        order_list = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__range=[start_date, end_date]).values('id', 'order_code', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count')
        for order_item in order_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        if order_list:
            order_list  = order_list
        else:
            order_list  = []            
    else:
        order_list = SpOrders.objects.filter(user_id=request.data.get("user_id"), order_date__year=year, order_date__month=month).values('id', 'order_code', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count')
        for order_item in order_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        if order_list:
            order_list  = order_list
        else:
            order_list  = []
        
    context = {}
    context['order_list']               = order_list 
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def saveGrievance(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    if bool(request.FILES.get('attachment', False)) == True:
        uploaded_attachment = request.FILES['attachment']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        attachment_name = uploaded_attachment.name
        temp = attachment_name.split('.')
        attachment_name = 'attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        attachment = storage.save(attachment_name, uploaded_attachment)
        attachment = storage.url(attachment)        
            

    data = SpGrievance()
    data.user_id                = request.data.get("user_id")
    if request.data.get("order_id"):
        order = SpOrders.objects.filter(order_code=request.data.get("order_id")).exists()
        if not  order:
            return Response({'message': 'Order id not exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
        order = SpOrders.objects.get(order_code=request.data.get("order_id"))
        data.order_id               = order.id
    if request.data.get("reason_id"):
        data.reason_id              = request.data.get('reason_id')
    if request.data.get("reason_name"):
        data.reason_name            = request.data.get('reason_name')
    data.description            = request.data.get('description')
    if bool(request.FILES.get('attachment', False)) == True:
        data.attachment             = attachment
    data.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'New Grievance Request has been initiated'
    activity    = 'New Grievance Request has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Order Management', 'Order Grievance Request', heading, activity, request.user.id, user_name, 'grievanceRequest.png', '2', 'app.png')

    context = {}
    context['message']       = 'Grievance Request has been successfully sent'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def orderSchemeList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    today   = date.today()
    free_scheme = []
    scheme_details             = SpUserSchemes.objects.filter(scheme_type=1, user_id=request.data.get("user_id"), status=1).values('id', 'scheme_start_date', 'scheme_end_date') 
    for free in scheme_details:
        if free['scheme_start_date'] and free['scheme_end_date']:
            try:
                free_schemes = SpUserSchemes.objects.get(id=free['id'], scheme_start_date__lte=today.strftime("%Y-%m-%d"), scheme_end_date__gte=today.strftime("%Y-%m-%d"))
            except SpUserSchemes.DoesNotExist:
                free_schemes = None
        elif free['scheme_start_date'] and free['scheme_end_date'] is None:
            try:
                free_schemes = SpUserSchemes.objects.get(id=free['id'], scheme_start_date__lte=today.strftime("%Y-%m-%d"))
            except SpUserSchemes.DoesNotExist:
                free_schemes = None
        if free_schemes:
            if int(free_schemes.pouch_quantity) > 0:
                free_scheme_list = {}
                free_scheme_list['id']  = free_schemes.id
                free_scheme_list['scheme_id']  = free_schemes.scheme_id
                free_scheme_list['scheme_name']  = free_schemes.scheme_name
                free_scheme_list['state_id']  = free_schemes.state_id
                free_scheme_list['route_id']  = free_schemes.route_id
                free_scheme_list['town_id']  = free_schemes.town_id
                free_scheme_list['scheme_start_date']  = free_schemes.scheme_start_date
                free_scheme_list['scheme_end_date']  = free_schemes.scheme_end_date
                free_scheme_list['applied_on_variant_id']  = free_schemes.applied_on_variant_id
                free_scheme_list['applied_on_variant_name']  = free_schemes.applied_on_variant_name
                free_scheme_list['minimum_order_quantity']  = free_schemes.minimum_order_quantity
                free_scheme_list['order_container_id']  = free_schemes.order_container_id
                free_scheme_list['order_container_name']  = free_schemes.order_container_name
                free_scheme_list['order_packaging_id']  = free_schemes.order_packaging_id
                free_scheme_list['order_packaging_name']  = free_schemes.order_packaging_name
                free_scheme_list['free_variant_id']  = free_schemes.free_variant_id
                free_scheme_list['free_variant_name']  = free_schemes.free_variant_name
                free_scheme_list['container_quantity']  = free_schemes.container_quantity
                free_scheme_list['pouch_quantity']  = free_schemes.pouch_quantity
                free_scheme_list['packaging_type']  = free_schemes.packaging_type
                product_id                              = getModelColumnById(SpProductVariants, free_schemes.free_variant_id, 'product_id')
                free_scheme_list['container_type']      = getModelColumnById(SpProductVariants, free_schemes.free_variant_id, 'container_name')
                free_scheme_list['variant_size']        = float(getModelColumnById(SpProductVariants, free_schemes.free_variant_id, 'variant_size'))
                free_scheme_list['no_of_pouch']         = int(getModelColumnById(SpProductVariants, free_schemes.free_variant_id, 'no_of_pouch'))
                free_scheme_list['applied_no_of_pouch'] = int(getModelColumnById(SpProductVariants, free_schemes.applied_on_variant_id, 'no_of_pouch'))
                free_scheme.append(free_scheme_list)

    quantitative_scheme = []  
    scheme_list = SpUserSchemes.objects.filter(user_id=request.data.get("user_id"), status=1)
    for scheme in scheme_list:
        quantitative_scheme     = SpUserSchemes.objects.filter(scheme_type=2, user_id=request.data.get("user_id"), status=1).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'applied_on_variant_id', 'applied_on_variant_name', 'minimum_order_quantity', 'order_container_id', 'order_container_name', 'free_variant_id', 'free_variant_name', 'container_quantity', 'pouch_quantity') 
        for quantitative in quantitative_scheme:
            product_id             = getModelColumnById(SpProductVariants, quantitative['free_variant_id'], 'product_id')
            quantitative['container_type'] = getModelColumnById(SpProductVariants, quantitative['free_variant_id'], 'container_name')

    flat_scheme = []
    flat_schemes  = SpUserFlatSchemes.objects.filter(user_id=request.data.get("user_id"), incentive_amount__gt=0, status=1).values('id', 'scheme_start_date', 'scheme_end_date') 
    for flat in flat_schemes:
        if flat['scheme_start_date'] and flat['scheme_end_date']:
            try:
                flat_schemes = SpUserFlatSchemes.objects.get(id=flat['id'], incentive_amount__gt=0, scheme_start_date__lte=today.strftime("%Y-%m-%d"), scheme_end_date__gte=today.strftime("%Y-%m-%d"))
            except SpUserFlatSchemes.DoesNotExist:
                flat_schemes = None
        elif flat['scheme_start_date'] and flat['scheme_end_date'] is None:
            try:
                flat_schemes = SpUserFlatSchemes.objects.get(id=flat['id'], incentive_amount__gt=0, scheme_start_date__lte=today.strftime("%Y-%m-%d"))
            except SpUserFlatSchemes.DoesNotExist:
                flat_schemes = None
        if flat_schemes:
            flat_scheme_list = {}
            flat_scheme_list['id'] = flat_schemes.id
            flat_scheme_list['scheme_id'] = flat_schemes. scheme_id 
            flat_scheme_list['scheme_name'] = flat_schemes.scheme_name 
            flat_scheme_list['state_id'] = flat_schemes.state_id 
            flat_scheme_list['route_id'] = flat_schemes.route_id 
            flat_scheme_list['town_id'] = flat_schemes.town_id 
            flat_scheme_list['scheme_start_date'] = flat_schemes.scheme_start_date 
            flat_scheme_list['scheme_end_date'] = flat_schemes.scheme_end_date 
            flat_scheme_list['applied_on_variant_id'] = flat_schemes.applied_on_variant_id 
            flat_scheme_list['applied_on_variant_name'] = flat_schemes.applied_on_variant_name 
            flat_scheme_list['incentive_amount'] = flat_schemes.incentive_amount 
            flat_scheme_list['unit_id'] = flat_schemes.unit_id 
            flat_scheme_list['unit_name'] = flat_schemes.unit_name 
            flat_scheme_list['product_class_id'] = flat_schemes.product_class_id
            flat_scheme_list['no_of_pouch'] = getModelColumnById(SpProductVariants, flat_schemes.applied_on_variant_id, 'no_of_pouch')
            flat_scheme_list['variant_size'] = getModelColumnById(SpProductVariants, flat_schemes.applied_on_variant_id, 'variant_size')
            flat_scheme.append(flat_scheme_list)

    bulkpack_scheme_list = SpUserBulkpackSchemes.objects.filter(user_id=request.data.get("user_id"), status=1).values('id', 'scheme_id', 'scheme_name', 'state_id', 'route_id', 'town_id', 'scheme_start_date', 'scheme_end_date', 'unit_id', 'unit_name','product_class_id') 
    for bulkpack_scheme in bulkpack_scheme_list:
        bulkpack_scheme['bifurcation'] = SpUserBulkpackSchemeBifurcation.objects.filter(user_id=request.data.get("user_id")).values('id', 'user_id', 'bulkpack_scheme_id', 'above_upto_quantity', 'incentive_amount')
    
    context = {}
    context['message']              = 'Success'
    context['response_code']        = HTTP_200_OK
    context['free_scheme']          = free_scheme
    context['quantitative_scheme']  = quantitative_scheme
    context['flat_scheme']          = flat_scheme
    context['bulkpack_scheme']      = bulkpack_scheme_list
    return Response(context, status=HTTP_200_OK)

#get userOrder list
@csrf_exempt
@api_view(["POST"])
def userOrderList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 

    user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id')
    user_id = []
    for area_allocation in user_area_allocation:
        operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.user_type=%s and sp_users.status=%s order by sp_users.first_name asc ''', [area_allocation['town_id'], 2, 1])
        if operational_user_list: 
            for operational_user in operational_user_list:
                users_id  = operational_user.user_id
                user_id.append(users_id)
              
    #Call function to get dates range
    current_date = date.today() 
    if request.data.get("year") is None or request.data.get("year") == '':
        year = current_date.year
    else:
        year = request.data.get("year")

    if request.data.get("month") is None or request.data.get("month") == '':
        month = current_date.month
    else:
        month = request.data.get("month")
    if user_id:
        order_list = SpOrders.objects.filter(user_id__in=user_id, order_date__year=year, order_date__month=month).values('id', 'user_id', 'user_name', 'town_name', 'route_name', 'order_code', 'order_date', 'order_status', 'order_shift_id', 'order_shift_name', 'order_scheme_id', 'order_total_amount', 'order_items_count')
        for order_item in order_list:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']  = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        if order_list:
            order_list  = order_list
        else:
            order_list  = []
    else:
        order_list  = []    
        
    context = {}
    context['order_list']               = order_list 
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)     


@csrf_exempt
@api_view(["POST"])
def userlist(request):
    context = {}
    UserName = request.data.get('keyword')
    userType = request.data.get("user_type")
    context['data'] = list(
        SpUsers.objects.filter(first_name__icontains=UserName, user_type=userType, status=1).values('id', 'first_name', 'primary_contact_number', 'emp_sap_id', 'organization_id', 'organization_name'))

    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def customerlist(request):
    if request.method == 'POST':
        context = {}
        UserName = request.data.get('keyword')
        users = SpUsers.objects.filter(first_name__icontains=UserName, status=1).filter(Q(user_type=2) | Q(user_type=3)).values('id', 'first_name','middle_name','last_name','role_name')
        for user in users:
            if SpUserAreaAllocations.objects.filter(user_id = user['id']).exists():
                user_area = SpUserAreaAllocations.objects.filter(user_id = user['id']).first()
                name = user['first_name']+' '

                if user['middle_name'] is not None:
                    name += user['middle_name']+' '

                if user['last_name'] is not None:
                    name += user['last_name']

                user['first_name'] = name + '('+ user['role_name'] + '-'+ user_area.town_name+')'

        context['data'] = list(users)
        return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def productWithProductVariant(request):
    context = {}
    productList = SpProducts.objects.filter(status=1).values('id', 'product_name', 'product_class_name').order_by('product_name')
    for product in productList:
        product['product_variant_list'] = list(SpProductVariants.objects.filter(product_id=int(product['id']),status=1).values('id', 'variant_name', 'variant_size').order_by('variant_name'))

    context['products'] = list(productList)
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def freeOfCost(request):
    if request.method == 'POST':
        context = {}
        if request.data.get("user_id") is None or request.data.get("user_id") == '':
            return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST},
                            status=HTTP_400_BAD_REQUEST)

        if request.data.get("foc_delivery_date") is None or request.data.get("foc_delivery_date") == '':
            return Response({'message': 'foc_delivery_date field is required', 'response_code': HTTP_400_BAD_REQUEST},
                            status=HTTP_400_BAD_REQUEST)
        foc_delivery_date = (request.data.get('foc_delivery_date')).split(' ')[0]
        product_variant_list = request.data.get('product_variant_list')
        if request.data.get("product_variant_list") is None or request.data.get("product_variant_list") == '':
            return Response({'message': 'select any product', 'response_code': HTTP_400_BAD_REQUEST},
                            status=HTTP_400_BAD_REQUEST)

        request_by_name = request.user.first_name + ' ' + request.user.middle_name + ' ' + request.user.last_name

        context['request_by_name'] = request_by_name
        context['request_by_id'] = request.user.id
        context['user_id'] = request.data.get('user_id')
        context['user_name'] = getModelColumnById(SpUsers, request.data.get('user_id'), 'first_name')
        context['foc_delivery_date'] = foc_delivery_date

        # save data into table SpFocRequests()
        foc_request = SpFocRequests()

        foc_request.user_id = request.data.get('user_id')
        foc_request.user_name = getModelColumnById(SpUsers, request.data.get('user_id'), 'first_name')
        foc_request.foc_delivery_date = foc_delivery_date
        foc_request.request_by_id = request.user.id
        foc_request.request_by_name = request_by_name
        foc_request.foc_status = 1
        foc_request.save()

        for data in product_variant_list:
            id = data['product_variant_id']
            quantity = data['quantity']
            spFocRequestDetails = SpFocRequestsDetails()
            spFocRequestDetails.foc_request_id = (SpFocRequests.objects.filter(foc_delivery_date=foc_delivery_date).values('id').order_by('-id')[0])[
                    'id']
            spFocRequestDetails.product_id = getModelColumnById(SpProductVariants, id, 'product_id')
            spFocRequestDetails.product_name = getModelColumnById(SpProductVariants, id, 'product_name')
            spFocRequestDetails.product_variant_id = id
            spFocRequestDetails.product_variant_name = getModelColumnById(SpProductVariants, id, 'variant_name')
            spFocRequestDetails.product_variant_size = getModelColumnById(SpProductVariants, id, 'variant_size')
            spFocRequestDetails.quantity = quantity
            spFocRequestDetails.save()
        
        sendFocNotificationToUsers(foc_request.id, '', 'add', 39, request.user.id, request_by_name, 'SpFocRequests',request.user.role_id)

        return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def focRequestList(request):
    if request.method == "POST":
        if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
            return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

        context = {}
        foc_request_count = SpFocRequests.objects.filter(request_by_id=request.user.id).values('id').count()
        if foc_request_count:
            foc_request_count = math.ceil(round(foc_request_count/10, 2))
        else:
            foc_request_count = 0 

        page_limit  = int(request.data.get("page_limit"))*10
        offset      = int(page_limit)-10
        page_limit  = 10

        foc_requests = SpFocRequests.objects.filter(request_by_id=request.user.id).values('id', 'user_id','foc_status', 'user_name', 'foc_delivery_date', 'request_by_id', 'request_by_name').order_by('-id')[offset:offset+page_limit]
        for data in foc_requests:
            data['product_variant_list'] = list(SpFocRequestsDetails.objects.filter(foc_request_id=data['id']).order_by('-id').values('product_id', 'product_name', 'product_variant_id', 'product_variant_name','quantity'))
        
        context['products'] = list(foc_requests)
        context['foc_request_count'] = foc_request_count
        return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def userDashboardDetails(request):
    context = {}
    if not SpUserCrateLedger.objects.filter(user_id=request.user.id).exists():
        normal_crate_balance = 0
        jumbo_crate_balance = 0
    else:
        normal_crate_balance_record = SpUserCrateLedger.objects.raw(''' SELECT id, sum(normal_balance) as normal_balance FROM sp_user_crate_ledger WHERE id IN (SELECT MAX(id) FROM sp_user_crate_ledger GROUP BY user_id) ''')
        normal_crate_balance = normal_crate_balance_record[0].normal_balance

        jumbo_crate_balance_record = SpUserCrateLedger.objects.raw(''' SELECT id, sum(jumbo_balance) as jumbo_balance FROM sp_user_crate_ledger WHERE id IN (SELECT MAX(id) FROM sp_user_crate_ledger GROUP BY user_id) ''')
        jumbo_crate_balance = jumbo_crate_balance_record[0].jumbo_balance
        
    context['normal_crate_balance'] = int(normal_crate_balance) 
    context['jumbo_crate_balance'] = int(jumbo_crate_balance)

    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def userCrateLedger(request):
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    context = {}

    today  = date.today()
        
    if not SpUserCrateLedger.objects.filter(user_id=request.user.id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).exists():
        normal_crate_received = 0
        normal_crate_delivered = 0
        jumbo_crate_received = 0
        jumbo_crate_delivered = 0
        
    else:
        normal_crate_received_record = SpUserCrateLedger.objects.filter(user_id=request.user.id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).aggregate(Sum('normal_credit'))
        normal_crate_received = normal_crate_received_record['normal_credit__sum']
        normal_crate_delivered_record = SpUserCrateLedger.objects.filter(user_id=request.user.id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).aggregate(Sum('normal_debit'))
        normal_crate_delivered = normal_crate_delivered_record['normal_debit__sum']

        jumbo_crate_received_record = SpUserCrateLedger.objects.filter(user_id=request.user.id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).aggregate(Sum('jumbo_credit'))
        jumbo_crate_received = jumbo_crate_received_record['jumbo_credit__sum']
        jumbo_crate_delivered_record = SpUserCrateLedger.objects.filter(user_id=request.user.id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).aggregate(Sum('jumbo_debit'))
        jumbo_crate_delivered = jumbo_crate_delivered_record['jumbo_debit__sum']
        
    context['normal_crate_received'] = normal_crate_received 
    context['normal_crate_delivered'] = normal_crate_delivered

    context['jumbo_crate_received'] = jumbo_crate_received 
    context['jumbo_crate_delivered'] = jumbo_crate_delivered

    ledger_count = SpUserCrateLedger.objects.filter(user_id=request.user.id).values('id').count()
    if ledger_count:
        ledger_count = math.ceil(round(ledger_count/10, 2))
    else:
        ledger_count = 0 

    page_limit  = int(request.data.get("page_limit"))*30
    offset      = int(page_limit)-30
    page_limit  = 30

    crate_ledger = SpUserCrateLedger.objects.filter(user_id=request.user.id).values('id', 'user_id','driver_name', 'normal_credit', 'normal_debit', 'normal_balance', 'jumbo_credit','jumbo_debit','jumbo_balance','updated_datetime').order_by('-id')[offset:offset+page_limit]
    context['crate_ledger'] = list(crate_ledger)
    context['ledger_count'] = ledger_count

    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def notificationList(request):

    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    page_limit  = int(request.data.get("page_limit"))*30
    offset      = int(page_limit)-30
    page_limit  = 30

    try:
        notification_list = SpNotifications.objects.filter(to_user_id=request.user.id,to_user_type=1).values('id','row_id','model_name', 'heading', 'activity', 'activity_image', 'from_user_id', 'from_user_name', 'icon', 'platform_icon', 'read_status', 'created_at').order_by('-id')[offset:offset+page_limit]
    except SpAddresses.DoesNotExist:
        notification_list = None
    if notification_list:
        for notification in notification_list:
            if notification['activity_image']:
                notification['activity_image'] = baseurl+'/'+notification['activity_image']
            else:
                notification['activity_image'] = ''
            now = datetime.now()    
            notification['created_at'] = timeago.format(str(notification['created_at']), now)        
    else:    
        notification_list = []  

    notification_count = SpNotifications.objects.filter(to_user_id=request.user.id,to_user_type=1).values('id').count()
    if notification_count is not None:
        notification_count = math.ceil(round(notification_count/10, 2))
    else:
        notification_count = 0

    context = {}
    context['message']              = 'Success'
    context['notification_list']    = notification_list
    context['notification_count']   = notification_count
    context['response_code']        = HTTP_200_OK

    return Response(context, status=HTTP_200_OK)
    
@csrf_exempt
@api_view(["POST"])
def approvalList(request):
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    page_limit  = int(request.data.get("page_limit"))*30
    offset      = int(page_limit)-30
    page_limit  = 30

    try:
        approval_list = SpOrderCrateApproval.objects.filter(user_id=request.data.get("user_id")).values('id','transporter_id','driver_id', 'driver_name', 'user_id', 'user_name', 'delivered_normal', 'delivered_jumbo', 'received_normal', 'received_jumbo', 'status', 'updated_datetime').order_by('-id')[offset:offset+page_limit]
    except SpAddresses.DoesNotExist:
        approval_list = None
    if approval_list:
        for approval in approval_list:
            now = datetime.now() 
            approval['vehicle_no']       = getModelColumnById(SpVehicles, approval['transporter_id'], 'registration_number')   
            approval['created_at']       = timeago.format(str(approval['updated_datetime']), now)   
            approval_date                = str(approval['updated_datetime']).replace('+00:00', '')
            approval['created_date']     = datetime.strptime(str(approval_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')        
    else:    
        approval_list = []  

    approval_count = SpOrderCrateApproval.objects.filter(user_id=request.data.get("user_id")).values('id').count()
    if approval_count is not None:
        approval_count = math.ceil(round(approval_count/10, 2))
    else:
        approval_count = 0

    context = {}
    context['message']              = 'Success'
    context['approval_list']        = approval_list
    context['approval_count']       = approval_count
    context['response_code']        = HTTP_200_OK

    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def updateApprovalStatus(request):
    today   = date.today()
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("id")is None or request.data.get("id") == '':
        return Response({'message': 'Approval Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("status")is None or request.data.get("status") == '':
        return Response({'message': 'Status is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)

    try:
        approval_data = SpOrderCrateApproval.objects.get(id=request.data.get("id"), created_at__icontains=today.strftime("%Y-%m-%d"))
    except SpOrderCrateApproval.DoesNotExist:
        approval_data = None
    if approval_data:
        vehicle = SpVehicles.objects.get(id=approval_data.transporter_id)
        if request.data.get("status") == '2':
            item                            = SpOrderCrateApproval.objects.get(id=request.data.get("id"))
            item.status                     = 2
            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item.save()
 
            if approval_data.order_id and request.data.get("status") == '2':
                #update order status
                order = SpOrders.objects.get(id=approval_data.order_id)
                order.order_status = 4
                order.save()

                approval_order = SpApprovalStatus.objects.filter(row_id=approval_data.order_id).order_by('-id').first()
                if approval_order:
                    data                            = SpApprovalStatus()
                    data.row_id                     = approval_order.row_id
                    data.model_name                 = approval_order.model_name
                    data.initiated_by_id            = approval_order.user_id
                    data.initiated_by_name          = approval_order.user_name
                    data.user_id                    = vehicle.driver_id
                    data.user_name                  = vehicle.driver_name+'('+vehicle.registration_number+')'
                    data.role_id                    = approval_order.role_id
                    data.sub_module_id              = approval_order.sub_module_id
                    data.permission_id              = approval_order.permission_id
                    data.permission_slug            = approval_order.permission_slug
                    data.final_status_user_id       = vehicle.driver_id
                    data.final_status_user_name     = vehicle.driver_name+'('+vehicle.registration_number+')'
                    data.final_update_date_time     = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    data.level_id                   = 4
                    data.level                      = 'Delivered'
                    data.status                     = 1
                    data.save()

                message = ""
                message_title = "Request Approved"
                #update Transporter Crate Ledger
                if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:   
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.delivered_normal
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(last_row.normal_balance)-int(approval_data.delivered_normal)
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.delivered_jumbo
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(last_row.jumbo_balance)-int(approval_data.delivered_jumbo)
                    
                    item                            = SpTransporterCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = 0
                    item.normal_debit               = int(approval_data.delivered_normal)
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = 0  
                    item.jumbo_debit                = int(approval_data.delivered_jumbo)
                    item.jumbo_balance              = jumbo_balance 
                    item.is_route                   = 1
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()
                    
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.delivered_normal
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(approval_data.delivered_normal)+int(last_row.normal_balance)
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.delivered_jumbo
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(approval_data.delivered_jumbo)+int(last_row.jumbo_balance)

                    item                            = SpUserCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = int(approval_data.delivered_normal)
                    item.normal_debit               = 0
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = int(approval_data.delivered_jumbo)  
                    item.jumbo_debit                = 0
                    item.jumbo_balance              = jumbo_balance 
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()    

                    total_delivered_crates = int(approval_data.delivered_normal)+int(approval_data.delivered_jumbo)
                    message += str(total_delivered_crates)+" Crates has been delivered."
                    if int(approval_data.delivered_normal) > 0:
                        message += '\n'+str(approval_data.delivered_normal)+" normal " 
                    if int(approval_data.delivered_jumbo) > 0:
                        message += '\n'+str(approval_data.delivered_jumbo)+" jumbo"

                    # message_title += "delivered"
                #update User Crate Ledger
                if int(approval_data.received_normal) > 0 or int(approval_data.received_jumbo) > 0:   
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.received_normal
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(last_row.normal_balance)-int(approval_data.received_normal)
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.received_jumbo
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(last_row.jumbo_balance)-int(approval_data.received_jumbo)
                    
                    item                            = SpUserCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = 0
                    item.normal_debit               = int(approval_data.received_normal)
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = 0  
                    item.jumbo_debit                = int(approval_data.received_jumbo)
                    item.jumbo_balance              = jumbo_balance 
                    item.is_route                   = 1
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()

                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.received_normal
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(approval_data.received_normal)+int(last_row.normal_balance)
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.received_jumbo
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(approval_data.received_jumbo)+int(last_row.jumbo_balance)
                    
                    item                            = SpTransporterCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = int(approval_data.received_normal)
                    item.normal_debit               = 0
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = int(approval_data.received_jumbo)  
                    item.jumbo_debit                = 0  
                    item.jumbo_balance              = jumbo_balance 
                    item.is_route                   = 1
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()

                    total_received_crates = int(approval_data.received_normal)+int(approval_data.received_jumbo)
                    if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:
                        message += '\n and '+str(total_received_crates)+" Crates has been received."
                    else:
                        message += str(total_received_crates)+" Crates has been received."
                    if int(approval_data.received_normal) > 0:
                        message += '\n'+str(approval_data.received_normal)+" normal " 
                    if int(approval_data.received_jumbo) > 0:
                        message += '\n'+str(approval_data.received_jumbo)+" jumbo"
                    
                    # if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:
                    #     message_title += " and received"
                    # else:
                    #     message_title += " received"
                #-----------------------------notify android block-------------------------------#
                notification_image = ""
                message_body = message

                user_name = getUserName(request.data.get("user_id"))
                userFirebaseToken   = vehicle.firebase_token
                registration_number = vehicle.registration_number
                transporter_details = vehicle.driver_name+'('+registration_number+')'
                
                if userFirebaseToken is not None and userFirebaseToken != "" :
                    registration_ids = []
                    registration_ids.append(userFirebaseToken)
                    data_message = {}
                    data_message['id'] = 1
                    data_message['status'] = 'notification'
                    data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                    data_message['image'] = notification_image
                    send_android_notification(message_title,message_body,data_message,registration_ids)
                    #-----------------------------notify android block-------------------------------#
                #-----------------------------save notification block----------------------------#
                saveNotification(None,None,'Order Management',message_title,message_title,message_body,notification_image,request.user.id,user_name,vehicle.id,transporter_details,'order.png',2,'app.png',1,2)
                #-----------------------------save notification block-------- --------------------#

                # save activity
                heading     = message
                activity    = 'Request has been approved by  on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p')
                saveActivity('Order Management', 'Request approved', heading, activity, request.data.get("user_id"), user_name, 'updateVehiclePass.png', '2', 'app.png')


                context = {}
                context['message']              = "Request has been approved"
                context['response_code']        = HTTP_200_OK

                return Response(context, status=HTTP_200_OK)
            else:
                message = ""
                message_title = "Request Approved"
                #update Transporter Crate Ledger
                if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:   
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.delivered_normal
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(last_row.normal_balance)-int(approval_data.delivered_normal)
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.delivered_jumbo
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(last_row.jumbo_balance)-int(approval_data.delivered_jumbo)
                    
                    item                            = SpTransporterCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = 0
                    item.normal_debit               = int(approval_data.delivered_normal)
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = 0  
                    item.jumbo_debit                = int(approval_data.delivered_jumbo)
                    item.jumbo_balance              = jumbo_balance 
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()
                    
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.delivered_normal
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(approval_data.delivered_normal)+int(last_row.normal_balance)
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.delivered_jumbo
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(approval_data.delivered_jumbo)+int(last_row.jumbo_balance)

                    item                            = SpUserCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = int(approval_data.delivered_normal)
                    item.normal_debit               = 0
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = int(approval_data.delivered_jumbo)  
                    item.jumbo_debit                = 0
                    item.jumbo_balance              = jumbo_balance 
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()    

                    total_delivered_crates = int(approval_data.delivered_normal)+int(approval_data.delivered_jumbo)
                    message += str(total_delivered_crates)+" Crates has been delivered."
                    if int(approval_data.delivered_normal) > 0:
                        message += '\n'+str(approval_data.delivered_normal)+" normal " 
                    if int(approval_data.delivered_jumbo) > 0:
                        message += '\n'+str(approval_data.delivered_jumbo)+" jumbo"

                    # message_title += "delivered"
                #update User Crate Ledger
                if int(approval_data.received_normal) > 0 or int(approval_data.received_jumbo) > 0:   
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.received_normal
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(last_row.normal_balance)-int(approval_data.received_normal)
                    if not SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.received_jumbo
                    else:
                        last_row = SpUserCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(last_row.jumbo_balance)-int(approval_data.received_jumbo)
                    
                    item                            = SpUserCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = 0
                    item.normal_debit               = int(approval_data.received_normal)
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = 0  
                    item.jumbo_debit                = int(approval_data.received_jumbo)
                    item.jumbo_balance              = jumbo_balance 
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()

                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        normal_balance = approval_data.received_normal
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        normal_balance = int(approval_data.received_normal)+int(last_row.normal_balance)
                    if not SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).exists():
                        jumbo_balance = approval_data.received_jumbo
                    else:
                        last_row = SpTransporterCrateLedger.objects.filter(user_id=request.data.get("user_id"), transporter_id=vehicle.id).order_by('-id').first()
                        jumbo_balance = int(approval_data.received_jumbo)+int(last_row.jumbo_balance)
                    
                    item                            = SpTransporterCrateLedger()
                    item.transporter_id             = vehicle.id
                    item.driver_id                  = vehicle.driver_id
                    item.driver_name                = vehicle.driver_name
                    item.user_id                    = request.data.get("user_id")
                    item.normal_credit              = int(approval_data.received_normal)
                    item.normal_debit               = 0
                    item.normal_balance             = normal_balance
                    item.jumbo_credit               = int(approval_data.received_jumbo)  
                    item.jumbo_debit                = 0  
                    item.jumbo_balance              = jumbo_balance 
                    item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    item.save()

                    total_received_crates = int(approval_data.received_normal)+int(approval_data.received_jumbo)
                    if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:
                        message += '\n and '+str(total_received_crates)+" Crates has been received."
                    else:
                        message += str(total_received_crates)+" Crates has been received."
                    if int(approval_data.received_normal) > 0:
                        message += '\n'+str(approval_data.received_normal)+" normal " 
                    if int(approval_data.received_jumbo) > 0:
                        message += '\n'+str(approval_data.received_jumbo)+" jumbo"
                    
                    # if int(approval_data.delivered_normal) > 0 or int(approval_data.delivered_jumbo) > 0:
                    #     message_title += " and received"
                    # else:
                    #     message_title += " received"
                #-----------------------------notify android block-------------------------------#
                notification_image = ""
                message_body = message

                user_name = getUserName(request.data.get("user_id"))
                userFirebaseToken   = vehicle.firebase_token
                registration_number = vehicle.registration_number
                transporter_details = vehicle.driver_name+'('+registration_number+')'
                
                if userFirebaseToken is not None and userFirebaseToken != "" :
                    registration_ids = []
                    registration_ids.append(userFirebaseToken)
                    data_message = {}
                    data_message['id'] = 1
                    data_message['status'] = 'notification'
                    data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                    data_message['image'] = notification_image
                    send_android_notification(message_title,message_body,data_message,registration_ids)
                    #-----------------------------notify android block-------------------------------#
                #-----------------------------save notification block----------------------------#
                saveNotification(None,None,'Order Management',message_title,message_title,message_body,notification_image,request.user.id,user_name,vehicle.id,transporter_details,'order.png',2,'app.png',1,2)
                #-----------------------------save notification block-------- --------------------#

                # save activity
                heading     = message
                activity    = 'Request has been approved by  on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p')
                saveActivity('Order Management', 'Request approved', heading, activity, request.data.get("user_id"), user_name, 'updateVehiclePass.png', '2', 'app.png')


                context = {}
                context['message']              = "Request has been approved"
                context['response_code']        = HTTP_200_OK

                return Response(context, status=HTTP_200_OK)

        else:
            item                            = SpOrderCrateApproval.objects.get(id=request.data.get("id"))
            item.status                     = 3
            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item.save()
            
            user_name = getUserName(request.data.get("user_id"))
            message = "Your Request has been declined by "+user_name+"."
            message_title = "Request Declined"

            #-----------------------------notify android block-------------------------------#
            notification_image = ""
            message_body = message

            userFirebaseToken   = vehicle.firebase_token
            registration_number = vehicle.registration_number
            transporter_details = vehicle.driver_name+'('+registration_number+')'
            
            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 1
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#
            #-----------------------------save notification block----------------------------#
            saveNotification(None,None,'Order Management',message_title,message_title,message_body,notification_image,request.user.id,user_name,vehicle.id,transporter_details,'order.png',2,'app.png',1,2)
            #-----------------------------save notification block-------- --------------------#

            # save activity
            heading     = message
            activity    = 'Request has been declined by  on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p')
            saveActivity('Order Management', 'Request declined', heading, activity, request.data.get("user_id"), user_name, 'updateVehiclePass.png', '2', 'app.png')


            context = {}
            context['message']              = "Request has been declined"
            context['response_code']        = HTTP_200_OK

            return Response(context, status=HTTP_200_OK)
    else:
        return Response({'message': 'Approval Data not found', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    