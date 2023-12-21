import os

import calendar

from apps.src.models.helper_model import Configuration

from apps.src.models.models import *

from django.template.loader import get_template

from django.conf import settings

from sales_port.settings import EMAIL_HOST_USER

from django.core.mail import EmailMessage

from datetime import datetime,date

from datetime import timedelta

import requests

import math, random 

from django.db.models import Sum

from django.core.mail import send_mass_mail,EmailMessage

import re

from pyfcm import FCMNotification

from random import randint

from PIL import Image, ExifTags

baseurl = settings.BASE_URL







Path = settings.MEDIA_ROOT









def getUserRole(id):

    result =  SpUsers.objects.get(id=id)

    if result.user_type == 2:

        if result.is_distributor == 1:

            return 'Distributor'

        else:

            return 'SuperStockist'

    elif result.user_type == 1: 

        return 'Employee'       

    else:

        if result.is_distributor == 1:

            return 'Distributor'

        else:

            return 'Retailer'

          



def getConfigurationResult(column):

    result =  Configuration.objects.values(column).filter()[0][column]

    return result

def clean_data(data):
    data = data.strip()
    return data
    

def getModelColumnById(Model, id,column):

    result =  Model.objects.values(column).filter(pk=id)[0][column]

    return result

def getCrateDate():
    today   = date.today()
    user_crate_date = today.strftime("%Y-%m-%d")
    return user_crate_date

def getModelColumnByColumnId(Model,column_name,column_value,column):

    filters = {

        column_name: column_value

    }

    result =  Model.objects.values(column).filter(**filters)[0][column]

    return result

def getModelColumnByMultiFilter(Model,condition_list,column):
    result =  Model.objects.values(column).filter(**condition_list)[0][column]
    return result


def getUserName(id):
    if SpUsers.objects.filter(id=id):
        user = SpUsers.objects.filter(id=id).values('first_name','middle_name','last_name')
        user_name = user[0]['first_name']+" "
        if user[0]['middle_name'] is not None and user[0]['middle_name'] != "":
            user_name += user[0]['middle_name']+" "
        if user[0]['last_name'] is not None and user[0]['last_name'] != "":
            user_name += user[0]['last_name']
        return user_name
    else:
        return "User not found"



def deleteMediaFile(path):

    path = path.replace('/media', '') 

    path = Path + path

    if os.path.isfile(path):

       os.remove(path)



def sendEmail(request, template, context, subject, recipient):

    subject = subject

    message = get_template(template).render(context)

    msg = EmailMessage(

        subject,

        message,

        EMAIL_HOST_USER,

        [recipient],

    )

    msg.content_subtype = "html"  

    msg.send()

    print("Mail successfully sent")



def weeks_in_month(year, month):

    return len(calendar.monthcalendar(year, month))



def get_week_day(current_year, current_month):

    year, week, dow = datetime.today().isocalendar()

    result = [datetime.strptime(str(year) + "-" + str(week-1) + "-" + str(x), "%Y-%W-%w").day for x in range(0,7)]

    

    week_days = []

    for id, val in enumerate(result):

        if id != 0:

            if current_month > 9:

                if val > 9:

                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val)    

            else:

                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val)  

            day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%a') 

                  

            week_days.append(day)

        else:

            val = result[1]-1

            if current_month > 9:

                if val > 9:

                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val) 

            else:

                week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val) 

            day = datetime.strptime(str(week_date), '%Y-%m-%d').strftime('%a')  

                  

            week_days.append(day)

    return week_days



def get_week_date(current_year, current_month):

    year, week, dow = datetime.today().isocalendar()

    result = [datetime.strptime(str(year) + "-" + str(week-1) + "-" + str(x), "%Y-%W-%w").day for x in range(0,7)]

    

    week_dates = []

    for id, val in enumerate(result):

        if id != 0:

            if current_month > 9:

                if val > 9:

                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val)    

            else:

                if val > 9:

                    week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-0'+str(current_month)+'-0'+str(val)  

                  

            week_dates.append(week_date)

        else:

            val = result[1]-1

            if current_month > 9:

                if val > 9:

                    week_date = str(current_year)+'-'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-'+str(current_month)+'-0'+str(val) 

            else:

                if val > 9:

                    week_date = str(current_year)+'-0'+str(current_month)+'-'+str(val)

                else:

                    week_date = str(current_year)+'-0'+str(current_month)+'-0'+str(val) 

                  

            week_dates.append(week_date)

    return week_dates



