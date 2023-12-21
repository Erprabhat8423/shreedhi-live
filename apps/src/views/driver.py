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


from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from django.core.files.storage import FileSystemStorage

# Create your views here.

@login_required
def index(request):
    context = {}
    page = request.GET.get('page')
    drivers = SpDrivers.objects.all().order_by('-id')
    paginator = Paginator(drivers, getConfigurationResult('page_limit'))

    try:
        drivers = paginator.page(page)
    except PageNotAnInteger:
        drivers = paginator.page(1)
    except EmptyPage:
        drivers = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1

    total_pages = int(paginator.count/getConfigurationResult('page_limit'))   

    if(paginator.count == 0):
        paginator.count = 1
        
    temp = total_pages%paginator.count
    if(temp > 0 and getConfigurationResult('page_limit')!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages

    data=[]
    for driver in drivers:
        temp={}
        temp['id']=driver.id
        temp['first_name']=driver.first_name
        temp['middle_name']=driver.middle_name
        temp['last_name']=driver.last_name
        temp['primary_contact_number']=driver.primary_contact_number
        temp['last_login']=driver.last_login
        registration_number = SpVehicles.objects.filter(driver_id=driver.id).first()
        temp['status']=driver.status
        if registration_number is not None :
            temp['assigned_vehicle'] = registration_number.registration_number
        else : 
            temp['assigned_vehicle'] = "-"
        
        data.append(temp)
        
    context['drivers']          = data
    context['page_limit']             = getConfigurationResult('page_limit')
    context['page_title'] = "Driver Management"

    # first_driver = SpDrivers.objects.raw('''SELECT sp_drivers.*,sp_driver_basic_details.blood_group,sp_driver_basic_details.gender, sp_driver_basic_details.father_name,sp_driver_basic_details.mother_name,sp_driver_basic_details.date_of_birth, sp_driver_addresses.address_line_1
    # ,sp_driver_addresses.address_line_2, sp_driver_addresses.country_name, sp_driver_addresses.state_name,sp_driver_addresses.city_name,sp_driver_addresses.pincode
    # FROM sp_drivers left join sp_driver_basic_details on sp_driver_basic_details.driver_id = sp_drivers.id
    # left join sp_driver_addresses on sp_driver_addresses.user_id = sp_drivers.id  
    # where sp_driver_addresses.type=%s order by id desc LIMIT 1 ''',['correspondence'])
    first_driver = SpDrivers.objects.raw('''SELECT sp_drivers.*,sp_driver_basic_details.blood_group,sp_driver_basic_details.gender, sp_driver_basic_details.father_name,sp_driver_basic_details.mother_name,sp_driver_basic_details.date_of_birth, sp_driver_addresses.address_line_1
    ,sp_driver_addresses.address_line_2, sp_driver_addresses.country_name, sp_driver_addresses.state_name,sp_driver_addresses.city_name,sp_driver_addresses.pincode
    FROM sp_drivers left join sp_driver_basic_details on sp_driver_basic_details.driver_id = sp_drivers.id
    left join sp_driver_addresses on sp_driver_addresses.user_id = sp_drivers.id  
    order by id desc LIMIT 1 ''')

    if first_driver :
        context['first_driver'] = first_driver[0]
    else : 
        context['first_driver'] = []

    
    template = 'logistics/driver/drivers.html'
    return render(request, template, context)



@login_required
def ajaxDriverList(request):
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

    template = 'logistics/driver/ajax-drivers.html'
    return render(request, template, context)



@login_required
def addDriver(request):

    if request.method == "POST":
        response = {}
        try:
            user_context = {}
            user_context['first_name']      = request.POST['first_name']
            user_context['middle_name']     = request.POST['middle_name']
            user_context['last_name']       = request.POST['last_name']

            error_count = 0
            error_response = {}
            

            if(error_count > 0):
                response['error'] = True
                response['message'] = error_response

                return JsonResponse(response)
            else:
                
                if bool(request.FILES.get('profile_image', False)) == True:
                    if request.POST['previous_profile_image'] != '':
                        deleteMediaFile(request.POST['previous_profile_image'])
                    uploaded_profile_image = request.FILES['profile_image']
                    storage = FileSystemStorage()
                    timestamp = int(time.time())
                    profile_image_name = uploaded_profile_image.name
                    temp = profile_image_name.split('.')
                    profile_image_name = 'profile_'+str(timestamp)+"."+temp[(len(temp) - 1)]
                    
                    profile_image = storage.save(profile_image_name, uploaded_profile_image)
                    profile_image = storage.url(profile_image)
                
                else:
                    profile_image = None        
                
                user = SpDrivers()
                user.salutation     = request.POST['salutation']
                user.first_name     = request.POST['first_name']
                user.middle_name    = request.POST['middle_name']
                user.profile_image  = profile_image
                user.last_name      = request.POST['last_name']
                user.production_unit_id = request.POST['production_unit_id']


                user.status = 1
                user.save()
                last_user_id = user.id
                country_codes       = request.POST.getlist('country_code[]') 
                contact_types       = request.POST.getlist('contact_type[]')
                contact_nos         = request.POST.getlist('contact_no[]')
                is_primary          = request.POST.getlist('primary_contact[]')

                for id, val in enumerate(contact_nos):
                    user_contact_no         = SpDriverContactNumbers()
                    user_contact_no.user_id = last_user_id
                    if country_codes[id]!='':
                        user_contact_no.country_code = country_codes[id]
                    if contact_types[id]!='':    
                        user_contact_no.contact_type = contact_types[id]
                        user_contact_no.contact_type_name = getModelColumnById(SpContactTypes,contact_types[id],'contact_type')
                    if contact_nos[id]!='':    
                        user_contact_no.contact_number = contact_nos[id]
                    if is_primary[id]!='':    
                        user_contact_no.is_primary = is_primary[id]
                    user_contact_no.status = 1
                    user_contact_no.save()
                    if is_primary[id] == '1':
                        user_data = SpDrivers.objects.get(id=last_user_id)
                        user_data.primary_contact_number = contact_nos[id]
                        
                        user_data.save()

               
               
                basic = SpDriverBasicDetails()
                basic.driver_id       = last_user_id
                basic.father_name   = request.POST['father_name']
                basic.mother_name   = request.POST['mother_name']
                basic.gender        = request.POST['user_gender']
                basic.date_of_birth = datetime.strptime(request.POST['date_of_birth'], '%d/%m/%Y').strftime('%Y-%m-%d')
                basic.blood_group   = request.POST['blood_group']
                basic.status = 1
                basic.save() 

                correspondence = SpDriverAddresses()
                correspondence.user_id          = last_user_id
                correspondence.type             = 'correspondence'
                correspondence.address_line_1   = request.POST['store_address_line_1']
                correspondence.address_line_2   = request.POST['store_address_line_2']
                correspondence.country_id       = request.POST['store_country_id']
                correspondence.country_name     = getModelColumnById(SpCountries, request.POST['store_country_id'],'country')
                correspondence.state_id         = request.POST['store_state_id']
                correspondence.state_name       = getModelColumnById(SpStates, request.POST['store_state_id'],'state')
                correspondence.city_id          = request.POST['store_city_id']
                correspondence.city_name        = getModelColumnById(SpCities, request.POST['store_city_id'],'city')
                correspondence.pincode          = request.POST['store_pincode']
                correspondence.save()

                permanent = SpDriverAddresses()
                permanent.user_id           = last_user_id
                permanent.type              = 'permanent'
                permanent.address_line_1    = request.POST['permanent_address_line_1']
                permanent.address_line_2    = request.POST['permanent_address_line_2']
                permanent.country_id        = request.POST['permanent_country_id']
                permanent.country_name      = getModelColumnById(SpCountries, request.POST['permanent_country_id'],'country')
                permanent.state_id          = request.POST['permanent_state_id']
                permanent.state_name        = getModelColumnById(SpStates, request.POST['permanent_state_id'],'state')
                permanent.city_id           = request.POST['permanent_city_id']
                permanent.city_name         = getModelColumnById(SpCities, request.POST['permanent_city_id'],'city')
                permanent.pincode           = request.POST['permanent_pincode']
                permanent.save()

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Driver created'
                activity    = 'Driver created by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Driver Management', heading, activity, request.user.id, user_name, 'addDriver.png', '1', 'web.png')
                
                context = {}
                context['last_user_id']             = last_user_id
                context['basic_details']     = SpDriverBasicDetails.objects.get(driver_id=last_user_id)
                context['official_details']     = SpDrivers.objects.get(id=last_user_id)
                template = 'logistics/driver/update-driver-official-details.html'
                return render(request, template, context)
        
        except Exception as e:
            response['flag'] = False
            response['message'] = str(e)
            return JsonResponse(response)

    else:
        template = 'logistics/driver/add-driver.html'
        context = {}
        contact_types   = SpContactTypes.objects.filter(status=1)
        countries       = SpCountries.objects.all()
        country_codes   = SpCountryCodes.objects.filter(status=1)

        context = {}
        context['contact_types']    = contact_types
        context['countries']        = countries
        context['country_codes']    = country_codes
        context['production_unit'] = SpProductionUnit.objects.all()
        
        return render(request, template,context)



