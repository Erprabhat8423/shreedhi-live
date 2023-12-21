from ...models import *
from ...decorators import validate_logistic_api,validatePOST,validateGET
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
from django.core import serializers
from utils import *
from datetime import datetime, date
from datetime import timedelta
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from  django.contrib.auth.hashers import check_password,make_password
import json,time,timeago
from math import sin, cos, sqrt, atan2, radians

@csrf_exempt
@validatePOST
def login(request):
    response = {}
    status_code = 200
    received_data=json.loads(request.body)
    if 'registration_number' not in received_data or received_data['registration_number'] == "" :
        response['message'] = "Registration Number is missing"
        status_code = 404
    if 'password' not in received_data or received_data['password'] == "" :
        response['message'] = "Password is missing"
        status_code = 404
    
    if status_code == 200 :
        registration_number = received_data['registration_number']
        password = received_data['password']
        if SpVehicles.objects.filter(registration_number=registration_number).exists() :
            vehicle = SpVehicles.objects.get(registration_number=registration_number)
            if vehicle.password:
                if check_password(received_data['password'], vehicle.password):
                    if vehicle.route_id is not None :
                        if received_data['firebase_token'] != "":
                            vehicle.firebase_token = received_data['firebase_token']

                        vehicle.api_token = make_password(str(vehicle.id) + str(vehicle.registration_number))
                        vehicle.save()
                        response['message'] = "Logged in successfully"
                        response['registration_number'] = vehicle.registration_number
                        response['route_name'] = vehicle.route_name
                        response['user_id'] = vehicle.id
                        response['api_key'] = vehicle.api_token
                        if vehicle.vehicle_pic is None:
                            response['vehicle_pic'] = '/static/img/png/default_app_icon.png'
                        else:
                            response['vehicle_pic'] = vehicle.vehicle_pic
                        response['tracking_time']   = getModelColumnById(Configuration, 1, 'user_tracking_time')
                        response['contact_number']  = getConfigurationResult('contact_number')
                        status_code = 200
                    else:
                        response['message'] = "Route is not assigned. please contact the administrator."
                        status_code = 401
                else:
                    response['message'] = "Invalid Credentials"
                    status_code = 401
            else:
                response['message'] = "Invalid Credentials"
                status_code = 401        
        else:
            response['message'] = "Invalid Credentials"
            status_code = 401
    return JsonResponse(response,status = status_code)

@csrf_exempt
@validateGET
@validate_logistic_api
def getMasterData(request):

    api_token = request.headers['Authorization']
    vehicle = SpVehicles.objects.get(api_token=api_token)

    response = {}
    response['state_list']               = list(SpStates.objects.all().values('id', 'state'))
    response['city_list']                = list(SpCities.objects.all().values('id', 'state_id', 'city'))
    response['leave_type_list']          = list(SpLeaveTypes.objects.all().values('id', 'alias', 'leave_type'))
    response['route_list']               = list(SpRoutes.objects.filter(id=vehicle.route_id).values('id', 'route'))
    response['message']                  = 'Success'
    response['response_code']            = 200
    return JsonResponse(response,status = 200)



@csrf_exempt
@validateGET
@validate_logistic_api
def dashboardDetails(request):
    
    response = {}
    status_code = 200
    api_token = request.headers['Authorization']
    vehicle = SpVehicles.objects.get(api_token=api_token)
    if vehicle.route_id is None:
        response['message'] = "Route is not assigned. please contact the administrator."
        status_code = 401
    else:
        if not SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id).exists():
            normal_crate_balance = 0
            jumbo_crate_balance = 0
        else:
            # normal_crate_balance_record = SpTransporterCrateLedger.objects.raw(''' SELECT id, sum(normal_balance) as normal_balance FROM sp_transporter_crate_ledger WHERE id IN (SELECT MAX(id) FROM sp_transporter_crate_ledger GROUP BY user_id) ''')
            normal_crate_balance_record = SpTransporterCrateLedger.objects.raw(''' SELECT id, sum(normal_credit)-sum(normal_debit) as normal_balance FROM sp_transporter_crate_ledger WHERE transporter_id=%s ''',[vehicle.id])
            normal_crate_balance = normal_crate_balance_record[0].normal_balance

            # jumbo_crate_balance_record = SpTransporterCrateLedger.objects.raw(''' SELECT id, sum(jumbo_balance) as jumbo_balance FROM sp_transporter_crate_ledger WHERE id IN (SELECT MAX(id) FROM sp_transporter_crate_ledger GROUP BY user_id) ''')
            jumbo_crate_balance_record = SpTransporterCrateLedger.objects.raw(''' SELECT id, sum(jumbo_credit)-sum(jumbo_debit) as jumbo_balance FROM sp_transporter_crate_ledger WHERE transporter_id=%s ''',[vehicle.id])
            
            jumbo_crate_balance = jumbo_crate_balance_record[0].jumbo_balance
        
        response['normal_crate_balance'] = int(normal_crate_balance) 
        response['jumbo_crate_balance'] = int(jumbo_crate_balance)
    
    return JsonResponse(response,status = status_code)

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