def saveActivity(module,sub_module,heading,activity_msg,user_id,user_name,icon,platform,platform_icon):

    activity = SpActivityLogs()

    activity.module = module

    activity.sub_module = sub_module

    activity.heading = heading

    activity.activity = activity_msg

    activity.user_id = user_id

    activity.user_name = user_name

    if icon:

        activity.icon = icon

    else:

       activity.icon = 'add.png'     

    activity.platform = platform

    if platform_icon:

        activity.platform_icon = platform_icon

    else:

        activity.platform_icon = 'web.png'    

    activity.save()



def sendNotificationToUsers(order_id, order_code, permission_slug, sub_module_id, user_id, user_name, model_name, role_id):
    user_wf_level           = SpRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id).values('level_id').distinct().count()
    user_role_wf_permission = SpUserRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id, status=1).exclude(level_id=1).order_by('level_id')
    for wf_permission in user_role_wf_permission:
        user_detail = SpUsers.objects.get(id=wf_permission.user_id)
        if user_wf_level != 1:
            data                    = SpApprovalStatus()
            data.row_id             = order_id
            data.model_name         = model_name
            data.initiated_by_id    = user_id
            data.initiated_by_name  = user_name
            data.user_id            = wf_permission.user_id
            data.user_name          = str(user_detail.first_name)+' '+str(user_detail.middle_name)+' '+str(user_detail.last_name)
            data.role_id            = wf_permission.workflow_level_role_id
            data.sub_module_id      = wf_permission.sub_module_id
            data.permission_id      = wf_permission.permission_id
            data.permission_slug    = wf_permission.permission_slug
            data.level_id           = wf_permission.level_id
            data.level              = wf_permission.level
            data.status             = 0
            data.save()

            #save notification
            if user_wf_level == 3 and wf_permission.level_id == 2:
                notification                        = SpUserNotifications()
                notification.row_id                 = order_id
                notification.user_id                = wf_permission.user_id
                notification.model_name             = model_name
                notification.notification           = 'Order('+order_code+') '+wf_permission.level+' Request has been sent.'
                notification.is_read                = 0
                notification.created_by_user_id     = user_id
                notification.created_by_user_name   = user_name
                notification.save()
                order                               = SpOrders.objects.get(id=order_id)    
                order.order_status                  = wf_permission.level_id-1
                order.save()
            elif user_wf_level == 2 and wf_permission.level_id == 3:
                notification                        = SpUserNotifications()
                notification.row_id                 = order_id
                notification.user_id                = wf_permission.user_id
                notification.model_name             = model_name
                notification.notification           = 'Order('+order_code+') '+wf_permission.level+' Request has been sent.'
                notification.is_read                = 0
                notification.created_by_user_id     = user_id
                notification.created_by_user_name   = user_name
                notification.save()
                order                               = SpOrders.objects.get(id=order_id)     
                order.order_status                  = wf_permission.level_id-1
                order.save()

            #-----------------------------notify android block-------------------------------#
            userFirebaseToken = getModelColumnById(SpUsers,wf_permission.user_id,'firebase_token')
            employee_name = getUserName(wf_permission.user_id)

            message_title = "Order initiated"
            message_body = "An order ("+order_code+") has been initiated by "+user_name
            notification_image = ""

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
            saveNotification(order_id,'SpOrders','Order Management','Order initiated',message_title,message_body,notification_image,user_id,user_name,wf_permission.user_id,employee_name,'profile.png',2,'app.png',1,1)
            #-----------------------------save notification block----------------------------#    

    if user_wf_level == 1:
        order                               = SpOrders.objects.get(id=order_id)     
        order.order_status                  = 3
        order.save() 