@login_required
def editDriverOfficial(request,driver_id):
    if request.method == "POST":
        response = {}
        try:
            user_basic_details                  = SpDriverBasicDetails.objects.get(driver_id=request.POST['last_user_id'])
            user_basic_details.aadhaar_nubmer       = request.POST['aadhaar_nubmer']
            user_basic_details.dl_number           = request.POST['dl_number']
            user_basic_details.personal_email           = request.POST['personal_email']
            user_basic_details.date_of_joining      = datetime.strptime(request.POST['date_of_joining'], '%d/%m/%Y').strftime('%Y-%m-%d')
            

            if bool(request.FILES.get('aadhaar_document', False)) == True:
                if request.POST['previous_aadhaar_document'] != '':
                        deleteMediaFile(request.POST['previous_aadhaar_document'])
                uploaded_aadhaar_document = request.FILES['aadhaar_document']
                storage = FileSystemStorage()
                timestamp = int(time.time())
                aadhaar_document_name = uploaded_aadhaar_document.name
                temp = aadhaar_document_name.split('.')
                aadhaar_document_name = 'aadhaar_document_'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
                aadhaar_document = storage.save(aadhaar_document_name, uploaded_aadhaar_document)
                aadhaar_document = storage.url(aadhaar_document)
            else:
                if request.POST['previous_aadhaar_document'] != '':
                        aadhaar_document = request.POST['previous_aadhaar_document'] 
                else:
                    aadhaar_document = None
                
            if bool(request.FILES.get('dl_document', False)) == True:
                if request.POST['previous_dl_document'] != '':
                        deleteMediaFile(request.POST['previous_dl_document'])        
                uploaded_dl_document = request.FILES['dl_document']
                storage = FileSystemStorage()
                timestamp = int(time.time())
                dl_document_name = uploaded_dl_document.name
                temp = dl_document_name.split('.')
                dl_document_name = 'dl_document_'+str(timestamp)+"."+temp[(len(temp) - 1)]
                
                dl_document = storage.save(dl_document_name, uploaded_dl_document)
                dl_document = storage.url(dl_document)
            else:
                if request.POST['previous_dl_document'] != '':
                        dl_document = request.POST['previous_dl_document'] 
                else:
                    dl_document = None
                
            user_basic_details.aadhaar_document = aadhaar_document
            user_basic_details.dl_document = dl_document
            user_basic_details.save()

            if user_basic_details.id :

                #Save Activity
                user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
                heading     = 'Driver updated'
                activity    = 'Driver updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
                saveActivity('Logistics Management', 'Driver Management', heading, activity, request.user.id, user_name, 'editDriver.png', '1', 'web.png')

                response['flag'] = True
                response['message'] = "Record has been updated successfully."
            else:
                response['flag'] = False
                response['message'] = "Failed to save"
        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        context = {}
        context['basic_details']     = SpDriverBasicDetails.objects.get(driver_id=driver_id)
        context['official_details']     = SpDrivers.objects.get(id=driver_id)
        context['last_user_id']             = driver_id
        template = 'logistics/driver/update-driver-official-details.html'
        return render(request, template, context)