@validateGET
@validate_logistic_api
def todayOrders(request):
    if 'date' in request.GET and request.GET['date'] != "":
        given_order_date = datetime.strptime(request.GET['date'], '%d/%m/%Y')
    else:
        given_order_date = datetime.now()
         
    
    response = {}
    status_code = 200
    api_token = request.headers['Authorization']
    vehicle = SpVehicles.objects.get(api_token=api_token)
    if vehicle.route_id is None:
        response['message'] = "Route is not assigned. please contact the administrator."
        status_code = 401
        
    else:
        route_id = vehicle.route_id
        today   = given_order_date
        
        user_list = SpUserAreaAllocations.objects.filter(route_id=route_id).values('id', 'user_id', 'route_id', 'route_name')
        user_lists = []
        for user in user_list:
            if getModelColumnById(SpUsers, user['user_id'], 'user_type') == 2:
                route_users = {}
                route_users['id']                 = user['user_id']
                route_users['username']           = getModelColumnById(SpUsers, user['user_id'], 'store_name')
                route_users['user_number']        = getModelColumnById(SpUsers, user['user_id'], 'primary_contact_number')
                route_users['route_name']         = getModelColumnByColumnId(SpUserAreaAllocations, 'user_id', user['user_id'], 'route_name')
                route_users['town_name']          = getModelColumnByColumnId(SpUserAreaAllocations, 'user_id', user['user_id'], 'town_name')

                try:
                    order = SpOrders.objects.filter(user_id=user['user_id'],order_date__icontains=today.strftime("%Y-%m-%d"),route_id=route_id,order_status__gt=2).values('id','user_id', 'order_code','town_name','route_name','user_name', 'order_date', 'order_status', 'order_total_amount', 'order_items_count').first()
                except SpOrders.DoesNotExist:
                    order = None
                
                if order:
                    today   = given_order_date
                    if SpTransporterCrateLedger.objects.filter(user_id=order['user_id'],updated_datetime__icontains=today.strftime("%Y-%m-%d")).exists():
                        current_order = {}
                        order_date = str(order['order_date']).replace('+00:00', '')
                        route_users['order_id']           = order['id']
                        route_users['order_date']         = datetime.strptime(str(order_date), '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y | %I:%M:%p')
                        route_users['order_code']         = order['order_code']
                        route_users['town_name']          = order['town_name']
                        route_users['user_name']          = order['user_name']
                        route_users['route_name']         = order['route_name']
                        route_users['order_status']       = order['order_status']
                        route_users['order_items_count']  = order['order_items_count']

                        order_item_list     = SpOrderDetails.objects.filter(order_id=order['id']).values('id','product_variant_size', 'order_id', 'product_id', 'product_name', 'product_variant_id', 'product_variant_name', 'quantity', 'rate', 'amount', 'order_date','product_container_type','packaging_type','product_packaging_type_name')
                        order_items = []
                        for order_item in order_item_list:
                            current_item = {}
                            container_name                          = SpProducts.objects.get(id=order_item['product_id'])
                            current_item['container_name']          = order_item['product_container_type']
                            current_item['product_class_name']      = container_name.product_class_name
                            current_item['product_name']            = order_item['product_name']
                            current_item['product_variant_name']    = order_item['product_variant_name']
                            current_item['quantity']                = order_item['quantity']
                            current_item['packaging_type']                = order_item['packaging_type']
                            current_item['product_packaging_type_name']   = order_item['product_packaging_type_name']
                            current_item['free_scheme']             = getFreeSchemes(order_item['product_variant_id'], order_item['order_id'], order['user_id'])
                            order_items.append(current_item)

                        route_users['order_item_list'] = order_items        
                        
                route_users['request_count']    = SpOrderCrateApproval.objects.filter(user_id=user['user_id'], updated_datetime__icontains=today.strftime("%Y-%m-%d")).count()  
                
                try:
                    crate_status = SpOrderCrateApproval.objects.filter(user_id=user['user_id'], updated_datetime__icontains=today.strftime("%Y-%m-%d")).order_by('-id').first()
                except SpOrderCrateApproval.DoesNotExist:
                    crate_status = None

                if crate_status:
                    route_users['request_status']    = crate_status.status
                else:
                    route_users['request_status']    = 0    
                user_lists.append(route_users)
        
        status_code = 200
        response['user_lists'] = user_lists
    

    return JsonResponse(response,status = status_code)