def sendFocNotificationToUsers(model_id, code, permission_slug, sub_module_id, user_id, user_name, model_name, role_id):
    user_wf_level           = SpRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, 
    sub_module_id=sub_module_id).values('level_id').distinct().count()
    
    user_role_wf_permission = SpUserRoleWorkflowPermissions.objects.filter(permission_slug=permission_slug, sub_module_id=sub_module_id, status=1).exclude(level_id=1).order_by('level_id')
    for wf_permission in user_role_wf_permission:
        user_detail = SpUsers.objects.get(id=wf_permission.user_id)
        if user_wf_level != 1:
            data                    = SpApprovalStatus()
            data.row_id             = model_id
            data.model_name         = model_name
            data.initiated_by_id    = user_id
            data.initiated_by_name  = user_name
            data.user_id            = wf_permission.user_id
            data.user_name          = str(user_detail.first_name)+' '+str(user_detail.middle_name)+' '+str(user_detail.last_name)
            data.role_id            = wf_permission.workflow_level_role_id
            data.sub_module_id      = wf_permission.sub_module_id
            data.permission_id      = wf_permission.permission_id
            data.permission_slug    = wf_permission.permission_slug
            data.level_id           = wf_permission.level_id
            data.level              = wf_permission.level
            data.status             = 0
            data.save()
            
            #save notification
            if user_wf_level == 3 and wf_permission.level_id == 2:
                if model_name == 'SpUserLeaves':
                    data_model                               = SpUserLeaves.objects.get(id=model_id)    
                    data_model.leave_status                  = wf_permission.level_id-1
                else:
                    data_model                               = SpFocRequests.objects.get(id=model_id)    
                    data_model.foc_status                    = wf_permission.level_id-1
                
                data_model.save()
                

            elif user_wf_level == 2 and wf_permission.level_id == 3:
                if model_name == 'SpUserLeaves':
                    data_model                               = SpUserLeaves.objects.get(id=model_id)    
                    data_model.leave_status                  = wf_permission.level_id-1
                else:
                    data_model                               = SpFocRequests.objects.get(id=model_id)    
                    data_model.foc_status                    = wf_permission.level_id-1       
                
                data_model.save()
            
            if model_name == 'SpUserLeaves':
                #-----------------------------notify android block-------------------------------#
                userFirebaseToken = getModelColumnById(SpUsers,wf_permission.user_id,'firebase_token')
                employee_name = getUserName(wf_permission.user_id)

                message_title = "Leave initiated"
                message_body = "A leave has been applied by "+user_name
                notification_image = ""

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
                saveNotification(model_id,'SpUserLeaves','Users Management','Leave applied',message_title,message_body,notification_image,user_id,user_name,wf_permission.user_id,employee_name,'profile.png',2,'app.png',1,1)
                #-----------------------------save notification block----------------------------#
                
            else:
                #-----------------------------notify android block-------------------------------#
                userFirebaseToken = getModelColumnById(SpUsers,wf_permission.user_id,'firebase_token')
                employee_name = getUserName(wf_permission.user_id)

                message_title = "Sample Request initiated"
                message_body = "A Sample Request has been initiated by "+user_name
                notification_image = ""

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
                saveNotification(model_id,'SpFocRequests','Order Management','Order initiated',message_title,message_body,notification_image,user_id,user_name,wf_permission.user_id,employee_name,'profile.png',2,'app.png',1,1)
                #-----------------------------save notification block----------------------------#


    if user_wf_level == 1:
        if model_name == 'SpUserLeaves':
            data_model                             = SpUserLeaves.objects.get(id=model_id)
            data_model.leave_status                = 3 
        else:
            data_model                             = SpFocRequests.objects.get(id=model_id) 
            data_model.foc_status                  = 3
        data_model.save()

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



def sendSMS(sender_id,mobile,message):

    url = 'https://alerts.cbis.in/SMSApi/send'

    postdata = {

        "userid": "sahaj",

        "password": "MilK@01",

        "sendMethod": "quick",

        "senderid": sender_id,

        "mobile": mobile,

        "msg": message,

        "msgType": 'unicode',

        "duplicatecheck": 'true',

        "duplicatecheck": 'json'

        }

        

    response = requests.post(url, data=postdata)

    return response.status_code



