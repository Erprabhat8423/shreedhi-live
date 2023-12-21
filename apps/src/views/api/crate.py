import json
import time
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
# get free schemes helper function
def getFreeSchemes(product_variant_id, order_id, user_id):
    try:
        free_scheme = SpOrderSchemes.objects.get(order_id=order_id, variant_id=product_variant_id, scheme_type='free', user_id=user_id)
    except SpOrderSchemes.DoesNotExist:
        free_scheme = None
    if free_scheme:
        free = 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')+''
        if free_scheme.container_quantity>0:
            product_id             = getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'product_id')
            free += str(free_scheme.container_quantity)+' free '+getModelColumnById(SpProducts, product_id, 'container_name')+''
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
    

#get superstockist vehicle list for dispatch crates
@csrf_exempt
@api_view(["POST"])
def getUserVehicleList(request):
    if request.data.get("route_id") is None or request.data.get("route_id") == '':
        return Response({'message': 'Route is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    try:
        driver_details = SpVehicles.objects.filter(route_id=request.data.get("route_id")).all()

    except SpVehicles.DoesNotExist:
        driver_details = None
        
    if driver_details is None:
        return Response({'message': 'No Driver assigned on this route', 'response_code': HTTP_200_OK}, status=HTTP_200_OK) 
    today   = date.today()
    
    vehicles=[]
    for driver_detail in driver_details:
        temp={}
        temp['vehicle_id']               = driver_detail.id
        temp['vehicle_no']               = driver_detail.registration_number
        temp['driver_id']                = driver_detail.driver_id
        temp['driver_name']              = driver_detail.driver_name
        temp['driver_contact_no']        = "-" if (driver_detail.driver_id is None) else getModelColumnById(SpDrivers,driver_detail.driver_id,'primary_contact_number')
        vehicles.append(temp)
        
    context = {}
    context['vehicles']                 = vehicles
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

#get superstockist order list for dispatch crates
@csrf_exempt
@api_view(["POST"])
def getUserOrderList(request):
    if request.data.get("route_id") is None or request.data.get("route_id") == '':
        return Response({'message': 'Route is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("vehicle_id") is None or request.data.get("vehicle_id") == '':
        return Response({'message': 'Vehicle is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    try:
        driver_details = SpVehicles.objects.get(route_id=request.data.get("route_id"),id=request.data.get("vehicle_id"))
    except SpVehicles.DoesNotExist:
        driver_details = None
        
    if driver_details is None:
        return Response({'message': 'No Driver assigned on this route', 'response_code': HTTP_200_OK}, status=HTTP_200_OK)
    today   = date.today()
    user_list = SpOrders.objects.filter(order_date__icontains=today.strftime("%Y-%m-%d"), route_id=request.data.get("route_id"), order_status__gt=2).values('id', 'user_id', 'user_name', 'route_id', 'route_name', 'order_date', 'order_status', 'dispatch_order_status')
    for order_details in user_list:
        if order_details['dispatch_order_status'] == 0:
            order_details['normal'] = ''
            order_details['jumbo']  = ''
        else:
            order_details['normal'] = SpPlantCrateLedger.objects.filter(updated_datetime__icontains=today.strftime("%Y-%m-%d"), plant_user_id=request.user.id, user_id=order_details['user_id']).values_list('normal_debit', flat=True)[0]
            order_details['jumbo']  = SpPlantCrateLedger.objects.filter(updated_datetime__icontains=today.strftime("%Y-%m-%d"), plant_user_id=request.user.id, user_id=order_details['user_id']).values_list('jumbo_debit', flat=True)[0]
       
        order_details['store_name']    = getModelColumnById(SpUsers, order_details['user_id'], 'store_name')
        order_date = str(order_details['order_date']).replace('+00:00', '')
        order_details['order_date']     = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
        order_details['product_list']   = SpOrderDetails.objects.filter(order_id=order_details['id']).values('id', 'order_id', 'product_id', 'product_name', 'product_variant_id', 'product_variant_name', 'quantity', 'rate', 'amount', 'order_date','product_container_type','packaging_type','product_packaging_type_name')
         
        for order_item in order_details['product_list']:
            order_date = str(order_item['order_date']).replace('+00:00', '')
            order_item['order_date']            = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
            container_name                      = SpProducts.objects.get(id=order_item['product_id'])
            order_item['container_name']        = order_item['product_container_type']
            order_item['product_class_name']    = container_name.product_class_name
            order_item['unit_name']             = getModelColumnById(SpProductVariants, order_item['product_variant_id'], 'largest_unit_name')
            order_item['order_date']            = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
            order_item['free_scheme']           = getFreeSchemes(order_item['product_variant_id'], order_item['order_id'], order_details['user_id'])
    if user_list:
        user_list  = user_list
    else:
        user_list  = []
    context = {}
    context['vehicle_id']               = driver_details.id
    context['vehicle_no']               = driver_details.registration_number
    context['driver_id']                = driver_details.driver_id
    context['driver_name']              = driver_details.driver_name
    context['driver_contact_no']        = "-" if (driver_details.driver_id is None) else getModelColumnById(SpDrivers,driver_details.driver_id,'primary_contact_number')
    context['user_list']                = user_list
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 

@csrf_exempt
@api_view(["POST"])
def sendOtp(request):
    if request.data.get("vehicle_id")is None or request.data.get("vehicle_id") == '':
        return Response({'message': 'Please provide vehicle id', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("mobile_no")is None or request.data.get("mobile_no") == '':
        return Response({'message': 'Please provide mobile no.', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("normal_crates")is None or request.data.get("normal_crates") == '':
        return Response({'message': 'Please provide normal crates', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("jumbo_crates")is None or request.data.get("jumbo_crates") == '':
        return Response({'message': 'Please provide jumbo crates', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("otp_type")is None or request.data.get("otp_type") == '':
        return Response({'message': 'Please provide otp type', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    try:
        user_details = SpDrivers.objects.filter(primary_contact_number=request.data.get("mobile_no"), status=1).first()
    except SpUsers.DoesNotExist:
        user_details = None
    try:
        vehicle_details = SpVehicles.objects.filter(id=request.data.get("vehicle_id"), status=1).first()
    except SpVehicles.DoesNotExist:
        vehicle_details = None
    
    if not vehicle_details:
        return Response({'message': 'Invalid vehicle id', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if user_details:
        otp = generateOTP()
        try:
            user_otp = SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id")).first()
        except SpOrderOtp.DoesNotExist:
            user_otp = None
        if user_otp:
            SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id")).delete()
        user_otp                = SpOrderOtp()
        user_otp.vehicle_id     = request.data.get("vehicle_id")
        user_otp.order_id       = vehicle_details.driver_id
        user_otp.otp            = otp
        user_otp.save()

        user_name   = str(request.user.first_name)
        if request.user.middle_name:
            user_name += ' '+str(request.user.middle_name)
        if request.user.last_name:
            user_name += ' '+str(request.user.last_name)
            
        message = "You are receiving "
        if int(request.data.get("normal_crates")) > 0 :
            message += str(int(request.data.get("normal_crates"))) + " normal crate"
        if int(request.data.get("jumbo_crates")) > 0 :
            message += ' and '+str(int(request.data.get("jumbo_crates"))) + " jumbo crate"
        if request.data.get("otp_type") == '0':
            message += ". Share this OTP("+ str(otp) +") with "+str(user_name)+" for dispatch ordered crates."
            message_title   = "Dispatch Order OTP"
            title           = 'Dispatch Order Crates'
        else:    
            message += ". Share this OTP("+ str(otp) +") with "+str(user_name)+" for receiving crates."
            message_title   = "Received Crates OTP"
            title           = 'Received Crates'
        sendSMS('SAAHAJ',request.data.get("mobile_no"),message)
        #-----------------------------notify android block-------------------------------#
        notification_image = ""
        
        message_body = message
        userFirebaseToken = getModelColumnById(SpVehicles,request.data.get("vehicle_id"),'firebase_token')
        registration_number = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'registration_number')
        transporter_details = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')+'('+registration_number+')'
        
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
        saveNotification(None,None,'Order Management',title,message_title,message_body,notification_image,request.user.id,user_name,request.data.get("vehicle_id"),transporter_details,'order.png',2,'app.png',1,2)
        #-----------------------------save notification block-------- --------------------#
        context = {}
        context['message']          = 'OTP sent successfully'
        context['otp']              = otp
        context['response_code']    = HTTP_200_OK
        return Response(context, status=HTTP_200_OK)
    else:
        return Response({'message': 'Invalid mobile no.', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
#save order and order details for dispatch crates
@csrf_exempt
@api_view(["POST"])
def dispatchCrates(request):
    today  = date.today()
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("otp") is None or request.data.get("otp") == '':
        return Response({'message': 'OTP is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("vehicle_id") is None or request.data.get("vehicle_id") == '':
        return Response({'message': 'Vehicle Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if not SpVehicles.objects.filter(id=request.data.get("vehicle_id")).exists():
        return Response({'message': 'Invalid Vehicle Id', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if not SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id"), order_id=getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id'),otp=request.data.get("otp")).exists():
        return Response({'message': 'Invalid OTP', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    #reset otp
    #SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id"), order_id=getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id'),otp=request.data.get("otp")).delete()         
    if request.data.get("crates_list") is None or request.data.get("crates_list") == '':
        return Response({'message': 'Crate Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    order_id=(request.data.get("order_id")).split(",")
    if not SpOrders.objects.filter(id__in=order_id).exists():
        return Response({'message': 'Order Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    else:
        orders   = SpOrders.objects.filter(id__in=order_id)
        for order in orders:
            data = SpOrders.objects.get(id=order.id)
            data.dispatch_order_status = 1
            data.save()
     
    
    crates_list = request.data.get('crates_list')
    #save crates details
    for crate in crates_list:
        if not SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            normal_balance = crate['normal_crate']
        else:
            last_row = SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            normal_balance = int(crate['normal_crate'])+int(last_row.normal_balance)
        if not SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            jumbo_balance = crate['jumbo_crate']
        else:
            last_row = SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            jumbo_balance = int(crate['jumbo_crate'])+int(last_row.jumbo_balance)
        item                            = SpPlantCrateLedger()
        item.plant_user_id              = request.data.get("user_id")
        item.transporter_id             = request.data.get("vehicle_id")
        item.driver_id                  = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id')
        item.driver_name                = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')
        item.user_id                    = crate['ss_distributor_id']
        item.normal_credit              = 0
        item.normal_debit               = crate['normal_crate']
        item.normal_balance             = normal_balance
        item.jumbo_credit               = 0  
        item.jumbo_debit                = crate['jumbo_crate']
        item.jumbo_balance              = jumbo_balance 
        item.is_route                   = 1
        item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()
    #save crates details
    for crate in crates_list:
        if not SpTransporterCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            normal_balance = crate['normal_crate']
        else:
            last_row = SpTransporterCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            normal_balance = int(crate['normal_crate'])+int(last_row.normal_balance)
        if not SpTransporterCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            jumbo_balance = crate['jumbo_crate']
        else:
            last_row = SpTransporterCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            jumbo_balance = int(crate['jumbo_crate'])+int(last_row.jumbo_balance)
        item                            = SpTransporterCrateLedger()
        item.plant_user_id              = request.data.get("user_id")
        item.transporter_id             = request.data.get("vehicle_id")
        item.driver_id                  = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id')
        item.driver_name                = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')
        item.user_id                    = crate['ss_distributor_id']
        item.normal_credit              = crate['normal_crate']
        item.normal_debit               = 0
        item.normal_balance             = normal_balance
        item.jumbo_credit               = crate['jumbo_crate']  
        item.jumbo_debit                = 0
        item.jumbo_balance              = jumbo_balance 
        item.is_route                   = 1
        item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()     
    registration_number = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'registration_number')
    transporter_details = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')+'('+registration_number+')'
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Order has been dispatched from plant'
    activity    = 'Order has been dispatched from plant by '+user_name+' to '+transporter_details+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    saveActivity('Crate Management', 'Crate Dispatch', heading, activity, request.user.id, user_name, 'Orderplaced.png', '2', 'app.png')
    context = {}
    context['message']                  = 'Order has been dispatched successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#get superstockist list used for receive crates
@csrf_exempt
@api_view(["POST"])
def getUserList(request):
    if request.data.get("route_id") is None or request.data.get("route_id") == '':
        return Response({'message': 'Route is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("vehicle_id") is None or request.data.get("vehicle_id") == '':
        return Response({'message': 'Vehicle is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    try:
        driver_details = SpVehicles.objects.get(route_id=request.data.get("route_id"),id=request.data.get("vehicle_id"))
    except SpVehicles.DoesNotExist:
        driver_details = None
        
    if driver_details is None:
        return Response({'message': 'No Driver assigned on this route', 'response_code': HTTP_200_OK}, status=HTTP_200_OK) 
    user_list = SpUserAreaAllocations.objects.filter(route_id=request.data.get("route_id")).values('id', 'user_id', 'route_id', 'route_name')
    user_lists = []
    for user in user_list:
        if getModelColumnById(SpUsers, user['user_id'], 'user_type') == 2:
            route_users = {}
            route_users['id']       = user['id']
            route_users['user_id']  = user['user_id']
            route_users['username'] = getModelColumnById(SpUsers, user['user_id'], 'first_name')+' '+getModelColumnById(SpUsers, user['user_id'], 'middle_name')+' '+getModelColumnById(SpUsers, user['user_id'], 'last_name')
            route_users['store_name']    = getModelColumnById(SpUsers, route_users['user_id'], 'store_name')
            user_lists.append(route_users)
    
    context = {}
    context['vehicle_id']               = driver_details.id
    context['vehicle_no']               = driver_details.registration_number
    context['driver_id']                = driver_details.driver_id
    context['driver_name']              = driver_details.driver_name
    context['driver_contact_no']        = "-" if (driver_details.driver_id is None) else getModelColumnById(SpDrivers,driver_details.driver_id,'primary_contact_number')
    context['user_list']                = user_lists
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


#save order and order details for dispatch crates
@csrf_exempt
@api_view(["POST"])
def receivedCrates(request):
    today  = date.today()
    if request.data.get("user_id") is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("otp") is None or request.data.get("otp") == '':
        return Response({'message': 'OTP is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("vehicle_id") is None or request.data.get("vehicle_id") == '':
        return Response({'message': 'Vehicle Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if not SpVehicles.objects.filter(id=request.data.get("vehicle_id")).exists():
        return Response({'message': 'Invalid Vehicle Id', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if not SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id"), order_id=getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id'),otp=request.data.get("otp")).exists():
        return Response({'message': 'Invalid OTP', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    #reset otp
    #SpOrderOtp.objects.filter(vehicle_id=request.data.get("vehicle_id"), order_id=getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id'),otp=request.data.get("otp")).delete()         
    if request.data.get("crates_list") is None or request.data.get("crates_list") == '':
        return Response({'message': 'Crate Details is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
          
     
    
    crates_list = request.data.get('crates_list')
    #save crates details
    for crate in crates_list:
        if not SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            normal_balance = crate['normal_crate']
        else:
            last_row = SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            normal_balance = int(last_row.normal_balance)-int(crate['normal_crate'])
        if not SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            jumbo_balance = crate['jumbo_crate']
        else:
            last_row = SpPlantCrateLedger.objects.filter(plant_user_id=request.data.get("user_id"), transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            jumbo_balance = int(last_row.jumbo_balance)-int(crate['jumbo_crate'])
        item                            = SpPlantCrateLedger()
        item.plant_user_id              = request.data.get("user_id")
        item.transporter_id             = request.data.get("vehicle_id")
        item.driver_id                  = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id')
        item.driver_name                = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')
        item.user_id                    = crate['ss_distributor_id']
        item.normal_credit              = crate['normal_crate']
        item.normal_debit               = 0
        item.normal_balance             = normal_balance
        item.jumbo_credit               = crate['jumbo_crate']  
        item.jumbo_debit                = 0
        item.jumbo_balance              = jumbo_balance 
        item.is_route                   = 1
        item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()
    
    for crate in crates_list:
        if not SpTransporterCrateLedger.objects.filter(transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            normal_balance = crate['normal_crate']
        else:
            last_row = SpTransporterCrateLedger.objects.filter(transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            # if int(last_row.normal_balance) >= int(crate['normal_crate']):
            #     normal_balance = int(last_row.normal_balance)-int(crate['normal_crate'])
            # else:    
            #     normal_balance = int(crate['normal_crate'])-int(last_row.normal_balance)
            normal_balance = int(last_row.normal_balance)-int(crate['normal_crate']) 
        if not SpTransporterCrateLedger.objects.filter(transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).exists():
            jumbo_balance = crate['jumbo_crate']
        else:
            last_row = SpTransporterCrateLedger.objects.filter(transporter_id=request.data.get("vehicle_id"), user_id=crate['ss_distributor_id']).order_by('-id').first()
            # if int(last_row.jumbo_balance) >= int(crate['jumbo_crate']):
            #     jumbo_balance = int(last_row.jumbo_balance)-int(crate['jumbo_crate'])
            # else:    
            #     jumbo_balance = int(crate['jumbo_crate'])-int(last_row.jumbo_balance)
            jumbo_balance = int(last_row.jumbo_balance)-int(crate['jumbo_crate'])
        item                            = SpTransporterCrateLedger()
        item.plant_user_id              = request.data.get("user_id")
        item.transporter_id             = request.data.get("vehicle_id")
        item.driver_id                  = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_id')
        item.driver_name                = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')
        item.user_id                    = crate['ss_distributor_id']
        item.normal_credit              = 0
        item.normal_debit               = crate['normal_crate']
        item.normal_balance             = normal_balance
        item.jumbo_credit               = 0  
        item.jumbo_debit                = crate['jumbo_crate']
        item.jumbo_balance              = jumbo_balance 
        item.is_route                   = 1
        item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        item.save()
    registration_number = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'registration_number')
    transporter_details = getModelColumnById(SpVehicles, request.data.get("vehicle_id"), 'driver_name')+'('+registration_number+')'
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Crates has been received by plant'
    activity    = 'Crates has been received by plant('+user_name+') from '+transporter_details+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    saveActivity('Crate Management', 'Crate Received', heading, activity, request.user.id, user_name, 'Orderplaced.png', '2', 'app.png')
    context = {}
    context['message']                  = 'Crates has been received successfully.'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)      