@csrf_exempt
@validatePOST
@validate_logistic_api
def saveTracking(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'latitude' not in received_data or received_data['latitude'] == "" :
        response['message'] = "Lattitude is missing"
        status_code = 404
    if 'longitude' not in received_data or received_data['longitude'] == "" :
        response['message'] = "Longitude is missing"
        status_code = 404


    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            if SpVehicleTracking.objects.filter(vehicle_id=vehicle.id).exists():
                vehicle_last_data = SpVehicleTracking.objects.filter(vehicle_id=vehicle.id).order_by('-id').first()
                R = 6373.0
                lat1 = radians(float(vehicle_last_data.latitude))
                lon1 = radians(float(vehicle_last_data.longitude))
                lat2 = radians(float(received_data["latitude"]))
                lon2 = radians(float(received_data["longitude"]))

                dlon = lon2 - lon1
                dlat = lat2 - lat1

                a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))

                distance = R * c
                meter_distance = float(distance * 1000)
                if meter_distance > 15 :
                    route_id = vehicle.route_id
                    driver_id = vehicle.driver_id
                    vehicle_tracking = SpVehicleTracking()
                    vehicle_tracking.vehicle_id = vehicle.id
                    vehicle_tracking.route_id = vehicle.route_id
                    vehicle_tracking.route_name = vehicle.route_name
                    vehicle_tracking.driver_id = vehicle.driver_id
                    vehicle_tracking.driver_name = vehicle.driver_name
                    vehicle_tracking.latitude = received_data['latitude']
                    vehicle_tracking.longitude = received_data['longitude']
                    vehicle_tracking.save()
                    
            else:
                route_id = vehicle.route_id
                driver_id = vehicle.driver_id
                vehicle_tracking = SpVehicleTracking()
                vehicle_tracking.vehicle_id = vehicle.id
                vehicle_tracking.route_id = vehicle.route_id
                vehicle_tracking.route_name = vehicle.route_name
                vehicle_tracking.driver_id = vehicle.driver_id
                vehicle_tracking.driver_name = vehicle.driver_name
                vehicle_tracking.latitude = received_data['latitude']
                vehicle_tracking.longitude = received_data['longitude']
                vehicle_tracking.save()

            response['message'] = "Data has been saved successfully."
            status_code = 200

    return JsonResponse(response,status = status_code)