def generateOTP() : 

    # Declare a digits variable   

    # which stores all digits  

    digits = "0123456789"

    OTP = "" 

  

   # length of password can be chaged 

   # by changing value in range 

    for i in range(4) : 

        OTP += digits[math.floor(random.random() * 10)] 

  

    return OTP

    



def get_ho_report_quantity(user_id,product_variant_id):

    if SpHoReport.objects.filter(user_id=user_id,product_variant_id=product_variant_id).exists() :

        ho_report = SpHoReport.objects.get(user_id=user_id,product_variant_id=product_variant_id)

        return ho_report.quantity

    else:

        return 0



def get_ho_report_foc(product_variant_id):

    if SpHoReport.objects.filter(user_id__isnull=True, product_variant_id=product_variant_id).exists() :

        ho_report = SpHoReport.objects.get(user_id__isnull=True, product_variant_id=product_variant_id)

        return ho_report.foc_pouch

    else:

        return 0

    

def get_ho_report_total_variant_qty(product_variant_id):

    print(product_variant_id)

    if SpHoReport.objects.filter(foc_pouch__isnull=True, product_variant_id=product_variant_id).exists() :

        ho_report = SpHoReport.objects.filter(foc_pouch__isnull=True,product_variant_id=product_variant_id).aggregate(Sum('quantity'))

        return ho_report['quantity__sum']

    else:

        return 0

def getFlatBulkIncentive(order_id, user_id):

    try:

        free_scheme = SpOrderSchemes.objects.filter(order_id=order_id, user_id=user_id).aggregate(Sum('incentive_amount'))['incentive_amount__sum']

    except SpOrderSchemes.DoesNotExist:

        free_scheme = None

    if free_scheme:

        free_scheme = free_scheme

    else:

        free_scheme = 0

    return free_scheme        





# send web push notifications

def sendWebPushNotification(message_title,message_body,registration_ids):

    firebase_server_key = getConfigurationResult('firebase_server_key')

    if firebase_server_key is not None and firebase_server_key != "":

        push_service = FCMNotification(api_key=firebase_server_key)

        result = push_service.notify_multiple_devices(registration_ids=registration_ids, message_title=message_title, message_body=message_body)

        return result   



# send android push notifications

def send_android_notification(message_title, message_body, data_message,registration_ids):

    firebase_server_key = getConfigurationResult('firebase_server_key')

    if firebase_server_key is not None and firebase_server_key != "":

        push_service = FCMNotification(api_key=firebase_server_key)

        result =  push_service.notify_multiple_devices(registration_ids=registration_ids,message_title=message_title, message_body=message_body, data_message=data_message)

        return result



# save notification to table.

def saveNotification(row_id,model_name,module,sub_module,heading,notification_msg,notification_image,from_user_id,from_user_name,to_user_id,to_user_name,icon,platform,platform_icon,notification_type,to_user_type=None):

    notification = SpNotifications()

    if row_id is not None:

        notification.row_id = row_id

    else:

       notification.row_id = None  



    if model_name is not None:

        notification.model_name = model_name

    else:

       notification.model_name = None

    if to_user_type is not None:
        notification.to_user_type = to_user_type
    else:
        notification.to_user_type = to_user_type
    



    notification.module = module

    notification.sub_module = sub_module

    notification.heading = heading

    notification.activity = notification_msg



    if notification_image is not None and notification_image != "" :

        notification.activity_image = notification_image

    else:

       notification.activity_image = None



    notification.from_user_id = from_user_id

    notification.from_user_name = from_user_name

    notification.to_user_id = to_user_id

    notification.to_user_name = to_user_name



    if icon is not None:

        notification.icon = icon

    else:

       notification.icon = 'add.png'  



    notification.platform = platform

    if platform_icon is not None:

        notification.platform_icon = platform_icon

    else:

        notification.platform_icon = 'web.png'

    notification.notification_type = notification_type



        

    notification.save()



def sendBulkEmail(message_title,message_message,emails,attachment=None):

    mail = EmailMessage(message_title, message_message, 'from@example.comg', emails)

    if attachment is not None:

        mail.attach_file(attachment)

    mail.send()