@login_required
def editDriverBasic(request,driver_id):
    if request.method == "POST":
        response = {}
        try:
            
            if bool(request.FILES.get('profile_image', False)) == True:
                uploaded_profile_image = request.FILES['profile_image']
                pfs = FileSystemStorage()
                profile_image = pfs.save(uploaded_profile_image.name, uploaded_profile_image)
                profile_image = pfs.url(profile_image)
            else:
                if request.POST['previous_profile_image'] != '':
                    profile_image = request.POST['previous_profile_image'] 
                else:
                    profile_image = None

            SpDriverAddresses.objects.filter(user_id=request.POST['last_user_id']).delete()
            SpDriverContactNumbers.objects.filter(user_id=request.POST['last_user_id']).delete()

            user = SpDrivers.objects.get(id=request.POST['last_user_id'])
            user.salutation = request.POST['salutation']
            user.first_name = request.POST['first_name']
            user.middle_name = request.POST['middle_name']
            user.profile_image = profile_image
            user.last_name = request.POST['last_name']
            user.official_email = request.POST['official_email']
            user.production_unit_id = request.POST['production_unit_id']
            user.save()
            last_user_id = driver_id#request.POST['last_user_id']

        
            country_codes       = request.POST.getlist('country_code[]') 
            contact_person_name = request.POST.getlist('contact_person_name[]')
            contact_types       = request.POST.getlist('contact_type[]')
            contact_nos         = request.POST.getlist('contact_no[]')
            is_primary          = request.POST.getlist('primary_contact[]')

            for id, val in enumerate(contact_nos):
                if is_primary[id] == '1':
                    user_data = SpDrivers.objects.get(id=last_user_id)
                    user_data.primary_contact_number = contact_nos[id]
                    user_data.save()

                user_contact_no = SpDriverContactNumbers()
                user_contact_no.user_id = last_user_id
                if country_codes[id]!='':
                    user_contact_no.country_code = country_codes[id]
                if contact_types[id]!='':    
                    user_contact_no.contact_type = contact_types[id]
                    user_contact_no.contact_type_name = getModelColumnById(SpContactTypes,contact_types[id],'contact_type')
                if contact_nos[id]!='':    
                    user_contact_no.contact_number = contact_nos[id]
                if is_primary[id]!='':    
                    user_contact_no.is_primary = is_primary[id]
                user_contact_no.status = 1
                user_contact_no.save()
        
            basic                       = SpDriverBasicDetails.objects.get(driver_id=last_user_id)
            basic.user_id               = last_user_id
            basic.father_name           = request.POST['father_name']
            basic.mother_name           = request.POST['mother_name']
            basic.gender                = request.POST['user_gender']
            basic.date_of_birth         = datetime.strptime(request.POST['date_of_birth'], '%d/%m/%Y').strftime('%Y-%m-%d')
            basic.blood_group           = request.POST['blood_group']
            basic.save()

        
            correspondence = SpDriverAddresses()
            correspondence.user_id          = last_user_id
            correspondence.type             = 'correspondence'
            correspondence.address_line_1   = request.POST['store_address_line_1']
            correspondence.address_line_2   = request.POST['store_address_line_2']
            correspondence.country_id       = request.POST['store_country_id']
            correspondence.country_name     = getModelColumnById(SpCountries, request.POST['store_country_id'],'country')
            correspondence.state_id         = request.POST['store_state_id']
            correspondence.state_name       = getModelColumnById(SpStates, request.POST['store_state_id'],'state')
            correspondence.city_id          = request.POST['store_city_id']
            correspondence.city_name        = getModelColumnById(SpCities, request.POST['store_city_id'],'city')
            correspondence.pincode          = request.POST['store_pincode']
            correspondence.save()

            permanent = SpDriverAddresses()
            permanent.user_id = last_user_id
            permanent.type = 'permanent'
            permanent.address_line_1    = request.POST['permanent_address_line_1']
            permanent.address_line_2    = request.POST['permanent_address_line_2']
            permanent.country_id        = request.POST['permanent_country_id']
            permanent.country_name      = getModelColumnById(SpCountries, request.POST['permanent_country_id'],'country')
            permanent.state_id          = request.POST['permanent_state_id']
            permanent.state_name        = getModelColumnById(SpStates, request.POST['permanent_state_id'],'state')
            permanent.city_id           = request.POST['permanent_city_id']
            permanent.city_name         = getModelColumnById(SpCities, request.POST['permanent_city_id'],'city')
            permanent.pincode           = request.POST['permanent_pincode']
            permanent.save()

            response['error'] = False
            response['last_user_id'] = last_user_id

             #Save Activity
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Driver updated'
            activity    = 'Driver updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Logistics Management', 'Driver Management', heading, activity, request.user.id, user_name, 'editDriver.png', '1', 'web.png')

            return JsonResponse(response)

        except Exception as e:
            response['error'] = False
            response['message'] = str(e)
        return JsonResponse(response)
    else:
        contact_types = SpContactTypes.objects.filter(status=1)
        countries = SpCountries.objects.all()
        country_codes   = SpCountryCodes.objects.filter(status=1)

        context = {}
        context['contact_types'] = contact_types
        context['countries']     = countries
        context['country_codes'] = country_codes

        driver = SpDrivers.objects.raw('''SELECT sp_drivers.*,sp_driver_basic_details.blood_group,sp_driver_basic_details.date_of_birth,
        sp_driver_basic_details.gender,sp_driver_basic_details.date_of_joining,sp_driver_basic_details.mother_name,sp_driver_basic_details.father_name
        FROM sp_drivers left join sp_driver_basic_details on sp_driver_basic_details.driver_id = sp_drivers.id 
        where sp_drivers.id = %s''',[driver_id])
        
        try:
            driver_correspondence_address = SpDriverAddresses.objects.get(user_id=driver_id,type='correspondence')
        except SpDriverAddresses.DoesNotExist:
            driver_correspondence_address = None

        try:
            driver_permanent_address = SpDriverAddresses.objects.get(user_id=driver_id,type='permanent')
        except SpDriverAddresses.DoesNotExist:
            driver_permanent_address = None

        try:
            driver_contact_numbers = SpDriverContactNumbers.objects.filter(user_id=driver_id)
        except SpContactNumbers.DoesNotExist:
            driver_contact_numbers = None    


        try:
            if driver_correspondence_address is not None:
                driver_store_states = SpStates.objects.filter(country_id=driver_correspondence_address.country_id)
            else:
                driver_store_states = None    
        except SpStates.DoesNotExist:
            driver_store_states = None    

        try:
            if driver_correspondence_address is not None:
                driver_store_cities = SpCities.objects.filter(state_id=driver_correspondence_address.state_id)
            else:
                driver_store_cities = None
        except SpCities.DoesNotExist:
            driver_store_cities = None 
        
        try:
            if driver_permanent_address is not None:
                driver_permanent_states = SpStates.objects.filter(country_id=driver_permanent_address.country_id)
            else:
                driver_permanent_states = None    
        except SpStates.DoesNotExist:
            driver_permanent_states = None

        try:
            if driver_permanent_address is not None:
                driver_permanent_cities = SpCities.objects.filter(state_id=driver_permanent_address.state_id)
            else:
                driver_permanent_cities = None    
        except SpCities.DoesNotExist:
            driver_permanent_cities = None

        if driver:
            context['driver'] = driver[0]
            context['driver_correspondence_address']  = driver_correspondence_address
            context['driver_permanent_address']       = driver_permanent_address
            context['user_contacts']                    = driver_contact_numbers
            context['store_states']                     = driver_store_states
            context['store_cities']                     = driver_store_cities
            context['permanent_states']                 = driver_permanent_states
            context['permanent_cities']                 = driver_permanent_cities
            context['last_user_id']                     = driver_id
            context['production_unit'] = SpProductionUnit.objects.all()

            template = 'logistics/driver/edit-driver-basic.html'
            return render(request, template, context)
        else:
            return HttpResponse('Driver not found')