@csrf_exempt
@validatePOST
@validate_logistic_api
def sendOrderOtp(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'order_id' not in received_data or received_data['order_id'] == "" :
        response['message'] = "Order# is missing"
        status_code = 404
    
    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            if SpOrders.objects.filter(id=received_data['order_id']).exists():
                order = SpOrders.objects.get(id=received_data['order_id'])
                if order.order_status < 4 :
                    SpOrderOtp.objects.filter(order_id=received_data['order_id'],vehicle_id=vehicle.id).delete()
                    
                    otp = generateOTP()
                    order_otp = SpOrderOtp()
                    order_otp.vehicle_id = vehicle.id
                    order_otp.order_id = received_data['order_id']
                    order_otp.otp = otp
                    order_otp.save()

                    if order_otp.id :
                        #send sms

                        today   = date.today()
                        message = "You are receiving "
                        crates = SpTransporterCrateLedger.objects.filter(user_id=order.user_id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).first()
                        
                        if int(crates.normal_credit) > 0 :
                            message += str(int(crates.normal_credit)) + " normal crate"
                        if int(crates.jumbo_credit) > 0 :
                            message += " and "+str(int(crates.jumbo_credit)) + " jumbo crate"
                        
                        primary_contact_number =  getModelColumnById(SpUsers,order.user_id,'primary_contact_number')
                        message += ". Share this OTP ("+ str(otp) +") with delivery boy for order & Crate verification."
                        print(message)
                        
                        # sendSMS('SAAHAJ',primary_contact_number,message)
                        #-----------------------------notify android block-------------------------------#
                        notification_image = ""
                        message_title = "Order OTP"
                        message_body = message
                        userFirebaseToken = getModelColumnById(SpUsers,order.user_id,'firebase_token')
                        user_name = getUserName(order.user_id)
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
                        saveNotification(None,None,'Order Management','Order Delivery',message_title,message_body,notification_image,order.user_id,user_name,order.user_id,user_name,'order.png',2,'app.png',1,1)
                        #-----------------------------save notification block----------------------------#

                        response['message'] = "OTP sent successfully."
                        status_code = 200
                    else:
                        response['message'] = "Server error occurred."
                        status_code = 500
                else:
                    response['message'] = "Server error occurred."
                    status_code = "Order already delivered. Please contact administrator."

            else:
                response['message'] = "Order not found."
                status_code = 404
    return JsonResponse(response,status = status_code)

@csrf_exempt
@validatePOST
@validate_logistic_api
def sendApprovalRequest(request):
    response = {}
    status_code = 200
    today   = date.today()
    received_data=json.loads(request.body)

    if 'user_id' not in received_data or received_data['user_id'] == "" :
        response['message'] = "User Id is missing"
        status_code = 404
    if 'received_normal' not in received_data or received_data['received_normal'] == "" :
        response['message'] = "Normal Crate Quantity is missing"
        status_code = 404
    if 'received_jumbo' not in received_data or received_data['received_jumbo'] == "" :
        response['message'] = "Jumbo Crate Quantity is missing"
        status_code = 404
    if SpOrderCrateApproval.objects.filter(user_id=received_data['user_id'], updated_datetime__icontains=today.strftime("%Y-%m-%d")).count() == 3:
        response['message'] = "You have accessed limit of approval, kindly contact administrator"
        status_code = 404
    if SpOrderCrateApproval.objects.filter(user_id=received_data['user_id'], updated_datetime__icontains=today.strftime("%Y-%m-%d"), status=2).count() > 0:
        response['message'] = "You request already approved"
        status_code = 404    
    
    if 'date' in received_data and received_data['date'] != "":
        given_order_date = datetime.strptime(received_data['date'], '%d/%m/%Y')
    else:
        given_order_date = datetime.now()
    
    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            try:
                crate = SpTransporterCrateLedger.objects.filter(user_id=received_data['user_id'], updated_datetime__icontains=given_order_date.strftime("%Y-%m-%d"), normal_credit__gt=0).exclude(plant_user_id=None).first()
            except SpTransporterCrateLedger.DoesNotExist:
                crate = None

            if crate:
                delivered_normal    = crate.normal_credit
                delivered_jumbo     = crate.jumbo_credit
            else:
                delivered_normal    = 0
                delivered_jumbo     = 0

            user_name = getUserName(received_data['user_id'])

            item                            = SpOrderCrateApproval()
            if 'order_id' not in received_data or received_data['order_id'] == "" :
                item.order_id                   = None
            else:
                item.order_id                   = received_data['order_id']
            item.transporter_id             = vehicle.id
            item.driver_id                  = vehicle.driver_id
            item.driver_name                = vehicle.driver_name
            item.user_id                    = received_data['user_id']
            item.user_name                  = user_name
            item.delivered_normal           = delivered_normal
            item.delivered_jumbo            = delivered_jumbo
            item.received_normal            = received_data['received_normal']
            item.received_jumbo             = received_data['received_jumbo'] 
            item.status                     = 1
            item.updated_datetime           = given_order_date.strftime('%Y-%m-%d %H:%M:%S')
            item.save()

            # sendSMS('SAAHAJ',primary_contact_number,message)
            #-----------------------------notify android block-------------------------------#
            registration_number = vehicle.registration_number
            transporter_details = vehicle.driver_name+'('+registration_number+')'

            notification_image = ""
            message_title = "Approval Request"
            message_body = "An Approval request has been sent by "+transporter_details+""
            userFirebaseToken = getModelColumnById(SpUsers,received_data['user_id'],'firebase_token')
            
            if userFirebaseToken is not None and userFirebaseToken != "" :
                registration_ids = []
                registration_ids.append(userFirebaseToken)
                data_message = {}
                data_message['id'] = 2
                data_message['status'] = 'notification'
                data_message['click_action'] = 'FLUTTER_NOTIFICATION_CLICK'
                data_message['image'] = notification_image
                send_android_notification(message_title,message_body,data_message,registration_ids)
                #-----------------------------notify android block-------------------------------#
            #-----------------------------save notification block----------------------------#
            saveNotification(None,None,'Order Management','Approval Request',message_title,message_body,notification_image,vehicle.id,transporter_details,received_data['user_id'],user_name,'order.png',2,'app.png',1,1)
            #-----------------------------save notification block----------------------------#
            
            response['message'] = "Approval Request sent successfully."
            status_code = 200

    return JsonResponse(response,status = status_code)
    
@csrf_exempt
@validatePOST
@validate_logistic_api
def deliverOrder(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'order_id' not in received_data or received_data['order_id'] == "" :
        response['message'] = "Order# is missing"
        status_code = 404
    if 'otp' not in received_data or received_data['otp'] == "" :
        response['message'] = "OTP is missing"
        status_code = 404
    approval_order = SpApprovalStatus.objects.filter(row_id=received_data['order_id']).order_by('-id').first()
    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if vehicle.route_id is None:
            response['message'] = "Route is not assigned. please contact the administrator."
            status_code = 401
        else:
            if SpOrders.objects.filter(id=received_data['order_id']).exists():
                order = SpOrders.objects.get(id=received_data['order_id'])
                if order.order_status < 4 :
                    if SpOrderOtp.objects.filter(order_id=received_data['order_id'],otp=received_data['otp'],vehicle_id=vehicle.id).exists():
                        
                        #update order status
                        order.order_status = 4
                        order.save()

                        if order.id :
                            #delete otp
                            SpOrderOtp.objects.filter(order_id=received_data['order_id'],vehicle_id=vehicle.id).delete()
                            if approval_order:
                                data                            = SpApprovalStatus()
                                data.row_id                     = received_data['order_id']
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

                            
                            
                            today   = date.today()
                            # update transporter ledger 
                            crate = SpTransporterCrateLedger.objects.filter(user_id=order.user_id,updated_datetime__icontains=today.strftime("%Y-%m-%d")).first()
                            if not SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).exists():
                                normal_balance = crate.normal_credit
                            else:
                                last_row = SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).order_by('-id').first()
                                normal_balance = int(crate.normal_credit) - int(last_row.normal_balance)

                            if not SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).exists():
                                jumbo_balance = crate.jumbo_credit
                            else:
                                last_row = SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).order_by('-id').first()
                                jumbo_balance = int(crate.jumbo_credit) - int(last_row.jumbo_balance)

                            item                            = SpTransporterCrateLedger()
                            item.transporter_id             = vehicle.id
                            item.driver_id                  = vehicle.driver_id
                            item.driver_name                = vehicle.driver_name
                            item.user_id                    = order.user_id
                            item.normal_credit              = 0
                            item.normal_debit               = crate.normal_credit
                            item.normal_balance             = normal_balance
                            item.jumbo_credit               = 0
                            item.jumbo_debit                = crate.jumbo_credit 
                            item.jumbo_balance              = jumbo_balance 
                            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            item.save()

                            # update distrubutor/superstockist ledger 
                            if not SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).exists():
                                normal_balance = crate.normal_credit
                            else:
                                last_row = SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).order_by('-id').first()
                                normal_balance = int(crate.normal_credit) + int(last_row.normal_balance)

                            if not SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).exists():
                                jumbo_balance = crate.jumbo_credit
                            else:
                                last_row = SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=order.user_id).order_by('-id').first()
                                jumbo_balance = int(crate.jumbo_credit) + int(last_row.jumbo_balance)

                            item                            = SpUserCrateLedger()
                            item.transporter_id             = vehicle.id
                            item.driver_id                  = vehicle.driver_id
                            item.driver_name                = vehicle.driver_name
                            item.user_id                    = order.user_id
                            item.normal_credit              = crate.normal_credit
                            item.normal_debit               = 0
                            item.normal_balance             = normal_balance
                            item.jumbo_credit               = crate.jumbo_credit 
                            item.jumbo_debit                = 0
                            item.jumbo_balance              = jumbo_balance 
                            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            item.save()    
                             
                            #send sms
                            primary_contact_number =  getModelColumnById(SpUsers,order.user_id,'primary_contact_number')
                            message = "Your order("+ str(order.order_code) +") has been delivered successfully."
                            sendSMS('ENQARY',primary_contact_number,message)

                            #-----------------------------notify android block-------------------------------#
                            notification_image = ""
                            message_title = "Order Delivered"
                            crate_message = ''
                            if int(crate.normal_credit) > 0:
                                crate_message+=str(int(crate.normal_credit))+" normal"
                            if int(crate.jumbo_credit) > 0:
                                crate_message+=str(int(crate.jumbo_credit))+" jambo "

                            message = "An order ("+ str(order.order_code) +") has been delivered by "+vehicle.driver_name+" with "+crate_message+" crate"
                            message_body = message

                            userFirebaseToken = getModelColumnById(SpUsers,order.user_id,'firebase_token')
                            user_name = getUserName(order.user_id)
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
                            saveNotification(None,None,'Order Management','Order Delivery',message_title,message_body,notification_image,order.user_id,user_name,order.user_id,user_name,'order.png',2,'app.png',1,1)
                            #-----------------------------save notification block----------------------------#

                            # save activity
                            user_name = vehicle.registration_number
                            heading = 'Order('+order.order_code+') has been delivered'
                            activity = 'Order('+order.order_code+') has been delivered from vehicle '+vehicle.registration_number+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p')
                            saveActivity('Order Management', 'Order Delivery', heading, activity, vehicle.id, user_name, 'updateVehiclePass.png', '2', 'app.png')

                            response['message'] = "Order delivered successfully."
                            status_code = 200
                        else:
                            response['message'] = "Server error occurred."
                            status_code = 500
                    else:
                        response['message'] = "Invalid OTP."
                        status_code = 400

                else:
                    response['message'] = "Order already delivered. Please contact administrator."
                    status_code = 200

            else:
                response['message'] = "Order not found."
                status_code = 404
            

    return JsonResponse(response,status = status_code)