def isValidEmail(email):
    regex = '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+.[A-Za-z]{2,4}$'
    if(re.search(regex,email)):
        return True  
    else:  
        return False


def days_in_months(year, month):

    c = calendar.Calendar()

    month_array = []

    for date in c.itermonthdates(year, month):

        if int(month) > 9:

            months = month

        else:

            months = '0'+str(month)



        date_format = str(date).split('-')

        if date_format[0] == str(year) and date_format[1] == str(months):

            month_array.append(datetime.strptime(str(date), '%Y-%m-%d').strftime('%d/%m/%Y'))

    return month_array



def getDispatchedCratesSum(user_id, month_date, crate_type):

    if crate_type =='normal':

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('normal_debit'))['normal_debit__sum']

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum

        else:

            crate_sum = 0

        return crate_sum

    else:

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('jumbo_debit'))['jumbo_debit__sum']

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum

        else:

            crate_sum = 0

        return crate_sum    



def getReceivedCratesSum(user_id, month_date, crate_type):

    if crate_type =='normal':

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('normal_credit'))['normal_credit__sum']

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum

        else:

            crate_sum = 0

        return crate_sum

    else:

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('jumbo_credit'))['jumbo_credit__sum']

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum

        else:

            crate_sum = 0

        return crate_sum   

def getReturnCratesSum(user_id, month_date, crate_type):
    if crate_type =='normal':
        try:
            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('normal_debit'))['normal_debit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum
    else:
        try:
            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('jumbo_debit'))['jumbo_debit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum

def getLastCrateBalance(user_id, previous_month_last_date, crate_type):

    if crate_type =='normal':

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id,updated_datetime__lt=previous_month_last_date).values('normal_balance').order_by('-id').first()

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum['normal_balance']

        else:

            crate_sum = 0

        return crate_sum

    else:

        try:

            crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id,updated_datetime__lt=previous_month_last_date).values('jumbo_balance').order_by('-id').first()

        except SpUserCrateLedger.DoesNotExist:

            crate_sum = None

        if crate_sum:

            crate_sum = crate_sum['jumbo_balance']

        else:

            crate_sum = 0

        return crate_sum 



def getTotalCrates(user_id, year, month, crate_type, crates):

    if crate_type =='normal':

        if crates == 'dispatch':

            total_crates = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__year=year, updated_datetime__month=month).aggregate(Sum('normal_debit'))['normal_debit__sum']

            return total_crates

        else:

            total_crates = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__year=year, updated_datetime__month=month).aggregate(Sum('normal_credit'))['normal_credit__sum']

            return total_crates    

    else:

        if crates == 'dispatch':

            total_crates = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__year=year, updated_datetime__month=month).aggregate(Sum('jumbo_debit'))['jumbo_debit__sum']

            return total_crates

        else:

            total_crates = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__year=year, updated_datetime__month=month).aggregate(Sum('jumbo_credit'))['jumbo_credit__sum']

            return total_crates