@login_required
def driverShortDetails(request,driver_id):
    context = {}
    # first_driver = SpDrivers.objects.raw('''SELECT sp_drivers.*,sp_driver_basic_details.blood_group,sp_driver_basic_details.gender, sp_driver_basic_details.father_name,sp_driver_basic_details.mother_name,sp_driver_basic_details.date_of_birth, sp_driver_addresses.address_line_1
    # ,sp_driver_addresses.address_line_2, sp_driver_addresses.country_name, sp_driver_addresses.state_name,sp_driver_addresses.city_name,sp_driver_addresses.pincode
    # FROM sp_drivers left join sp_driver_basic_details on sp_driver_basic_details.driver_id = sp_drivers.id
    # left join sp_driver_addresses on sp_driver_addresses.user_id = sp_drivers.id  
    # where sp_driver_addresses.type=%s and sp_drivers.id = %s ''',['correspondence', driver_id])
    first_driver = SpDrivers.objects.raw('''SELECT sp_drivers.*,sp_driver_basic_details.blood_group,sp_driver_basic_details.gender, sp_driver_basic_details.father_name,sp_driver_basic_details.mother_name,sp_driver_basic_details.date_of_birth, sp_driver_addresses.address_line_1
    ,sp_driver_addresses.address_line_2, sp_driver_addresses.country_name, sp_driver_addresses.state_name,sp_driver_addresses.city_name,sp_driver_addresses.pincode
    FROM sp_drivers left join sp_driver_basic_details on sp_driver_basic_details.driver_id = sp_drivers.id
    left join sp_driver_addresses on sp_driver_addresses.user_id = sp_drivers.id  
    where sp_drivers.id = %s ''',[driver_id])
    if first_driver :
        context['first_driver'] = first_driver[0]
    else : 
        context['first_driver'] = []
    template = 'logistics/driver/driver-short-details.html'
    return render(request, template,context)

@login_required
def driverDetails(request,driver_id):
    context = {}
    
    template = 'logistic/driver/driver-details.html'

    return render(request, template,context)



@login_required
def updateDriverStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')
            data = SpDrivers.objects.get(id=id)
            data.status = is_active
            data.save()

             #Save Activity
            user_name   = request.user.first_name+' '+request.user.middle_name+' '+request.user.last_name
            heading     = 'Driver status updated'
            activity    = 'Driver status updated by '+user_name+' on '+datetime.now().strftime('%d/%m/%Y | %I:%M %p') 
            saveActivity('Logistics Management', 'Driver Management', heading, activity, request.user.id, user_name, 'editDriver.png', '1', 'web.png')

            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/drivers')
