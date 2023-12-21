import json
import time
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
from datetime import datetime,date
from datetime import timedelta
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import make_password, check_password
from math import sin, cos, sqrt, atan2, radians
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    user_type = request.data.get("user_type")
    if request.data.get("username") == '':  
        return Response({'message': 'Please provide username', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("password") == '':
        return Response({'message': 'Please provide password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)     
    if request.data.get("username") is None or request.data.get("password") is None:
        return Response({'message': 'Please provide both username and password', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if not user_type:
        return Response({'message': 'User type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    if user_type == '0':
        try:
            user_details = SpUsers.objects.filter(status=1, user_type=2, emp_sap_id=request.data.get("username")).first()
        except SpUsers.DoesNotExist:
            user_details = None
        if user_details:
            username = user_details.emp_sap_id
        else:        
            username = None
        error_msg = 'Invalid SAP Id'
        if not user_details:
            return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    else:
        if user_type == '1':
            try:
                user_details = SpUsers.objects.filter(status=1, user_type=1, official_email=request.data.get("username")).first()
            except SpUsers.DoesNotExist:
                user_details = None
        else:
            try:
                user_details = SpUsers.objects.filter(status=1, user_type=1, official_email=request.data.get("username"), role_id=50).first()
            except SpUsers.DoesNotExist:
                user_details = None
        if user_details:
            username = request.data.get("username")
        else:        
            username = None
        error_msg = 'Invalid Email Id'
        if not user_details:
            return Response({'message': error_msg, 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
        
      
    username = username
    password = request.data.get("password")
    
    if user_type == '0':
        if check_password(password, user_details.password):
            user = user_details
        else:    
            user = None
    else:
        user = authenticate(username=username, password=password)
    if not user:
        return Response({'message': 'Invalid Credentials', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    user_details = SpUsers.objects.filter(status=1, id=user.id).values()
    try:
        user_basic_details = model_to_dict(SpBasicDetails.objects.get(user_id=user.id))
    except SpBasicDetails.DoesNotExist:
        user_basic_details = []
    try:
        user_correspondence_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='correspondence'))
    except SpAddresses.DoesNotExist:
        user_correspondence_details = []
    try:
        user_permanent_details = model_to_dict(SpAddresses.objects.get(user_id=user.id,type='permanent'))
    except SpAddresses.DoesNotExist:
        user_permanent_details = []
    user_name   = user.first_name+' '+user.middle_name+' '+user.last_name
    heading     = user_name+' has been logged In'
    activity    = user_name+' has been logged In on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Login', 'Login', heading, activity, user.id, user_name, 'login.png', '2', 'app.png')
    
    if request.data.get("device_id") != '' :
        current_user = SpUsers.objects.get(id=user.id)
        current_user.device_id = request.data.get("device_id")
        current_user.save()
    
    if getModelColumnById(SpUsers, user.id, 'latitude')is None or getModelColumnById(SpUsers, user.id, 'latitude') == '':
        latitude = '' 
    else:
        latitude = getModelColumnById(SpUsers, user.id, 'latitude')

    if getModelColumnById(SpUsers, user.id, 'longitude')is None or getModelColumnById(SpUsers, user.id, 'longitude') == '':
        longitude = ''
    else:
        longitude = getModelColumnById(SpUsers, user.id, 'longitude')

    if getModelColumnById(SpUsers, user.id, 'periphery')is None or getModelColumnById(SpUsers, user.id, 'periphery') == '':
        periphery = ''
    else:
        periphery = getModelColumnById(SpUsers, user.id, 'periphery')

    if getModelColumnById(SpUsers, user.id, 'timing')is None or getModelColumnById(SpUsers, user.id, 'timing') == '':
        timing = ''
    else:
        timing = getModelColumnById(SpUsers, user.id, 'timing')
    
    #update
    if request.data.get("firebase_token") != "":
        SpUsers.objects.filter(id=user.id).update(firebase_token=request.data.get("firebase_token"))
    
        
    context = {}
    context['token']                    = token.key
    context['user_details']             = user_details
    context['basic_details']            = user_basic_details
    context['correspondence_address']   = user_correspondence_details
    context['permanent_address']        = user_permanent_details
    context['app_version']              = model_to_dict(SpAppVersions.objects.get())
    context['state_list']               = SpStates.objects.all().values('id', 'state')
    context['city_list']                = SpCities.objects.all().values('id', 'state_id', 'city')
    context['reason_list']              = SpReasons.objects.all().values('id', 'reason')
    context['latitude']                 = latitude
    context['longitude']                = longitude
    context['periphery']                = periphery
    context['timing']                   = timing
    context['message']                  = 'Login successfully'
    context['tracking_time']            = getModelColumnById(Configuration, 1, 'user_tracking_time')
    context['mark_attendance_time']     = getModelColumnById(Configuration, 1, 'mark_attendance_time')
    context['battery_percentage']       = getConfigurationResult('battery_percentage')
    context['contact_number']           = getConfigurationResult('contact_number')
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def updateUserLocation(request):
    
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("latitude")is None or request.data.get("latitude") == '':
        return Response({'message': 'Latitude field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("longitude")is None or request.data.get("longitude") == '':
        return Response({'message': 'Longitude field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  


    user                = SpUsers.objects.get(id=request.data.get("user_id"))
    user.latitude       = request.data.get("latitude")
    user.longitude      = request.data.get("longitude")
    user.periphery      = '500'
    user.timing         = '6:00 AM'
    user.save()

    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Location has been updated'
    activity    = 'Location has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Location', 'Location updated', heading, activity, request.user.id, user_name, 'UserCredentialChange.png', '2', 'app.png')

    context = {}
    context['latitude']     = request.data.get("latitude")
    context['longitude']    = request.data.get("longitude")
    context['periphery']    = '500'
    context['timing']       = '6:00 AM'
    context['message']      = 'Location has been successfully updated'
    context['response_code'] = HTTP_200_OK
    
    return Response(context, status=HTTP_200_OK)
    
@csrf_exempt
@api_view(["POST"])
def updateUserPassword(request):
    
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("old_password")is None or request.data.get("old_password") == '':
        return Response({'message': 'Old Password field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("new_password")is None or request.data.get("new_password") == '':
        return Response({'message': 'New Password field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    user_details = SpUsers.objects.get(id=request.data.get("user_id"))    
    if not check_password(request.data.get("old_password"), user_details.password):
        return Response({'message': 'Old Password incorrect', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    user                = SpUsers.objects.get(id=request.data.get("user_id"))
    user.password       = make_password(str(request.data.get("new_password")))
    user.save()
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Password has been updated'
    activity    = 'Password has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Change Password', 'Change Password', heading, activity, request.user.id, user_name, 'UserCredentialChange.png', '2', 'app.png')
    context = {}
    context['message'] = 'Password has been successfully updated'
    context['response_code'] = HTTP_200_OK
    
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def logout(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    AuthtokenToken.objects.filter(user_id=request.user.id).delete()

    # clear firebase token
    SpUsers.objects.filter(id=request.user.id).update(firebase_token=None)
    
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = user_name+' has been logout'
    activity    = user_name+' has been logout on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Logout', 'Logout', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
    context = {}
    context['message'] = 'Logout successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def updateUserProfile(request):
    user_exists = SpUsers.objects.filter(official_email=request.data.get("official_email")).exclude(id=request.data.get("user_id")).exists()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("gender")is None or request.data.get("gender") == '':
        return Response({'message': 'Gender field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("date_of_birth")is None or request.data.get("date_of_birth") == '':
        return Response({'message': 'Date of birth field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("contact_number")is None or request.data.get("contact_number") == '':
        return Response({'message': 'Contact No. field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    # if request.data.get("official_email")is None or request.data.get("official_email") == '':
    #     return Response({'message': 'Email id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if request.data.get("official_email")!='' and user_exists:
        return Response({'message': 'Email id already exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)            
    if request.data.get("store_address_line_1")is None or request.data.get("store_address_line_1") == '':
        return Response({'message': 'Store Address field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_state_id")is None or request.data.get("store_state_id") == '':
        return Response({'message': 'Store State field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_city_id")is None or request.data.get("store_city_id") == '':
        return Response({'message': 'Store City field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("store_pincode")is None or request.data.get("store_pincode") == '':
        return Response({'message': 'Store Pincode field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("permanent_address_line_1")is None or request.data.get("permanent_address_line_1") == '':
        return Response({'message': 'Permanent Address field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_state_id")is None or request.data.get("permanent_state_id") == '':
        return Response({'message': 'Permanent State field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_city_id")is None or request.data.get("permanent_city_id") == '':
        return Response({'message': 'Permanent City field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("permanent_pincode")is None or request.data.get("permanent_pincode") == '':
        return Response({'message': 'Permanent Pincode field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)          
    if bool(request.FILES.get('profile_image', False)) == True:
        uploaded_profile_image = request.FILES['profile_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        profile_image_name = uploaded_profile_image.name
        temp = profile_image_name.split('.')
        profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        profile_image = storage.save(profile_image_name, uploaded_profile_image)
        profile_image = storage.url(profile_image)        
            
    user                        = SpUsers.objects.get(id=request.data.get("user_id"))
    user.official_email         = request.data.get('official_email')
    if bool(request.FILES.get('profile_image', False)) == True:
        if user.profile_image:
            deleteMediaFile(user.profile_image)
        user.profile_image          = profile_image
    user.primary_contact_number = request.data.get('contact_number')
    user.save()
    try:
        user_basic_detail = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    except SpBasicDetails.DoesNotExist:
        user_basic_detail = None
    if user_basic_detail:
        user_basic_details = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    else:
        user_basic_details = SpBasicDetails()
        
    user_basic_details.user_id          = request.data.get("user_id")
    user_basic_details.date_of_birth    = datetime.strptime(request.data.get('date_of_birth'), '%d/%m/%Y').strftime('%Y-%m-%d')
    user_basic_details.gender           = request.data.get('gender')
    user_basic_details.blood_group      = request.data.get('blood_group')
    user_basic_details.save()
    try:
        user_contact_nos = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    except SpContactNumbers.DoesNotExist:
        user_contact_nos = None
    if user_contact_nos:
        user_contact_no = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    else:
        user_contact_no = SpContactNumbers()
    user_contact_no.user_id         = request.data.get("user_id")    
    user_contact_no.contact_number  = request.data.get('contact_number')
    user_contact_no.save()
    SpAddresses.objects.filter(user_id=request.data.get("user_id")).delete()
    correspondence = SpAddresses()
    correspondence.user_id          = request.data.get("user_id")
    correspondence.type             = 'correspondence'
    correspondence.address_line_1   = request.data.get('store_address_line_1')
    correspondence.address_line_2   = request.data.get('store_address_line_2')
    correspondence.country_id       = 1
    correspondence.country_name     = getModelColumnById(SpCountries, 1,'country')
    correspondence.state_id         = request.data.get('store_state_id')
    correspondence.state_name       = getModelColumnById(SpStates, request.data.get('store_state_id'),'state')
    correspondence.city_id          = request.data.get('store_city_id')
    correspondence.city_name        = getModelColumnById(SpCities, request.data.get('store_city_id'),'city')
    correspondence.pincode          = request.data.get('store_pincode')
    correspondence.save()
    permanent = SpAddresses()
    permanent.user_id               = request.data.get("user_id")
    permanent.type                  = 'permanent'
    permanent.address_line_1        = request.data.get('permanent_address_line_1')
    permanent.address_line_2        = request.data.get('permanent_address_line_2')
    permanent.country_id            = 1
    permanent.country_name          = getModelColumnById(SpCountries, 1,'country')
    permanent.state_id              = request.data.get('permanent_state_id')
    permanent.state_name            = getModelColumnById(SpStates, request.data.get('permanent_state_id'),'state')
    permanent.city_id               = request.data.get('permanent_city_id')
    permanent.city_name             = getModelColumnById(SpCities, request.data.get('permanent_city_id'),'city')
    permanent.pincode               = request.data.get('permanent_pincode')
    permanent.save()
    user                            = SpUsers.objects.get(id=request.data.get("user_id"))
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = 'Profile has been updated'
    activity    = 'Profile has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Profile Updated', 'Profile Updated', heading, activity, request.user.id, user_name, 'profileUpdated.png', '2', 'app.png')
    context = {}
    context['profile_image'] =  user.profile_image
    context['message']       = 'Profile has been updated successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def checkAttendance(request):
    today   = date.today()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    context = {}
    if SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).exists():
        start_data      = SpUserAttendance.objects.filter(start_time__isnull=False,attendance_date_time__icontains=today.strftime("%Y-%m-%d"),user_id=request.data.get("user_id")).order_by('id').first()
        end_data        = SpUserAttendance.objects.filter(end_time__isnull=False,attendance_date_time__icontains=today.strftime("%Y-%m-%d"),user_id=request.data.get("user_id")).order_by('-id').first()
        user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=request.data.get("user_id")).order_by('-id').first()
        if user_attendance.start_time is not None and user_attendance.end_time is None:
            context['status'] = 1
        elif user_attendance.start_time is None and user_attendance.end_time is not None:
            context['status'] = 0
        else:
            context['status'] = 0
        now = datetime.now().strftime('%Y-%m-%d')
        start_datetime = now + ' '+start_data.start_time
        if context['status'] == 0:
            end_datetime = now + ' '+end_data.end_time
        else:
            end_datetime = now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M:%S')
        end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M:%S')
        time_delta = (end_datetime - start_datetime)
        # total_seconds = time_delta.total_seconds()
        # hours = (total_seconds/60)/60
        time_delta = str(time_delta).split(':')
        time_delta = time_delta[0]+':'+time_delta[1]
        context['working_hours'] = str(time_delta) + ' hours'
    else:
        context['status'] = 0
        context['working_hours'] = ''
        
    if getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')is None or getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery') == '':
        periphery = '500'
    else:
        periphery = getModelColumnById(SpUsers, request.data.get("user_id"), 'periphery')

    if getModelColumnById(SpUsers, request.data.get("user_id"), 'timing')is None or getModelColumnById(SpUsers, request.data.get("user_id"), 'timing') == '':
        timing = ''
    else:
        timing = getModelColumnById(SpUsers, request.data.get("user_id"), 'timing')

    context['periphery']     = periphery
    context['timing']        = timing     
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def userAttendance(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("type")is None or request.data.get("type") == '':
        return Response({'message': 'Attendance type is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("attendance_date_time")is None or request.data.get("attendance_date_time") == '':
        return Response({'message': 'Attendance DateTime field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    # if int(request.data.get("type")) == 1:
        
    #     if request.data.get("dis_ss_id") is None or request.data.get("dis_ss_id") == '':
    #         return Response({'message': 'Dis/SS id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)      
    
    data = SpUserAttendance()
    data.user_id = request.data.get("user_id")
    data.attendance_date_time = request.data.get("attendance_date_time")
    now = datetime.now().strftime('%H:%M:%S')
    if request.data.get("type") == '1':
        data.start_time = now
        data.end_time = None
    else:
        data.start_time = None
        data.end_time = now
    
    if int(request.data.get("type")) == 1:
        data.dis_ss_id = request.data.get("user_id")

    if request.data.get("latitude") is None or request.data.get("latitude") == '':
        data.latitude = None
    else:
        data.latitude = request.data.get("latitude")
    
    if request.data.get("longitude") is None or request.data.get("longitude") == '':
        data.longitude = None
    else:
        data.longitude = request.data.get("longitude")
        
    data.status = 1
    data.save()
    
    # save tracking

    if (request.data.get("latitude") is not None and request.data.get("latitude") != '') and (request.data.get("longitude") is not None and request.data.get("longitude") != ''):

        if SpUserTracking.objects.filter(user_id=request.data.get("user_id")).exists():
            
            user_last_data = SpUserTracking.objects.filter(user_id=request.data.get("user_id")).order_by('-id').first()
            
            R = 6373.0
            lat1 = radians(float(user_last_data.latitude))
            lon1 = radians(float(user_last_data.longitude))
            lat2 = radians(float(request.data.get("latitude")))
            lon2 = radians(float(request.data.get("longitude")))
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            distance = R * c
            meter_distance = float(distance * 1000)
            if meter_distance > 15 :
                user_data                       = SpUserTracking()
                user_data.user_id               = request.data.get("user_id")
                user_data.latitude              = request.data.get("latitude")
                user_data.longitude             = request.data.get("longitude")
                user_data.distance_travelled    = meter_distance
                user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
                user_data.save()
        else:
            user_data                       = SpUserTracking()
            user_data.user_id               = request.data.get("user_id")
            user_data.latitude              = request.data.get("latitude")
            user_data.longitude             = request.data.get("longitude")
            user_data.distance_travelled    = 0
            user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
            user_data.save()
            
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = user_name+' attendance marked successfully'
    activity    = user_name+' attendance marked successfully on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('User Attendance', 'User Attendance', heading, activity, request.user.id, user_name, 'markedAtten.png', '2', 'app.png')


    context = {}
    context['message'] = 'Attendance marked successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
    
@csrf_exempt
@api_view(["POST"])
def userLocations(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    
    user_location = SpUserAttendanceLocations.objects.filter(user_id=request.data.get("user_id")).values('distributor_ss_id', 'distributor_ss_name', 'periphery')   
    for location in user_location:
        location['store_name']  = getModelColumnById(SpUsers, location['distributor_ss_id'], 'store_name')
        location['latitude']    = getModelColumnById(SpUsers, location['distributor_ss_id'], 'latitude')
        location['longitude']   = getModelColumnById(SpUsers, location['distributor_ss_id'], 'longitude')
    context = {}
    context['message']          = 'Success'
    context['user_location']    = user_location
    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)         
@csrf_exempt
@api_view(["POST"])
def userList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    page_limit  = int(request.data.get("page_limit"))*10
    offset      = int(page_limit)-10
    page_limit  = 10

    user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id')
    user_list = []   
    for area_allocation in user_area_allocation:

        operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.user_type!=%s and sp_users.status=%s order by sp_users.first_name asc''', [area_allocation['town_id'], 1, 1])
        operational_user_list_count = len(operational_user_list)
        operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.user_type!=%s and sp_users.status=%s order by sp_users.first_name asc Limit %s OFFSET %s ''', [area_allocation['town_id'], 1, 1,page_limit, offset])
        if operational_user_list: 
            for operational_user in operational_user_list:
                users_list = {}
                users_list['id']                    = operational_user.user_id
                users_list['name']                  = operational_user.first_name+' '+operational_user.middle_name+' '+operational_user.last_name
                users_list['contact_no']            = operational_user.primary_contact_number
                users_list['role_id']               = operational_user.role_id
                users_list['role']                  = getModelColumnById(SpRoles, operational_user.role_id, 'role_name')
                users_list['is_tagged']             = operational_user.is_tagged
                if operational_user.store_name:
                    users_list['store_name']            = operational_user.store_name
                else:
                    users_list['store_name']            = ''    
                users_list['user_type']             = operational_user.user_type
                if operational_user.reporting_to_id:
                    users_list['reporting_to_id']       = str(operational_user.reporting_to_id)
                else:
                    users_list['reporting_to_id']       = ''
                users_list['reporting_to_name']     = operational_user.reporting_to_name
                user_list.append(users_list)
    
    zone_list  = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('zone_id', 'zone_name')
    town_list  = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id', 'town_name')
    route_list = SpRoutes.objects.filter(status=1).values('id', 'route')
    for town in town_list:
        town['zone_id'] = getModelColumnById(SpTowns, town['town_id'], 'zone_id')
    context = {}
    context['message']          = 'Success'
    context['user_list']        = user_list
    
    if operational_user_list_count:
        user_list_count = math.ceil(round(operational_user_list_count/10, 2))
    else:
        user_list_count = 0 

    context['user_list_count']        = user_list_count
    context['zone_list']        = zone_list
    context['town_list']        = town_list
    context['route_list']       = route_list
    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
def unTaggedUserList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   

    user_role = getModelColumnById(SpUsers,request.data.get("user_id"),'role_id')
    if user_role == 5:
        user_type = 3
    else:
        user_type = 2
        
    user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id')
    user_list = []   
    for area_allocation in user_area_allocation:

        operational_user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.user_type=%s and sp_users.status=%s order by sp_users.first_name asc ''', [area_allocation['town_id'], user_type, 1])
        if operational_user_list: 
            for operational_user in operational_user_list:
                users_list = {}
                users_list['id']                    = operational_user.user_id
                users_list['name']                  = operational_user.first_name+' '+operational_user.middle_name+' '+operational_user.last_name
                users_list['contact_no']            = operational_user.primary_contact_number
                users_list['role_id']               = operational_user.role_id
                users_list['role']                  = getModelColumnById(SpRoles, operational_user.role_id, 'role_name')
                users_list['is_tagged']             = operational_user.is_tagged
                if operational_user.store_name:
                    users_list['store_name']            = operational_user.store_name
                else:
                    users_list['store_name']            = ''    
                users_list['user_type']             = operational_user.user_type
                if operational_user.reporting_to_id:
                    users_list['reporting_to_id']       = str(operational_user.reporting_to_id)
                else:
                    users_list['reporting_to_id']       = ''
                users_list['reporting_to_name']     = operational_user.reporting_to_name
                user_list.append(users_list)
    
    zone_list  = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('zone_id', 'zone_name')
    town_list  = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id', 'town_name')
    route_list = SpRoutes.objects.filter(status=1).values('id', 'route')
    for town in town_list:
        town['zone_id'] = getModelColumnById(SpTowns, town['town_id'], 'zone_id')
    context = {}
    context['message']          = 'Success'
    context['user_list']        = user_list

    context['zone_list']        = zone_list
    context['town_list']        = town_list
    context['route_list']       = route_list
    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def saveUser(request):
    user_exists = SpUsers.objects.filter(primary_contact_number=request.data.get("contact_no")).exists()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    if request.data.get("contact_no")!='' and user_exists:
        return Response({'message': 'Contact No. already exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("store_name")is None or request.data.get("store_name") == '':
        return Response({'message': 'Store Name field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("user_type")is None or request.data.get("user_type") == '':
        return Response({'message': 'User Type field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("role_id")is None or request.data.get("role_id") == '':
        return Response({'message': 'Role Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("first_name")is None or request.data.get("first_name") == '':
        return Response({'message': 'First Name field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("last_name")is None or request.data.get("last_name") == '':
        return Response({'message': 'Last Name field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("contact_no")is None or request.data.get("contact_no") == '':
        return Response({'message': 'Contact No. field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("gender")is None or request.data.get("gender") == '':
        return Response({'message': 'Gender field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("date_of_birth")is None or request.data.get("date_of_birth") == '':
        return Response({'message': 'Date of birth field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("saddress_line_1")is None or request.data.get("saddress_line_1") == '':
        return Response({'message': 'Store Address field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if request.data.get("sstate_id")is None or request.data.get("sstate_id") == '':
        return Response({'message': 'Store State is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("scity_id")is None or request.data.get("scity_id") == '':
        return Response({'message': 'Store City is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("zone_id")is None or request.data.get("zone_id") == '':
        return Response({'message': 'Zone field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
             
    if request.data.get("town_id")is None or request.data.get("town_id") == '':
        return Response({'message': 'Town field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("route_id")is None or request.data.get("route_id") == '':
        return Response({'message': 'Route field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
        
    password                        = '123456'
    user                            = SpUsers()
    user.self_owned                 = request.data.get("self_owned")
    user.store_name                 = request.data.get("store_name")
    user.user_type                  = request.data.get("user_type")
    if request.data.get("reporting_to_id"):
        user.reporting_to_id   = request.data.get("reporting_to_id")
        user.reporting_to_name = getModelColumnById(SpUsers,request.data.get("reporting_to_id"),'first_name')+' '+getModelColumnById(SpUsers,request.data.get("reporting_to_id"),'middle_name')+' '+getModelColumnById(SpUsers,request.data.get("reporting_to_id"),'last_name')
    user.first_name                 = request.data.get("first_name")
    user.middle_name                = request.data.get("middle_name")
    user.last_name                  = request.data.get("last_name")
    user.primary_contact_number     = request.data.get("contact_no")
    user.official_email             = request.data.get("official_email")
    user.password                   = make_password(str(password))
    user.organization_id            = 1
    user.organization_name          = getModelColumnById(SpOrganizations, 1, 'organization_name')
    user.department_id              = 3
    user.department_name            = getModelColumnById(SpDepartments, 3, 'department_name')
    if request.data.get("role_id") == '8':
        user.is_distributor         = 1
    elif request.data.get("role_id") == '9':
        user.is_super_stockist      = 1 
    elif request.data.get("role_id") == '10':
        user.is_retailer            = 1 
    user.role_id                    = request.data.get("role_id")
    user.role_name                  = getModelColumnById(SpRoles,request.data.get("role_id"),'role_name')
    
    user.created_by      = request.user.id
    user.save()
    last_user_id = user.id
    
    mapProductToUser(last_user_id)
    
    basic                           = SpBasicDetails()
    basic.user_id                   = last_user_id
    basic.gender                    = request.data.get("gender")
    if request.data.get("date_of_birth"):
        basic.date_of_birth             = datetime.strptime(request.data.get("date_of_birth"), '%d/%m/%Y').strftime('%Y-%m-%d')
    basic.blood_group               = request.data.get("blood_group")
    basic.save()
    
    user_contact_no = SpContactNumbers()
    user_contact_no.user_id             = last_user_id
    user_contact_no.country_code        = '+91'
    user_contact_no.is_primary          = 1
    user_contact_no.contact_type        = 1
    user_contact_no.contact_type_name   = 'Home'   
    user_contact_no.contact_number      = request.data.get("contact_no")
    user_contact_no.save()
    
    if request.data.get("saddress_line_1"):
        correspondence = SpAddresses()
        correspondence.user_id           = last_user_id
        correspondence.type              = 'correspondence'
        correspondence.address_line_1    = request.data.get("saddress_line_1")
        correspondence.address_line_2    = request.data.get("saddress_line_2")
        correspondence.country_id        = 1
        correspondence.country_name      = getModelColumnById(SpCountries, 1,'country')
        correspondence.state_id          = request.data.get("sstate_id")
        correspondence.state_name        = getModelColumnById(SpStates, request.data.get("sstate_id"),'state')
        correspondence.city_id           = request.data.get("scity_id")
        correspondence.city_name         = getModelColumnById(SpCities, request.data.get("scity_id"),'city')
        # correspondence.pincode           = request.data.get("cpincode")
        correspondence.save()
    if request.data.get("address_line_1"):
        permanent = SpAddresses()
        permanent.user_id           = last_user_id
        permanent.type              = 'permanent'
        permanent.address_line_1    = request.data.get("address_line_1")
        permanent.address_line_2    = request.data.get("address_line_2")
        permanent.country_id        = 1
        permanent.country_name      = getModelColumnById(SpCountries, 1,'country')
        permanent.state_id          = request.data.get("state_id")
        permanent.state_name        = getModelColumnById(SpStates, request.data.get("state_id"),'state')
        permanent.city_id           = request.data.get("city_id")
        permanent.city_name         = getModelColumnById(SpCities, request.data.get("city_id"),'city')
        # permanent.pincode           = request.data.get("pincode")
        permanent.save()
    
    area_allocation             = SpUserAreaAllocations()
    area_allocation.user_id     = last_user_id
    area_allocation.zone_id     = request.data.get("zone_id")
    area_allocation.zone_name   = getModelColumnById(SpZones,request.data.get("zone_id"),'zone')
    area_allocation.town_id     = request.data.get("town_id")
    area_allocation.town_name   = getModelColumnById(SpTowns,request.data.get("town_id"),'town')
    area_allocation.route_id    = request.data.get("route_id")
    area_allocation.route_name  = getModelColumnById(SpRoutes,request.data.get("route_id"),'route')
    area_allocation.save()
    context = {}
    context['message']          = 'User details has been saved successfully.'
    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

def mapProductToUser(user_id):
    product_variants = SpProductVariants.objects.all()
    if len(product_variants):
        
        SpUserProductVariants.objects.filter(user_id=user_id).delete()

        for product_variant in product_variants:
            user_product_variant                            = SpUserProductVariants()
            user_product_variant.user_id                    = user_id
            user_product_variant.product_id                 = product_variant.product_id
            user_product_variant.product_name               = product_variant.product_name
            user_product_variant.product_class_id           = getModelColumnById(SpProducts,product_variant.product_id,'product_class_id')
            user_product_variant.product_variant_id         = product_variant.id
            user_product_variant.item_sku_code              = product_variant.item_sku_code
            user_product_variant.variant_quantity           = product_variant.variant_quantity
            user_product_variant.variant_unit_id            = product_variant.variant_unit_id
            user_product_variant.variant_name               = product_variant.variant_name
            user_product_variant.variant_unit_name          = product_variant.variant_unit_name
            user_product_variant.largest_unit_name          = product_variant.largest_unit_name
            user_product_variant.variant_size               = product_variant.variant_size
            user_product_variant.no_of_pouch                = product_variant.no_of_pouch
            user_product_variant.container_size             = product_variant.container_size
            user_product_variant.is_bulk_pack               = product_variant.is_bulk_pack
            user_product_variant.included_in_scheme         = product_variant.included_in_scheme
            user_product_variant.mrp                        = product_variant.mrp
            user_product_variant.container_mrp              = float(product_variant.mrp) * float(product_variant.no_of_pouch)
            user_product_variant.sp_user                    = product_variant.sp_employee
            user_product_variant.container_sp_user          = float(product_variant.sp_employee) * float(product_variant.no_of_pouch)
            user_product_variant.valid_from                 = product_variant.valid_from
            user_product_variant.valid_to                   = product_variant.valid_to
            user_product_variant.status                     = product_variant.status
            user_product_variant.save()
            
@csrf_exempt
@api_view(["POST"])
def saveUserTagging(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if bool(request.FILES.get('store_image', False)) == False:
        return Response({'message': 'Store Image is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if bool(request.FILES.get('profile_image', False)) == False:
        return Response({'message': 'Profile Image is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("latitude")is None or request.data.get("latitude") == '' or request.data.get("longitude")is None or request.data.get("longitude") == '':
        return Response({'message': 'Coordinates is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if bool(request.FILES.get('profile_image', False)) == True:
        if getModelColumnById(SpUsers, request.data.get("user_id"), 'profile_image'):
            deleteMediaFile(getModelColumnById(SpUsers, request.data.get("user_id"), 'profile_image'))
        uploaded_profile_image = request.FILES['profile_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        profile_image_name = uploaded_profile_image.name
        temp = profile_image_name.split('.')
        profile_image_name = 'profile_image_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        profile_image = storage.save(profile_image_name, uploaded_profile_image)
        profile_image = storage.url(profile_image)
    else:
        profile_image = None
    if bool(request.FILES.get('store_image', False)) == True:
        if getModelColumnById(SpUsers, request.data.get("user_id"), 'store_image'):
            deleteMediaFile(getModelColumnById(SpUsers, request.data.get("user_id"), 'store_image'))
        uploaded_store_image = request.FILES['store_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        store_image_name = uploaded_store_image.name
        temp = store_image_name.split('.')
        store_image_name = 'store_image_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        store_image = storage.save(store_image_name, uploaded_store_image)
        store_image = storage.url(store_image)
    else:
        store_image = None
    
    user_data                = SpUsers.objects.get(id=request.data.get("user_id"))
    user_data.is_tagged      = 1
    user_data.tagged_by      = request.user.id
    user_data.tagged_date    = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    user_data.store_image    = store_image
    user_data.profile_image  = profile_image
    user_data.latitude       = request.data.get("latitude")
    user_data.longitude      = request.data.get("longitude")
    user_data.save()
    
    user_name   = user_data.first_name+' '+user_data.middle_name+' '+user_data.last_name
    user_names  = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    heading     = user_name+' Tagged Successfully'
    activity    = user_name+' tagged successfully by '+user_names+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('User Management', 'User Tagging', heading, activity, user_data.id, user_name, 'userTag.png', '2', 'app.png')
    context = {}
    context['message']       = 'User Tagged successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def saveUserTracking(request):
    today   = date.today()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
   
    if request.data.get("latitude")is None or request.data.get("latitude") == '' or request.data.get("longitude")is None or request.data.get("longitude") == '':
        return Response({'message': 'Coordinates is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if SpUserTracking.objects.filter(user_id=request.data.get("user_id"), created_at__icontains=today.strftime("%Y-%m-%d")).exists():
        user_last_data = SpUserTracking.objects.filter(user_id=request.data.get("user_id"), created_at__icontains=today.strftime("%Y-%m-%d")).order_by('-id').first()
        
        R = 6373.0
        lat1 = radians(float(user_last_data.latitude))
        lon1 = radians(float(user_last_data.longitude))
        lat2 = radians(float(request.data.get("latitude")))
        lon2 = radians(float(request.data.get("longitude")))
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        meter_distance = float(distance * 1000)
        if meter_distance > 15 :
            user_data                       = SpUserTracking()
            user_data.user_id               = request.data.get("user_id")
            user_data.latitude              = request.data.get("latitude")
            user_data.longitude             = request.data.get("longitude")
            user_data.distance_travelled    = meter_distance
            user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
            user_data.save()
    else:
        user_data                       = SpUserTracking()
        user_data.user_id               = request.data.get("user_id")
        user_data.latitude              = request.data.get("latitude")
        user_data.longitude             = request.data.get("longitude")
        user_data.distance_travelled    = 0
        user_data.travel_charges        = getModelColumnById(Configuration, 1, 'travel_amount')
        user_data.save()
    context = {}
    context['message']       = 'Tracking data saved successfully successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def paymentCollection(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("dist_ss_id")is None or request.data.get("dist_ss_id") == '':
        return Response({'message': 'Customer Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("credit_date")is None or request.data.get("credit_date") == '':
        return Response({'message': 'Credit Date is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if request.data.get("credit_amount")is None or request.data.get("credit_amount") == '':
        return Response({'message': 'Credit Amount is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    if request.data.get("credit_mode")is None or request.data.get("credit_mode") == '':
        return Response({'message': 'Credit Mode is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("collector_type")is None or request.data.get("collector_type") == '':
        return Response({'message': 'Collector Type Mode is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if bool(request.FILES.get('payment_receipt', False)) == True:
        uploaded_payment_receipt = request.FILES['payment_receipt']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        payment_receipt_name = uploaded_payment_receipt.name
        temp = payment_receipt_name.split('.')
        payment_receipt_name = 'payment_receipt_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        payment_receipt = storage.save(payment_receipt_name, uploaded_payment_receipt)
        payment_receipt = storage.url(payment_receipt)
        # create thumbnail
        # image_file = str(settings.MEDIA_ROOT) + '/'+payment_receipt_name
        # size = 300, 300
        # im = Image.open(image_file)
        
        # if im.mode in ("RGBA", "P"):
        #     im = im.convert("RGB")
        # for orientation in ExifTags.TAGS.keys() : 
        #     if ExifTags.TAGS[orientation]=='Orientation' : break 
        # exif=dict(im._getexif().items())
        # if exif[orientation] == 3 : 
        #     im=im.rotate(180, expand=True)
        # elif exif[orientation] == 6 : 
        #     im=im.rotate(270, expand=True)
        # elif exif[orientation] == 8 : 
        #     im=im.rotate(90, expand=True)
        # im.thumbnail(size, Image.ANTIALIAS)
        # thumbnail_image = str(settings.MEDIA_ROOT) + '/thumbnail/'+payment_receipt
        # im.save(thumbnail_image, "JPEG",quality=100, rotated=False)
    else:
        payment_receipt = None
    if not SpUserLedger.objects.filter(user_id=request.data.get("dist_ss_id")).exists():
        ledger = SpUserLedger()
        ledger.user_id = request.data.get("dist_ss_id")
        ledger.particulars = "Wallet recharge"
        ledger.payment_note = request.data.get("payment_note")
        ledger.credit = request.data.get("credit_amount")
        ledger.debit = 0
        ledger.balance = request.data.get("credit_amount")
        ledger.payment_mode = request.data.get("credit_mode")
        ledger.payment_receipt = payment_receipt
        ledger.collector_type = request.data.get("collector_type")
        ledger.credited_by = request.data.get("user_id")
        ledger.save()
    else:
        last_row = SpUserLedger.objects.filter(user_id=request.data.get("dist_ss_id")).order_by('-id').first()
        ledger = SpUserLedger()
        ledger.user_id = request.data.get("dist_ss_id")
        ledger.particulars = "Wallet recharge"
        ledger.payment_note = request.data.get("payment_note")
        ledger.credit = request.data.get("credit_amount")
        ledger.debit = 0
        ledger.balance = float(last_row.balance) + float(request.data.get("credit_amount"))
        ledger.payment_mode = request.data.get("credit_mode")
        ledger.payment_receipt = payment_receipt
        ledger.collector_type = request.data.get("collector_type")
        ledger.credited_by = request.data.get("user_id")
        ledger.save()    
    # basic                           = SpBasicDetails.objects.get(user_id=request.data.get("dist_ss_id"))
    # basic.wallet_amount             = float(request.data.get("credit_amount"))+float(getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("dist_ss_id"), 'wallet_amount'))
    # basic.save()
     #Save Activity
    user_name   = str(request.user.first_name)
    if request.user.middle_name:
        user_name += ' '+str(request.user.middle_name)
    if request.user.last_name:
        user_name += ' '+str(request.user.last_name)
    diss_ss_name = getModelColumnById(SpUsers, request.data.get("dist_ss_id"), 'first_name')
    if getModelColumnById(SpUsers, request.data.get("dist_ss_id"), 'middle_name'):
        diss_ss_name += ' '+getModelColumnById(SpUsers, request.data.get("dist_ss_id"), 'middle_name')
    if getModelColumnById(SpUsers, request.data.get("dist_ss_id"), 'last_name'):
        diss_ss_name += ' '+getModelColumnById(SpUsers, request.data.get("dist_ss_id"), 'last_name')
    heading     = diss_ss_name+' wallet updated'
    activity    = diss_ss_name+' wallet updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    saveActivity('User Management', 'User Management', heading, activity, request.user.id, user_name, 'wallet.png', '1', 'web.png')
    context = {}
    context['message']       = 'User wallet has been credited successfully.'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def searchUserList(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    
    if request.data.get("dis_ss_name")is None or request.data.get("dis_ss_name") == '':
        return Response({'message': 'Dist/SS Name is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
        
    user_area_allocation = SpUserAreaAllocations.objects.filter(user_id=request.data.get("user_id")).values('town_id')
    user_list = []   
    for area_allocation in user_area_allocation:
        dis_ss_name = '%' + request.data.get("dis_ss_name") + '%'
        user_list  = SpUserAreaAllocations.objects.raw(''' SELECT sp_user_area_allocations.id, sp_user_area_allocations.town_name, sp_users.id as user_id, sp_users.emp_sap_id, sp_users.first_name, sp_users.middle_name, sp_users.role_id, sp_users.user_type, sp_users.reporting_to_id, sp_users.reporting_to_name, sp_users.primary_contact_number, sp_users.store_name, sp_users.profile_image, sp_users.last_name, sp_users.is_tagged FROM sp_user_area_allocations left join sp_users on sp_users.id = sp_user_area_allocations.user_id WHERE sp_user_area_allocations.town_id=%s and sp_users.user_type=%s and sp_users.status=%s and (sp_users.first_name like %s or sp_users.emp_sap_id like %s) order by sp_users.first_name asc ''', [area_allocation['town_id'], 4, 1, dis_ss_name, dis_ss_name])
        
        if user_list: 
            for user in user_list:
                user_name = str(user.first_name)
                if user.middle_name:
                    user_name += ' '+str(user.middle_name)
                if user.last_name:
                    user_name += ' '+str(user.last_name)
                users_list = {}
                users_list['id']                    = user.user_id
                users_list['customer_id']           = user.emp_sap_id
                users_list['name']                  = user_name
                users_list['contact_no']            = user.primary_contact_number
                users_list['role_id']               = user.role_id
                users_list['role']                  = getModelColumnById(SpRoles, user.role_id, 'role_name')
                users_list['is_tagged']             = user.is_tagged
                if user.profile_image:
                    img = baseurl+'/'+user.profile_image
                    users_list['profile_image']       = str(img)
                else:
                    users_list['profile_image']       = ''    
                users_list['user_type']             = user.user_type
                if user.reporting_to_id:
                    users_list['reporting_to_id']       = str(user.reporting_to_id)
                else:
                    users_list['reporting_to_id']       = ''
                users_list['reporting_to_name']     = user.reporting_to_name
                try:
                    user_basic_details = model_to_dict(SpBasicDetails.objects.get(user_id=user.user_id))
                except SpBasicDetails.DoesNotExist:
                    user_basic_details = []
                users_list['user_basic_details']     = user_basic_details
                try:
                    user_correspondence_details = model_to_dict(SpAddresses.objects.get(user_id=user.user_id,type='correspondence'))
                except SpAddresses.DoesNotExist:
                    user_correspondence_details = []
                users_list['user_correspondence_details']     = user_correspondence_details
                try:
                    user_permanent_details = model_to_dict(SpAddresses.objects.get(user_id=user.user_id,type='permanent'))
                except SpAddresses.DoesNotExist:
                    user_permanent_details = []
                users_list['user_permanent_details']     = user_permanent_details
                user_list.append(users_list)
    context = {}
    context['message']          = 'Success'
    context['user_list']        = user_list
    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK) 
@csrf_exempt
@api_view(["POST"])
def userDetails(request):
    if request.data.get("dist_ss_id")is None or request.data.get("dist_ss_id") == '':
        return Response({'message': 'Dist/SS Id is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)  
    user_details = SpUsers.objects.filter(status=1, emp_sap_id=request.data.get("dist_ss_id")).values()
    for user_detail in user_details:
        user_name = str(user_detail['first_name'])
        if user_detail['middle_name']:
            user_name += ' '+str(user_detail['middle_name'])
        if user_detail['last_name']:
            user_name += ' '+str(user_detail['last_name'])
        user_detail['user_name']       = user_name    
        if user_detail['profile_image']:
            img = baseurl+'/'+user_detail['profile_image']
            user_detail['profile_image']       = str(img)
        else:
            user_detail['profile_image']       = ''
    if user_details:
        try:
            user_basic_details = model_to_dict(SpBasicDetails.objects.get(user_id=user_details[0]['id']))
        except SpBasicDetails.DoesNotExist:
            user_basic_details = []
        try:
            user_correspondence_details = model_to_dict(SpAddresses.objects.get(user_id=user_details[0]['id'],type='correspondence'))
        except SpAddresses.DoesNotExist:
            user_correspondence_details = []
        try:
            user_permanent_details = model_to_dict(SpAddresses.objects.get(user_id=user_details[0]['id'],type='permanent'))
        except SpAddresses.DoesNotExist:
            user_permanent_details = []
    else:
        user_basic_details          = []
        user_correspondence_details = []
        user_permanent_details      = []    
    context = {}
    context['message']                          = 'Success'
    context['user_details']                     = user_details
    context['user_basic_details']               = user_basic_details
    context['user_correspondence_details']      = user_correspondence_details
    context['user_permanent_details']           = user_permanent_details
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def updateUsersProfile(request):
    contact_no_exists = SpUsers.objects.filter(primary_contact_number=request.data.get("contact_number")).exclude(id=request.data.get("user_id")).exists()
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("gender")is None or request.data.get("gender") == '':
        return Response({'message': 'Gender field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("date_of_birth")is None or request.data.get("date_of_birth") == '':
        return Response({'message': 'Date of birth field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("contact_number")is None or request.data.get("contact_number") == '':
        return Response({'message': 'Contact No. field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if request.data.get("contact_number")!='' and contact_no_exists:
        return Response({'message': 'Mobile No. already exists', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)            
    if request.data.get("shipping_address_1")is None or request.data.get("shipping_address_1") == '':
        return Response({'message': 'Shipping Address is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if request.data.get("shipping_state")is None or request.data.get("shipping_state") == '':
        return Response({'message': 'Shipping State is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("shipping_city")is None or request.data.get("shipping_city") == '':
        return Response({'message': 'Shipping City is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    if request.data.get("billing_address_1")is None or request.data.get("billing_address_1") == '':
        return Response({'message': 'Billing Address is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)    
    if request.data.get("billing_state")is None or request.data.get("billing_state") == '':
        return Response({'message': 'Billing State is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("billing_city")is None or request.data.get("billing_city") == '':
        return Response({'message': 'Billing City is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)            
    if bool(request.FILES.get('profile_image', False)) == True:
        uploaded_profile_image = request.FILES['profile_image']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        profile_image_name = uploaded_profile_image.name
        temp = profile_image_name.split('.')
        profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        profile_image = storage.save(profile_image_name, uploaded_profile_image)
        profile_image = storage.url(profile_image)        
            
    user                        = SpUsers.objects.get(id=request.data.get("user_id"))
    user.official_email         = request.data.get('official_email')
    if bool(request.FILES.get('profile_image', False)) == True:
        if user.profile_image:
            deleteMediaFile(user.profile_image)
        user.profile_image          = profile_image
    user.primary_contact_number = request.data.get('contact_number')
    user.save()
    try:
        user_basic_detail = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    except SpBasicDetails.DoesNotExist:
        user_basic_detail = None
    if user_basic_detail:
        user_basic_details = SpBasicDetails.objects.get(user_id=request.data.get("user_id"))
    else:
        user_basic_details = SpBasicDetails()
        
    user_basic_details.user_id          = request.data.get("user_id")
    user_basic_details.date_of_birth    = datetime.strptime(request.data.get('date_of_birth'), '%d/%m/%Y').strftime('%Y-%m-%d')
    user_basic_details.gender           = request.data.get('gender')
    user_basic_details.blood_group      = request.data.get('blood_group')
    user_basic_details.save()
    try:
        user_contact_nos = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    except SpContactNumbers.DoesNotExist:
        user_contact_nos = None
    if user_contact_nos:
        user_contact_no = SpContactNumbers.objects.get(user_id=request.data.get("user_id"), is_primary=1)
    else:
        user_contact_no = SpContactNumbers()
    user_contact_no.user_id         = request.data.get("user_id")   
    user_contact_no.contact_type     = 1   
    user_contact_no.contact_number  = request.data.get('contact_number')
    user_contact_no.save()
    # SpAddresses.objects.filter(user_id=request.data.get("user_id")).delete()
    correspondence = SpAddresses.objects.get(user_id=request.data.get("user_id"),type='correspondence')
    correspondence.user_id          = request.data.get("user_id")
    correspondence.type             = 'correspondence'
    correspondence.address_line_1   = request.data.get('shipping_address_1')
    correspondence.address_line_2   = request.data.get('shipping_address_2')
    correspondence.country_id       = 1
    correspondence.country_name     = getModelColumnById(SpCountries, 1,'country')
    correspondence.state_id         = request.data.get('shipping_state')
    correspondence.state_name       = getModelColumnById(SpStates, request.data.get('shipping_state'),'state')
    correspondence.city_id          = request.data.get('shipping_city')
    correspondence.city_name        = getModelColumnById(SpCities, request.data.get('shipping_city'),'city')
    correspondence.pincode          = request.data.get('shipping_pincode')
    correspondence.save()
    permanent = SpAddresses.objects.get(user_id=request.data.get("user_id"),type='permanent')
    permanent.user_id               = request.data.get("user_id")
    permanent.type                  = 'permanent'
    permanent.address_line_1        = request.data.get('billing_address_1')
    permanent.address_line_2        = request.data.get('billing_address_2')
    permanent.country_id            = 1
    permanent.country_name          = getModelColumnById(SpCountries, 1,'country')
    permanent.state_id              = request.data.get('billing_state')
    permanent.state_name            = getModelColumnById(SpStates, request.data.get('billing_state'),'state')
    permanent.city_id               = request.data.get('billing_city')
    permanent.city_name             = getModelColumnById(SpCities, request.data.get('billing_city'),'city')
    permanent.pincode               = request.data.get('billing_pincode')
    permanent.save()
    user                            = SpUsers.objects.get(id=request.data.get("user_id"))
    user_name   = str(request.user.first_name)
    heading     = 'Profile has been updated'
    activity    = 'Profile has been updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Profile Updated', 'Profile Updated', heading, activity, request.user.id, user_name, 'profileUpdated.png', '2', 'app.png')
    context = {}
    context['profile_image'] =  user.profile_image
    context['message']       = 'Profile has been updated successfully'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
#get master data
@csrf_exempt
@api_view(["POST"])
def getMasterData(request): 
    context = {}
    context['state_list']               = SpStates.objects.all().values('id', 'state')
    context['city_list']                = SpCities.objects.all().values('id', 'state_id', 'city')
    context['leave_type_list']          = SpLeaveTypes.objects.all().values('id', 'alias', 'leave_type')
    context['route_list']               = SpRoutes.objects.filter(status=1).values('id','route')
    context['message']                  = 'Success'
    context['response_code']            = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
def userDashboardData(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    today   = date.today()
    
    try:
        total_user_count = SpUsers.objects.filter(created_by=request.data.get("user_id")).count()
    except SpUsers.DoesNotExist:
        total_user_count = 0
    try:
        today_user_count = SpUsers.objects.filter(tagged_by=request.data.get("user_id"), tagged_date__icontains=today.strftime("%Y-%m-%d")).count()
    except SpUsers.DoesNotExist:
        today_user_count = 0
    try:
        total_collection     = SpUserLedger.objects.filter(credited_by=request.data.get("user_id")).aggregate(Sum('credit'))['credit__sum']
    except SpUserLedger.DoesNotExist:
        total_collection     = None
    if total_collection:
        total_collection = total_collection
    else:
        total_collection = 0.00
    try:
        today_collection     = SpUserLedger.objects.filter(created_at__icontains=today.strftime("%Y-%m-%d"), credited_by=request.data.get("user_id")).aggregate(Sum('credit'))['credit__sum']
    except SpUserLedger.DoesNotExist:
        today_collection     = None
    if today_collection:
        today_collection = today_collection
    else:
        today_collection = 0.00
        
    context = {}
    context['total_user_count']     = total_user_count
    context['today_user_count']     = today_user_count
    context['total_collection']     = total_collection
    context['today_collection']     = today_collection
    context['week_of_day']          = getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'week_of_day')
    context['message']              = 'Success'
    context['response_code']        = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)  
@csrf_exempt
@api_view(["POST"])
def applyLeave(request):
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    
    if request.data.get("leave_type_id")is None or request.data.get("leave_type_id") == '':
        return Response({'message': 'Leave type id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("leave_from_date")is None or request.data.get("leave_from_date") == '':
        return Response({'message': 'From date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    
    if request.data.get("leave_to_date")is None or request.data.get("leave_to_date") == '':
        return Response({'message': 'To date field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    if request.data.get("description")is None or request.data.get("description") == '':
        return Response({'message': 'Description field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST) 
    attachment = None
    if bool(request.FILES.get('attachment', False)) == True:
        uploaded_attachment = request.FILES['attachment']
        storage = FileSystemStorage()
        timestamp = int(time.time())
        attachment_name = uploaded_attachment.name
        temp = attachment_name.split('.')
        attachment_name = 'leave_attachment_'+str(timestamp)+"."+temp[(len(temp) - 1)]
        
        attachment = storage.save(attachment_name, uploaded_attachment)
        attachment = storage.url(attachment)        
            
    user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
    data = SpUserLeaves()
    data.user_id                = request.data.get("user_id")
    data.user_name              = user_name
    data.leave_type_id          = request.data.get("leave_type_id")
    data.leave_type             = getModelColumnById(SpLeaveTypes,request.data.get("leave_type_id"),'leave_type')
    data.leave_from_date        = request.data.get("leave_from_date")
    data.leave_to_date          = request.data.get("leave_to_date")
    data.leave_detail           = request.data.get('description')
    data.leave_status           = 1
    data.attachment             = attachment
    data.save()
    sendFocNotificationToUsers(data.id, '', 'add', 38, request.user.id, user_name, 'SpUserLeaves',request.user.role_id)
    
    heading     = 'New Leave Request has been initiated'
    activity    = 'New Leave Request has been initiated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
    
    saveActivity('Leave Management', 'Leave Request', heading, activity, request.user.id, user_name, 'add.png', '2', 'app.png')
    context = {}
    context['message']       = 'Leave Request has been successfully sent.'
    context['response_code'] = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)
    
@csrf_exempt
@api_view(["POST"])
def appliedLeaves(request):
    if request.data.get("page_limit")is None or request.data.get("page_limit") == '':
        return Response({'message': 'Page limit is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)
    if request.data.get("user_id")is None or request.data.get("user_id") == '':
        return Response({'message': 'User Id field is required', 'response_code': HTTP_400_BAD_REQUEST}, status=HTTP_400_BAD_REQUEST)   
    page_limit  = int(request.data.get("page_limit"))*10
    offset      = int(page_limit)-10
    page_limit  = 10
    leave_list_count = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id').count()
        
    if leave_list_count:
        leave_list_count = math.ceil(round(leave_list_count/10, 2))
        leave_status     = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).order_by('-id').first()
        leave_status     = leave_status.leave_status 
    else:
        leave_list_count = 0 
        leave_status     = 0
    leave_list = SpUserLeaves.objects.filter(user_id=request.data.get("user_id")).values('id','user_id','user_name','leave_type_id','leave_type','leave_from_date','leave_to_date','leave_detail','leave_status').order_by('-id')[offset:offset+page_limit]
    for leave in leave_list:
        alias = getModelColumnById(SpLeaveTypes,leave['leave_type_id'],'alias')
        leave['leave_type'] = leave['leave_type']+" ("+ alias +")"


    context = {}
    context['message']              = 'Success'
    context['leave_list']           = list(leave_list)
    context['leave_list_count']     = leave_list_count
    context['leave_count']          = getModelColumnByColumnId(SpBasicDetails, 'user_id', request.data.get("user_id"), 'leave_count')
    context['leave_status']         = leave_status
    context['response_code']        = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)    