#get superstockist list used for receive crates
@csrf_exempt
@validatePOST
@validate_logistic_api
def getUserList(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'route_id' not in received_data or received_data['route_id'] == "" :
        response['message'] = "Route is required"
        status_code = 404

    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        try:
            driver_details = SpVehicles.objects.get(route_id=received_data['route_id'])
        except SpVehicles.DoesNotExist:
            driver_details = None
            
        if driver_details is None:
            response['message'] = "No Driver assigned on this route"
            status_code = 200
            return JsonResponse(response,status = status_code)

        user_list = SpUserAreaAllocations.objects.filter(route_id=received_data['route_id']).values('id', 'user_id', 'route_id', 'route_name')
        user_lists = []
        for user in user_list:
            # today   = date.today()
            # if SpTransporterCrateLedger.objects.filter(user_id=user['id'],updated_datetime__icontains=today.strftime("%Y-%m-%d")).exists():
            route_users = {}
            route_users['id']       = user['id']
            route_users['user_id']  = user['user_id']
            route_users['username'] = getModelColumnById(SpUsers, user['user_id'], 'first_name')+' '+getModelColumnById(SpUsers, user['user_id'], 'middle_name')+' '+getModelColumnById(SpUsers, user['user_id'], 'last_name')
            user_lists.append(route_users)
        

        response['vehicle_id']               = driver_details.id
        response['driver_id']                = driver_details.driver_id
        response['driver_name']              = driver_details.driver_name
        response['driver_contact_no']        = getModelColumnById(SpDrivers, driver_details.driver_id, 'primary_contact_number')
        response['user_list']                = user_lists
        response['message']                  = 'Success'
        response['response_code']            = 200
        
    return JsonResponse(response,status = status_code)

# send otp to superstockist for dispatching crates
@csrf_exempt
@validatePOST
@validate_logistic_api
def sendOtp(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    
    if 'normal_crate' not in received_data or received_data['normal_crate'] == "" :
        response['message'] = "Please provide normal crate"
        status_code = 404
    
    if 'jumbo_crate' not in received_data or received_data['jumbo_crate'] == "" :
        response['message'] = "Please provide jumbo crate"
        status_code = 404
    
    if 'user_id' not in received_data or received_data['user_id'] == "" :
        response['message'] = "Please provide user id."
        status_code = 404
    
    if status_code == 200 :
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)


        try:
            vehicle_details = SpVehicles.objects.filter(id=vehicle.id, status=1).first()
        except SpVehicles.DoesNotExist:
            vehicle_details = None

        
        if not vehicle_details:
            response['message']    = "Invalid vehicle id"
            response['response_code']    = 200
            return JsonResponse(response,status = 200)

        otp = generateOTP()
        SpOrderOtp.objects.filter(vehicle_id=vehicle.id).delete()
        user_otp                = SpOrderOtp()
        user_otp.vehicle_id     = vehicle.id
        user_otp.order_id       = received_data['user_id']
        user_otp.otp            = otp
        user_otp.save()
        #send sms
        message = "You are giving "
        if int(received_data['normal_crate']) > 0 :
            message += str(int(received_data['normal_crate'])) + " normal crate"
        if int(received_data['jumbo_crate']) > 0 :
            message += " and "+str(int(received_data['jumbo_crate'])) + " Jumbo crate"

        message += ". share this OTP ("+ str(otp) +") to confirm the transaction."
        #-----------------------------notify android block-------------------------------#
        notification_image = ""
        message_title = "Crate Handover OTP"
        message_body = message

        userFirebaseToken = getModelColumnById(SpUsers,received_data['user_id'],'firebase_token')
        user_name = getUserName(received_data['user_id'])
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
        saveNotification(None,None,'Order Management','Crate Handover',message_title,message_body,notification_image,received_data['user_id'],user_name,received_data['user_id'],user_name,'order.png',2,'app.png',1,1)
        #-----------------------------save notification block----------------------------#

        mobile_number = getModelColumnById(SpUsers,received_data['user_id'],'primary_contact_number')
        
        if mobile_number is not None and mobile_number != "":
            sendSMS('SAAHAJ',mobile_number,message)

            response['message']          = 'OTP sent successfully'
            response['otp']              = otp
            response['response_code']    = 200

    return JsonResponse(response,status = status_code)

# send otp to superstockist for dispatching crates
@csrf_exempt
@validatePOST
@validate_logistic_api
def receiveCrates(request):
    response = {}
    status_code = 200

    received_data=json.loads(request.body)
    if 'normal_crate' not in received_data or received_data['normal_crate'] == "" :
        response['message'] = "Please provide normal crate"
        status_code = 404
    
    if 'jumbo_crate' not in received_data or received_data['jumbo_crate'] == "" :
        response['message'] = "Please provide jumbo crate"
        status_code = 404
    
    if 'user_id' not in received_data or received_data['user_id'] == "" :
        response['message'] = "Please provide user id."
        status_code = 404
    
    if 'otp' not in received_data or received_data['otp'] == "" :
        response['message'] = "Please provide OTP."
        status_code = 404
    
    if status_code == 200:
        api_token = request.headers['Authorization']
        vehicle = SpVehicles.objects.get(api_token=api_token)

        if SpOrderOtp.objects.filter(vehicle_id=vehicle.id,order_id=received_data['user_id']).exists():
            today   = date.today()
            # update transporter ledger 
            if not SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).exists():
                normal_balance = received_data['normal_crate']
            else:
                last_row = SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).order_by('-id').first()
                normal_balance = int(received_data['normal_crate']) + int(last_row.normal_balance)

            if not SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).exists():
                jumbo_balance = received_data['jumbo_crate']
            else:
                last_row = SpTransporterCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).order_by('-id').first()
                jumbo_balance = int(received_data['jumbo_crate']) + int(last_row.jumbo_balance)

            item                            = SpTransporterCrateLedger()
            item.transporter_id             = vehicle.id
            item.driver_id                  = vehicle.driver_id
            item.driver_name                = vehicle.driver_name
            item.user_id                    = received_data['user_id']
            item.normal_credit              = received_data['normal_crate']
            item.normal_debit               = 0
            item.normal_balance             = normal_balance
            item.jumbo_credit               = received_data['jumbo_crate']
            item.jumbo_debit                = 0 
            item.jumbo_balance              = jumbo_balance 
            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item.save()

            # update distrubutor/superstockist ledger 
            if not SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).exists():
                normal_balance = received_data['normal_crate']
            else:
                last_row = SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).order_by('-id').first()
                normal_balance = int(received_data['normal_crate']) - int(last_row.normal_balance)

            if not SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).exists():
                jumbo_balance = received_data['jumbo_crate']
            else:
                last_row = SpUserCrateLedger.objects.filter(transporter_id=vehicle.id, user_id=received_data['user_id']).order_by('-id').first()
                jumbo_balance = int(received_data['jumbo_crate']) - int(last_row.jumbo_balance)

            item                            = SpUserCrateLedger()
            item.transporter_id             = vehicle.id
            item.driver_id                  = vehicle.driver_id
            item.driver_name                = vehicle.driver_name
            item.user_id                    = received_data['user_id']
            item.normal_credit              = 0
            item.normal_debit               = received_data['normal_crate']
            item.normal_balance             = normal_balance
            item.jumbo_credit               = 0
            item.jumbo_debit                = received_data['jumbo_crate'] 
            item.jumbo_balance              = jumbo_balance 
            item.updated_datetime           = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item.save()

            #-----------------------------notify android block-------------------------------#
            userFirebaseToken = getModelColumnById(SpUsers,received_data['user_id'],'firebase_token')
            user_name = getUserName(received_data['user_id'])
            if userFirebaseToken is not None and userFirebaseToken != "" :
                notification_image = ""
                message_title = "Crate Handover"
                message_body = 'Crate handover done successfully.'
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
                saveNotification(None,None,'Order Management','Crate Handover',message_title,message_body,notification_image,received_data['user_id'],user_name,received_data['user_id'],user_name,'order.png',2,'app.png',1,1)
                #-----------------------------save notification block----------------------------#

            response['message'] = "Crate Received successfully"
        else:
            response['message'] = "Invalid OTP."
            status_code = 404


    return JsonResponse(response,status = status_code)


@csrf_exempt
@validate_logistic_api
def notificationList(request):
    response = {}
    status_code = 200

    api_token = request.headers['Authorization']
    vehicle = SpVehicles.objects.get(api_token=api_token)

    try:
        notification_list = SpNotifications.objects.filter(to_user_id=vehicle.id,to_user_type=2).values('id','row_id','model_name', 'heading', 'activity', 'activity_image', 'from_user_id', 'from_user_name', 'icon', 'platform_icon', 'read_status', 'created_at').order_by('-id')
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

    notification_count = SpNotifications.objects.filter(to_user_id=vehicle.id,to_user_type=2).values('id').count()
    if notification_count is not None:
        notification_count = math.ceil(round(notification_count/10, 2))
    else:
        notification_count = 0

    response['message']              = 'Success'
    response['notification_list']    = list(notification_list)
    response['notification_count']    = notification_count
    response['response_code']        = 200

    return JsonResponse(response,status = status_code)