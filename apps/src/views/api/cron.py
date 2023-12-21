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
from sorl.thumbnail import get_thumbnail, delete
from django.conf import settings
from django.db.models import Count
from django.core.mail import send_mail
from PIL import Image, ExifTags
baseurl = settings.BASE_URL

def date_diff_in_seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

def dhms_from_seconds(seconds):
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
    #return (hours, minutes, seconds)
	return (hours)

#user day out
@api_view(["GET"])
@permission_classes((AllowAny,))
def userDayOut(request):
    today   = date.today()
    context = {}
    
    user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d")).order_by('user_id').values('user_id').distinct()
    for attendance in user_attendance:
        user_attendance = SpUserAttendance.objects.filter(attendance_date_time__icontains=today.strftime("%Y-%m-%d"), user_id=attendance['user_id']).order_by('-id').first()
        if user_attendance.start_time is not None and user_attendance.end_time is None:
            start_time      = user_attendance.created_at
            start_time      = datetime.strptime(str(start_time), '%Y-%m-%d %H:%M:%S')
            end_time        = datetime.now()
            
            second = date_diff_in_seconds(end_time,start_time)
            diff   = dhms_from_seconds(second)
            if diff >= 8:
                now  = datetime.now().strftime('%H:%M:%S')
                data                        = SpUserAttendance()
                data.user_id                = attendance['user_id']
                data.attendance_date_time   = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                data.start_time             = None
                data.end_time               = now
                data.dis_ss_id              = None
                data.attendance_type        = 2
                data.latitude               = None
                data.longitude              = None
                data.status                 = 1
                data.save()

                AuthtokenToken.objects.filter(user_id=attendance['user_id']).delete()

    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)

#update order scheme table
@api_view(["GET"])
@permission_classes((AllowAny,))
def updateSchemeOrderTable(request):
    context = {}
    
    scheme_data = SpOrderSchemes.objects.filter(scheme_type='free').order_by('id')
    for scheme in scheme_data:
        data                        = SpOrderSchemes.objects.get(id=scheme.id)
        data.product_id             = getModelColumnById(SpProductVariants,scheme.free_variant_id,'product_id')
        data.product_class_id       = getModelColumnById(SpProductVariants,scheme.free_variant_id,'product_class_id')
        data.quantity_in_ltr        = int(scheme.pouch_quantity)*float(getModelColumnById(SpProductVariants,scheme.free_variant_id,'variant_size'))
        data.save()

    context['response_code']    = HTTP_200_OK
    return Response(context, status=HTTP_200_OK)    

#update order details table
@api_view(["GET"])
@permission_classes((AllowAny,))
def updateOrderDetailsTable(request):
    context = {}
    
    order_data = SpUsers.objects.filter().exclude(emp_sap_id='').order_by('id')
    for orders in order_data:
        mapProductToUser(orders.id)

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
            
#update order details table
# @api_view(["GET"])
# @permission_classes((AllowAny,))
# def updateOrderDetailsTable(request):
#     context = {}
    
#     order_data = SpUserTracking.objects.raw('''SELECT DISTINCT(user_id), id FROM sp_user_tracking  WHERE 1 group by user_id''')
#     user_id = []
#     for orders in order_data:
#         user_id.append(orders.user_id)
    
#     start_date = date(2021, 4, 17)
#     end_date = date(2021, 5, 12)
#     delta = timedelta(days=1)
    
#     tracking_dates=[]
#     while start_date <= end_date:
#         tracking_dates.append(start_date)
#         start_date += delta
    
#     users = []
#     for id, user in enumerate(user_id): 
#         for tracking_date in tracking_dates:
#             if SpUserTracking.objects.filter(user_id=user, created_at__icontains=tracking_date).exists():
#                 data = SpUserTracking.objects.filter(user_id=user, created_at__icontains=tracking_date).order_by('id').first()
#                 if data:
#                     users.append(data.id)
        
#     context['data']    = users
#     context['response_code']    = HTTP_200_OK
#     return Response(context, status=HTTP_200_OK)