def getTotalDispatchedCratesSum(month_date, crate_type):
    if crate_type =='normal':
        try:
            crate_sum = SpUserCrateLedger.objects.filter(updated_datetime__icontains=month_date).aggregate(Sum('normal_debit'))['normal_debit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum
    else:
        try:
            crate_sum = SpUserCrateLedger.objects.filter(updated_datetime__icontains=month_date).aggregate(Sum('jumbo_debit'))['jumbo_debit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum    

def getTotalReceivedCratesSum(month_date, crate_type):
    if crate_type =='normal':
        try:
            crate_sum = SpUserCrateLedger.objects.filter(updated_datetime__icontains=month_date).aggregate(Sum('normal_credit'))['normal_credit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum
    else:
        try:
            crate_sum = SpUserCrateLedger.objects.filter(updated_datetime__icontains=month_date).aggregate(Sum('jumbo_credit'))['jumbo_credit__sum']
        except SpUserCrateLedger.DoesNotExist:
            crate_sum = None
        if crate_sum:
            crate_sum = crate_sum
        else:
            crate_sum = 0
        return crate_sum

def getOpeningCratesSum(user_id, month_date):

    try:
        crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__lt=month_date).values('normal_balance').order_by('-id').first()
    except SpUserCrateLedger.DoesNotExist:
        crate_sum = None

    if crate_sum:
        crate_sum = crate_sum['normal_balance']
    else:
        crate_sum = 0
    
    try:
        jumbo_crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__lt=month_date).values('jumbo_balance').order_by('-id').first()
    except SpUserCrateLedger.DoesNotExist:
        jumbo_crate_sum = None

    if jumbo_crate_sum:
        jumbo_crate_sum = jumbo_crate_sum['jumbo_balance']
    else:
        jumbo_crate_sum = 0    

    total_crate_sum = int(crate_sum)+int(jumbo_crate_sum)
    return total_crate_sum 

def getTotalDispatchedCratesSums(user_id, month_date):
    try:
        crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('normal_debit'))['normal_debit__sum']
    except SpUserCrateLedger.DoesNotExist:
        crate_sum = None
    if crate_sum:
        crate_sum = crate_sum
    else:
        crate_sum = 0
    
    try:
        jumbo_crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('jumbo_debit'))['jumbo_debit__sum']
    except SpUserCrateLedger.DoesNotExist:
        jumbo_crate_sum = None
    if jumbo_crate_sum:
        jumbo_crate_sum = jumbo_crate_sum
    else:
        jumbo_crate_sum = 0    
    
    total_crate_sum = int(crate_sum)+int(jumbo_crate_sum)
    return total_crate_sum 

def getTotalReceivedCratesSums(user_id, month_date):
    try:
        crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('normal_credit'))['normal_credit__sum']
    except SpUserCrateLedger.DoesNotExist:
        crate_sum = None
    if crate_sum:
        crate_sum = crate_sum
    else:
        crate_sum = 0
    
    try:
        jumbo_crate_sum = SpUserCrateLedger.objects.filter(user_id=user_id, updated_datetime__icontains=month_date).aggregate(Sum('jumbo_credit'))['jumbo_credit__sum']
    except SpUserCrateLedger.DoesNotExist:
        jumbo_crate_sum = None

    if jumbo_crate_sum:
        jumbo_crate_sum = jumbo_crate_sum
    else:
        jumbo_crate_sum = 0    

    total_crate_sum = int(crate_sum)+int(jumbo_crate_sum)
    return total_crate_sum    
        
# Python3 program to print a given number in words.
# The program handles till 9 digits numbers and
# can be easily extended to 20 digit number
 
# strings at index 0 is not used, it
# is to make array indexing simple
one = [ "", "one ", "two ", "three ", "four ",
        "five ", "six ", "seven ", "eight ",
        "nine ", "ten ", "eleven ", "twelve ",
        "thirteen ", "fourteen ", "fifteen ",
        "sixteen ", "seventeen ", "eighteen ",
        "nineteen "];
 
# strings at index 0 and 1 are not used,
# they is to make array indexing simple
ten = [ "", "", "twenty ", "thirty ", "forty ",
        "fifty ", "sixty ", "seventy ", "eighty ",
        "ninety "];
 
# n is 1- or 2-digit number
def numToWords(n, s):
 
    str = "";
     
    # if n is more than 19, divide it
    if (n > 19):
        str += ten[n // 10] + one[n % 10];
    else:
        str += one[n];
 
    # if n is non-zero
    if (n):
        str += s;
 
    return str;
 
# Function to print a given number in words
def convertToWords(n):
 
    # stores word representation of given
    # number n
    out = "";
 
    # handles digits at ten millions and
    # hundred millions places (if any)
    out += numToWords((n // 10000000),
                            "crore ");
 
    # handles digits at hundred thousands
    # and one millions places (if any)
    out += numToWords(((n // 100000) % 100),
                                   "lakh ");
 
    # handles digits at thousands and tens
    # thousands places (if any)
    out += numToWords(((n // 1000) % 100),
                             "thousand ");
 
    # handles digit at hundreds places (if any)
    out += numToWords(((n // 100) % 10),
                            "hundred ");
 
    if (n > 100 and n % 100):
        out += "and ";
 
    # handles digits at ones and tens
    # places (if any)
    out += numToWords((n % 100), "");
 
    return out;
 

        



