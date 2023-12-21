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
from django.forms.models import model_to_dict
from datetime import datetime, date
from datetime import timedelta

# State option View
@login_required
def stateOption(request,country_id):
    response = {}
    options = '<option value="" selected>Select State</option>'
    states = SpStates.objects.filter(country_id=country_id)
    for state in states :
        options += "<option value="+str(state.id)+">"+state.state+"</option>"

    response['options'] = options
    return JsonResponse(response)

# sapRouteOption option View
@login_required
def sapRouteOption(request):
    today                   = request.GET['order_date']
    today                   = datetime.strptime(str(today), '%d/%m/%Y').strftime('%Y-%m-%d')
    options =''
    vehicles_number  = ''
    response = {}
    routes = SpRoutes.objects.raw('''SELECT sp_routes.* FROM sp_routes LEFT JOIN sp_orders on sp_routes.id=sp_orders.route_id WHERE date(sp_orders.order_date)=%s and sp_orders.block_unblock=%s GROUP BY sp_orders.route_id''',[today,1])
    if request.GET["route_code"]:
        print(request.GET["route_code"])
        vehicles = SpVehicles.objects.filter(route_id=request.GET["route_code"])
        for vehicle in vehicles:
            vehicles_number += "<option value='vehicle.id'>" + vehicle.registration_number+"</option>"
        response['vehicles_number'] = vehicles_number
        if not vehicles_number:
            vehicles_number = '<option value="">Select Vehicle</option>'
    else:
        route_id = []
        for route in routes :
            if route.route_code:
                route_code=route.route_code
                route_id.append(route.id)
                options += "<option route_id='"+str(route.id)+"' value='"+str(route.id)+"'>"+route.route+" ["+str(route_code)+"] </option>"
                
            else:
                options += "<option value=''>"+route.route+"</option>"
        if route_id:
            vehicles = SpVehicles.objects.filter(route_id=route_id[0])
            for vehicle in vehicles:
                vehicles_number += "<option value='vehicle.id'>"+vehicle.registration_number+"</option>"

        if not vehicles_number:
            vehicles_number = '<option value="">Select Vehicle</option>'

        if not options:
            options = '<option value="">Select Route</option>'
        response['options']         = options
        response['vehicles_number'] = vehicles_number
    return JsonResponse(response)


@login_required
def sapRouteOption(request):
    today = request.GET['order_date']
    today = datetime.strptime(str(today), '%d/%m/%Y').strftime('%Y-%m-%d')
    options = ''
    vehicles_number = ''
    response = {}
    # routes = SpRoutes.objects.raw('''SELECT sp_routes.* FROM sp_routes LEFT JOIN sp_orders on sp_routes.id=sp_orders.route_id WHERE date(sp_orders.order_date)=%s and sp_orders.block_unblock=%s GROUP BY sp_orders.route_id''', [today, 1])
    route_ids = SpLogisticPlanDetail.objects.filter(order_date__icontains = today).values_list('route_id').distinct()
    routes = SpRoutes.objects.filter(id__in = route_ids)
    
    route_id = []
    for route in routes:
        if route.route_code:
            route_code = route.route_code
            route_id.append(route.id)
            options += "<option route_id='"+str(route.id)+"' value='"+str(
                route.id)+"'>"+route.route+" ["+str(route_code)+"] </option>"

        else:
            options += "<option value=''>"+route.route+"</option>"
    if route_id:
        vehicles = SpVehicles.objects.filter(route_id=route_id[0])
        for vehicle in vehicles:
            vehicles_number += "<option value='"+str(vehicle.id)+"'>" + vehicle.registration_number+"</option>"

    if not vehicles_number:
        vehicles_number = '<option value="">Select Vehicle</option>'

    if not options:
        options = '<option value="">Select Route</option>'
    response['options'] = options
    response['vehicles_number'] = vehicles_number
    return JsonResponse(response)


@login_required
def vehicleOptionList(request):
    vehicles_number = ''
    response = {}
    if request.GET["route_code"]:
        vehicles = SpVehicles.objects.filter(route_id=request.GET["route_code"])
        vehicles_number += "<option value=''>Select Vehicle</option>"
        for vehicle in vehicles:
            vehicles_number += "<option value='" + str(vehicle.id)+"'>" + vehicle.registration_number+"</option>"
        response['vehicles_number'] = vehicles_number
        if not vehicles_number:
            vehicles_number = '<option value="">Select Vehicle</option>'
        response['vehicles_number'] = vehicles_number
    return JsonResponse(response)


# order user option View
@login_required
def orderUserList(request):
    start_date                   = request.GET['start_date']
    organization_id            = request.GET['organization_id']
    response = {}
    # end_date                   = request.GET['end_date']
    # end_date    = datetime.strptime(request.GET['end_date'], "%Y-%m-%d")
    # end_date    = end_date + timedelta(days=1)
    
    # if start_date==end_date:
    #     orders_list = SpOrders.objects.filter( indent_status=1,block_unblock=1, order_date__icontains=start_date).order_by('user_id').values_list('user_id','user_name','user_sap_id').distinct()
    # else:
    #     orders_list = SpOrders.objects.filter( indent_status=1,block_unblock=1, order_date__range=[start_date, end_date]).order_by('user_id').values_list('user_id','user_name','user_sap_id').distinct()
        
    # options = '<option value="">Select User</option>'
    # if orders_list:                    
    #     for user in orders_list :
    #         store_name = getModelColumnById(SpUsers, user[0], 'store_name')     
    #         options += "<option value="+str(user[0])+">"+store_name+"("+user[1]+"/"+user[2]+")</option>"
    # response['options'] = options
    # return JsonResponse(response)
    orders_list = SpOrders.objects.filter(indent_status=1,block_unblock=1, order_date__icontains=start_date)                 
    
    if organization_id:
        user_ids = SpUsers.objects.filter(organization_id=organization_id).values_list("id" , flat=True)
        if len(user_ids)>0:
            orders_list = orders_list.filter(user_id__in=user_ids)
    orders_list = orders_list.order_by('user_id').values('user_id','user_name','user_sap_id').distinct() 
    options = '<option value="">Select User</option>'
    for order_list in orders_list :
        store_name = getModelColumnById(SpUsers, order_list['user_id'], 'store_name')     
        options += "<option value="+str(order_list['user_id'])+">"+store_name+"("+order_list['user_name']+"/"+order_list['user_sap_id']+")</option>"
    response['options'] = options
# print(len(options))
    return JsonResponse(response)



@login_required
def orderReportUserList(request):
    start_date                   = request.GET['order_date']
    response = {}
    orders_list = SpOrders.objects.filter( indent_status=1,block_unblock=1, order_date__icontains=start_date).order_by('user_id').values_list('user_id','user_name','user_sap_id')
    # print(len(orders_list))
    # for orders in orders_list:
    #     print(orders[0])
    
    options = '<option value="">Select User</option>'
    if orders_list:                    
        for user in orders_list :
            store_name = getModelColumnById(SpUsers, user[0], 'store_name')     
            options += "<option value="+str(user[0])+">"+store_name+"("+user[1]+"/"+user[2]+")</option>"
    response['options'] = options
    return JsonResponse(response)

# get user crate list
@login_required
def getUserCrateDetail(request):
    crate_date                   = request.GET['crate_date']
    user_id                      = request.GET['user_id']
    response = {}
    msg=""
    try:
        user_crate= SpUserCrateLedger.objects.get(user_id=user_id, normal_debit__gt=0, updated_datetime__icontains=crate_date)
    except SpUserCrateLedger.DoesNotExist:
        user_crate=None
    if user_crate:
        if  user_crate.normal_debit and user_crate.jumbo_debit==0: 
            msg="already dispatch "+ str(user_crate.normal_debit) +" normal crate." 
        elif  user_crate.jumbo_debit and user_crate.normal_debit==0: 
            msg="already dispatch " + str(user_crate.jumbo_debit) +" jumbo crate."    
        else:
            msg="already dispatch "+ str(user_crate.normal_debit) +" normal crate and " + str(user_crate.jumbo_debit) +" jumbo crate."    
    response['msg'] = msg
    return JsonResponse(response)


    
# order user option View
@login_required
def orderUserOption(request):
    today                   = request.GET['order_date']
    today                   = datetime.strptime(str(today), '%d/%m/%Y').strftime('%Y-%m-%d')

    response = {}
    options = ''
    condition = " and order_date LIKE '%%"+str(today)+"%%'" 
    users = SpUsers.objects.raw(''' SELECT id,emp_sap_id, CONCAT(first_name," ",middle_name," ", last_name) as name 
                        FROM sp_users WHERE id in (SELECT user_id FROM sp_orders WHERE 1 {condition} order by id asc) 
    
                        '''.format(condition=condition))

    if SpOrders.objects.filter(order_date__icontains=today).exists() :
        first_order = SpOrders.objects.filter(order_date__icontains=today).order_by('id').first()
        user_id = first_order.user_id
    else:
        user_id = 0

    user_details = SpUsers.objects.raw(''' SELECT sp_users.id,sp_users.emp_sap_id,sp_users.store_name, CONCAT(sp_users.first_name," ",sp_users.middle_name," ", sp_users.last_name) 
                    as name ,sp_user_area_allocations.route_name
                    FROM sp_users LEFT JOIN sp_user_area_allocations on sp_user_area_allocations.user_id = sp_users.id 
                    WHERE sp_users.id = %s ''',[user_id])

    if users:                    
        for user in users :
            if user_details:
                if user.id == user_details[0].id:
                    condition = "selected"
                else:
                    condition = ""
            else:
                condition = ""        
            options += "<option value="+str(user.id)+" "+condition+">"+user.emp_sap_id+"("+user.name+"/"+user.store_name+")</option>"
    else:
        options = '<option value="">Select SAP ID</option>'
    response['options'] = options
    return JsonResponse(response)

# order user option View
@login_required
def travelUserOption(request):
    today                   = request.GET['travel_date']
    today                   = datetime.strptime(str(today), '%d/%m/%Y').strftime('%Y-%m-%d')

    response = {}
    options = '<option value="">Select Employee</option>'
    condition = " and created_at LIKE '%%"+str(today)+"%%'" 
    users = SpUsers.objects.raw(''' SELECT id,emp_sap_id, CONCAT(first_name," ",middle_name," ", last_name) as name 
                        FROM sp_users WHERE id in (SELECT user_id FROM sp_user_tracking WHERE 1 group by user_id order by id asc) 
    
                        ''')

    if SpUserTracking.objects.filter().exists() :
        first_order = SpUserTracking.objects.filter().order_by('-id').first()
        user_id = first_order.user_id
    else:
        user_id = 0

    user_details = SpUsers.objects.raw(''' SELECT sp_users.id, CONCAT(sp_users.first_name," ",sp_users.middle_name," ", sp_users.last_name) as name
                    FROM sp_users WHERE sp_users.id = %s ''',[user_id])

    if users:                    
        for user in users :
            if user_details:
                if user.id == user_details[0].id:
                    condition = "selected"
                else:
                    condition = ""
            else:
                condition = ""        
            options += "<option value="+str(user.id)+" "+condition+">"+user.name+"</option>"
    else:
        options = '<option value="">Select Employee</option>'
    response['options'] = options
    return JsonResponse(response)
    
@login_required
def productClassOption(request,largest_unit):
    response = {}
    options = ''
    product_classes = SpProductClass.objects.raw(''' SELECT * FROM sp_product_class WHERE id in 
                    ( SELECT product_class_id FROM sp_product_variants WHERE largest_unit_name=%s) ''',[largest_unit])
    for product_class in product_classes :
        options += "<option value="+str(product_class.id)+">"+product_class.product_class+"</option>"

    response['options'] = options
    return JsonResponse(response)


# State option View
@login_required
def cityOption(request,state_id):
    response = {}
    options = '<option value="" selected>Select City</option>'
    cities = SpCities.objects.filter(state_id=state_id)
    for city in cities :
        options += "<option value="+str(city.id)+">"+city.city+"</option>"

    response['options'] = options
    return JsonResponse(response)

# option View
@login_required
def getOptionsList(request):
    response = {}
    if request.POST['id'] == 'organization_id':
        options = '<option value="" selected>Select Organization </option>'
        production_unit = SpProductionUnit.objects.get(id=request.POST['val'])
        production_units = production_unit.organization_id.split(',')
        
        for production_unit in production_units :
            selects = SpOrganizations.objects.filter(id=int(production_unit))
            for select in selects:
                options += "<option value=" + \
                    str(select.id)+">"+select.organization_name+"</option>"
                    
                    
                response['options'] = options
    elif request.POST['id'] == 'department_id':
        options = '<option value="" selected>Select Department</option>'
        selects = SpDepartments.objects.filter(organization_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.department_name+"</option>"
            response['options'] = options
    elif request.POST['id'] == 'role_id':
        options = '<option value="" selected>Select Role</option>'
        if request.POST['val'] == '33':
            selects = SpRoles.objects.filter(department_id='3')
        else:
            if request.POST['flag'] is not None and request.POST['flag'] =='0':
                selects = SpRoles.objects.filter(department_id=request.POST['val'])
            else:
                selects = SpRoles.objects.filter(department_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.role_name+"</option>"
            response['options'] = options
    elif request.POST['id'] == 'town_id':
        options = '<option value="" selected>Select Town</option>'
        selects = SpTowns.objects.filter(zone_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+select.town+"</option>"
            response['options'] = options
    elif request.POST['id'] == 'vehicle_id':
        options = '<option value="" selected>Select Vehicle</option>'
        selects = SpVehicles.objects.filter(route_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+str(select.registration_number)+"</option>"
        response['options'] = options        
    elif request.POST['id'] == 'slab_id':
        options = '<option value="" selected>Select Slab</option>'
        selects = SpSlabMasterList.objects.filter(product_class_id=request.POST['val'])
        for select in selects :
            options += "<option value="+str(select.id)+">"+str(select.more_than_quantity)+" - "+str(select.upto_quantity)+"</option>"
        response['options'] = options      
    return JsonResponse(response)

@login_required
def getOptionsVehicleList(request):
    context = {}
    if request.POST['id'] == 'vehicle_id':
        user_area_allocations   = SpUserAreaAllocations.objects.get(user_id=request.POST['val'])
        try:
            selects         = SpVehicles.objects.get(route_id = user_area_allocations.route_id)
        except SpVehicles.DoesNotExist:
            selects = None
        vehicle         = SpVehicles.objects.all()
        context['selects_vehicle_id']       =    selects  
        context['vehicle']                  =    vehicle  
    return render(request,'order-management/get-vehicle-list.html',context)


def updateFavorite(request):
    response = {}
    if request.method == "POST":
        current_user                = request.user
        if 'favorite' not in request.POST or request.POST['favorite'] == "" :
            response['flag']        = False
            response['message']     = "favorite is missing"
        elif 'link' not in request.POST or request.POST['link'] == "" :
            response['flag']        = False
            response['message']     = "link is missing"
        else:
            if SpFavorites.objects.filter(favorite=request.POST['favorite'],link=request.POST['link']).exists() :
                SpFavorites.objects.get(favorite=request.POST['favorite'],link=request.POST['link']).delete()

                current_user = request.user
                user_favorites = []
                favorites = SpFavorites.objects.filter(user_id = current_user.id)
                for favorite in favorites :
                    print(favorite.favorite)
                    temp = {}
                    temp['favorite'] = favorite.favorite
                    temp['link'] = favorite.link
                    user_favorites.append(temp)

                    request.session['favorites'] = user_favorites

                    template = 'ajax/favorite.html'
                    return render(request,template)
            else:
                favorite                = SpFavorites()
                favorite.user_id        = current_user.id
                favorite.favorite       = request.POST['favorite']
                favorite.link           = request.POST['link']
                favorite.save()
                if favorite.id :

                    current_user = request.user
                    user_favorites = []
                    favorites = SpFavorites.objects.filter(user_id = current_user.id)
                    for favorite in favorites :
                        temp = {}
                        temp['favorite'] = favorite.favorite
                        temp['link'] = favorite.link
                        user_favorites.append(temp)
                    
                    request.session['favorites'] = user_favorites
                    template = 'ajax/favorite.html'
                    return render(request,template)
                else:
                    response['flag']    = False
                    response['message'] = "Failed to save"
    else:
        response['flag']            = False
        response['message']         = "Method not allowed"

    return JsonResponse(response)

def globalMenuSearch(request):
    context = {}
    template = 'global-menu-search.html'
    return render(request,template,context)

def stateRouteOptions(request,state_id):
    response = {}
    options = '<option value="all">All</option>'
    routes = SpRoutes.objects.filter(state_id=state_id)
    for route in routes : 
         options += "<option value="+str(route.id)+">"+route.route+"</option>"
    
    response['options'] = options
    return JsonResponse(response)

def routeTownOptions(request):
    options = '<option value="all">All</option>'
    route_ids = request.POST['route_ids'].split(',')
    routes = SpZones.objects.raw(''' select * from sp_routes where id in %s ''',[route_ids])
    for route in routes:
        towns = SpRoutesTown.objects.filter(route_id=route.id).order_by('order_index')
        if towns:
            options += '<optgroup label="' + route.route + '">'
            for town in towns : 
                options += "<option value="+str(town.town_id)+">"+town.town_name+"</option>"
            options += '</optgroup>'

    return HttpResponse(options)
@login_required
def productVariantDetails(request,product_variant_id):
    response = {}
    options = ''
    if SpProductVariants.objects.filter(id=product_variant_id).exists():
        product_variant = SpProductVariants.objects.get(id=product_variant_id)
        response['flag'] = True
        response['product'] = model_to_dict(SpProducts.objects.get(id=product_variant.product_id))

        
        options += "<option value='0' selected>"+product_variant.container_name+"</option>"
        options += "<option value='1'>"+product_variant.packaging_type_name+"</option>"
        response['options'] = options

    else:
        response['flag'] = False
        response['flag'] = "Product Variant not found"
        response['options'] = options

    return JsonResponse(response)

@login_required
def getOrderTime(request):    
    shift_id = request.GET['shift_id']
    order_timing = SpWorkingShifts.objects.get(id=shift_id)
    response = {}
    response['flag']          = True
    response['order_timing'] = order_timing.order_timing

    return JsonResponse(response)

@login_required
def getStateTowns(request,state_id):
    response = {}
    if SpStates.objects.filter(id=state_id).exists():
        response['flag'] = True
        towns = list(SpTowns.objects.filter(state_id=state_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "State not found"

    return JsonResponse(response)

@login_required
def checkTownMappingRoute(request,town_id):
    response = {}
    if SpRoutesTown.objects.filter(town_id=town_id).exists():
        response['flag'] = True
        towns = SpRoutesTown.objects.filter(town_id=town_id).first()
        route_name=towns.route_name
        response['message'] = "Town Already Mapped to Route ("+route_name+")"
    else:
        response['flag'] = False
        response['message'] = "Town Does Not Mapped "

    return JsonResponse(response)


@login_required
def getZoneTowns(request,zone_id):
    response = {}
    if SpZones.objects.filter(id=zone_id).exists():
        response['flag'] = True
        towns = list(SpTowns.objects.filter(zone_id=zone_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "Zone not found"

    return JsonResponse(response)

@login_required
def getRouteTowns(request,route_id):
    response = {}
    if SpRoutes.objects.filter(id=route_id).exists():
        response['flag'] = True
        towns = list(SpRoutesTown.objects.filter(route_id=route_id).values())
        response['towns'] = towns
    else:
        response['flag'] = False
        response['message'] = "Route not found"

    return JsonResponse(response)

@login_required
def getMainSubRoute(request,route_id):
    response = {}
    if SpMainRoutes.objects.filter(id=route_id).exists():
        main_route=SpMainRoutes.objects.filter(id=route_id).values("sub_route").first()
        sub_route_id = []
        if main_route['sub_route']:
            sub_route_id=(main_route['sub_route']).split(",")
        response['flag'] = True
        routes = list(SpRoutes.objects.filter(id__in=sub_route_id).values())
        response['routes'] = routes
    else:
        response['flag'] = False
        response['message'] = "Main Route not found"

    return JsonResponse(response)

def getMainSubRouteList(request):
    options = '<option value="all">All</option>'
    route_ids = request.POST['route_ids'].split(',')
    routes = SpMainRoutes.objects.filter(id__in=route_ids).exclude(sub_route='').order_by('id').values("main_route", "sub_route")
    
    for route in routes:
        sub_route_id=(route['sub_route']).split(",")
        
        if sub_route_id:
            options += '<optgroup label="' + route["main_route"] + '">'
            sub_routes = SpRoutes.objects.filter(id__in=sub_route_id)
            for sub_route in sub_routes :
                options += "<option value="+str(sub_route.id)+">"+sub_route.route+"</option>"
            options += '</optgroup>'

    return HttpResponse(options)

def getStateZoneList(request):
    response = {}
    options = '<option value="all">All</option>'
    state_id = request.POST['state_id']
    zones = SpZones.objects.filter(state_id=state_id).order_by('id').values("id", "zone")
    
    for zone in zones:
        options += "<option value="+str(zone['id'])+">"+zone['zone']+"</option>"

    response['options'] = options
    
    route_options = '<option value="all">All</option>'
    routes = SpRoutes.objects.filter(state_id=state_id)
    for route in routes :
        route_options += "<option value="+str(route.id)+">"+route.route+"</option>"
    response['route_options'] = route_options
    
    return JsonResponse(response)

def getZoneTownList(request):
    options = '<option value="all">All</option>'
    zone_ids = request.POST['zone_ids'].split(',')
    zones = SpZones.objects.filter(id__in=zone_ids).order_by('id').values("id", "zone")
    
    for zone in zones:
        towns = SpTowns.objects.filter(zone_id=zone["id"])
        if towns:
            options += '<optgroup label="' + zone["zone"] + '">'
            for town in towns :
                options += "<option value="+str(town.id)+">"+town.town+"</option>"
        options += '</optgroup>'

    return HttpResponse(options)
    
# Variant option View
@login_required
def productOption(request):
    response = {}
    options = '<option value="" selected>Select Product Variant</option>'
    variants = SpUserProductVariants.objects.filter(product_id=request.GET['product_id'], user_id=request.GET['user_id'])
    for variant in variants :
        options += "<option value="+str(variant.product_variant_id)+">"+variant.variant_name+"</option>"

    response['options'] = options
    return JsonResponse(response)


@login_required
def getproductOption(request):
    response = {}
    options = '<option value="" selected>Select Product Variant</option>'
    variants = SpUserProductVariants.objects.filter(product_id=request.GET['product_id'], user_id=request.GET['user_id'])
    for variant in variants :
        options += "<option value="+str(variant.product_variant_id)+">"+variant.variant_name+"</option>"

    response['options'] = options
    return JsonResponse(response)
    
@login_required
def getproductDetails(request):
    response = {}
    options = '<option value="" selected>Select Product Variant</option>'
    variants = SpUserProductVariants.objects.get(product_variant_id=request.GET['product_variant_id'], user_id=request.GET['user_id'])
    
    response['variants'] = model_to_dict(variants)
    response['is_allow'] = getModelColumnById(SpProductVariants,request.GET['product_variant_id'],'is_allow_in_packaging')
    return JsonResponse(response)

# Variant option View
@login_required
def productDetails(request):
    response = {}
    options = '<option value="" selected>Select Product Variant</option>'
    variants = SpUserProductVariants.objects.get(product_variant_id=request.GET['product_variant_id'], user_id=request.GET['user_id'])
    
    response['variants'] = model_to_dict(variants)
    response['is_allow'] = getModelColumnById(SpProductVariants,request.GET['product_variant_id'],'is_allow_in_packaging')
    return JsonResponse(response)

# Variant option View
@login_required
def getProductFreeScheme(request):
    response = {}
    try:
        scheme = SpOrderSchemes.objects.get(order_id=request.GET['order_id'], variant_id=request.GET['product_variant_id'], user_id=request.GET['user_id'], scheme_type='free')
        scheme = model_to_dict(scheme)
    except SpOrderSchemes.DoesNotExist:
        scheme = None
    
    response['scheme'] = scheme
    return JsonResponse(response)

# Variant option View
@login_required
def getSchemeDetails(request):
    variants            = request.GET.getlist('variants[]')
    variants_quantity   = request.GET.getlist('variants_quantity[]')
    response = {}
    bonus_scheme_text = ''
    try:
        free_scheme = SpUserSchemes.objects.get(applied_on_variant_id=request.GET['product_variant_id'], user_id=request.GET['user_id'], scheme_type=1, status=1)
    except SpUserSchemes.DoesNotExist:
        free_scheme = None
    
    if free_scheme and request.GET['quantity']:
        if int(request.GET['quantity']) >= int(free_scheme.minimum_order_quantity):
            free = ''
            if free_scheme.pouch_quantity>0:
                if request.GET['packaging_type'] == '0':
                    free += 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')+'-'
                    quantity = int(free_scheme.pouch_quantity)*int(request.GET['quantity'])
                    if quantity == 1:
                        free += ' '+str(quantity)+' free '+str(free_scheme.order_packaging_name)+'.'
                    else:    
                        free += ' '+str(quantity)+' free '+str(free_scheme.order_packaging_name)+'.'
                else:    
                    quantity = int(request.GET['quantity'])/int(getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'no_of_pouch'))
                    quantity = str(quantity).split('.')
                    quantity = int(quantity[0])
                    if quantity > 0:
                        quantity = int(quantity)*int(free_scheme.pouch_quantity)
                        free += 'Free '+getModelColumnById(SpProductVariants, free_scheme.free_variant_id, 'variant_name')+'-'
                        if quantity == 1:
                            free += ' '+str(quantity)+' free '+str(free_scheme.order_packaging_name)+'.'
                        else:    
                            free += ' '+str(quantity)+' free '+str(free_scheme.order_packaging_name)+'.'
                    else:
                        free_scheme = ''
            free_scheme = free
        else:
            free_scheme = '' 
    
    try:
        flat_scheme = SpUserFlatSchemes.objects.get(applied_on_variant_id=request.GET['product_variant_id'], user_id=request.GET['user_id'], incentive_amount__gt=0, status=1)
    except SpUserFlatSchemes.DoesNotExist:
        flat_scheme = None
    
    if flat_scheme and request.GET['quantity']:
        if int(request.GET['quantity'])>0:
            if request.GET['packaging_type'] == '0':
                flat_discount = (float(request.GET['quantity'])*int(getModelColumnById(SpProductVariants, flat_scheme.applied_on_variant_id, 'no_of_pouch')))*float(getModelColumnById(SpProductVariants, flat_scheme.applied_on_variant_id, 'variant_size'))
                flat_discount = round((float(flat_scheme.incentive_amount)*float(flat_discount)),2)
            else:
                flat_discount = float(request.GET['quantity'])*float(getModelColumnById(SpProductVariants, flat_scheme.applied_on_variant_id, 'variant_size'))
                flat_discount = round((float(flat_scheme.incentive_amount)*float(flat_discount)),2)
            flat = 'Discount of Rs. '+str(flat_discount)+' applied.'
        flat_scheme = flat
    else:
        flat_scheme = '' 
            
    
    if len(variants) > 0:
        total_unit = []
        # for id, variant in enumerate(variants):        
        #     try:
        #         flat_scheme = SpUserFlatSchemes.objects.get(user_id=request.GET['user_id'], status=1)
        #     except SpUserFlatSchemes.DoesNotExist:
        #         flat_scheme = None     
        #     if flat_scheme:
        #         class_list = flat_scheme.product_class_id
        #         class_list = class_list.split(',')    
        #         product_classes =  SpProductClass.objects.filter(pk__in=class_list)
        #         if SpUserProductVariants.objects.filter(product_variant_id=variant, is_bulk_pack=0, product_class_id__in=product_classes).exists():
        #             total_unit_in_ltr_kg = int(getModelColumnById(SpProductVariants, variant, 'no_of_pouch'))*float(getModelColumnById(SpProductVariants, variant, 'variant_size'))
        #             incentive = (total_unit_in_ltr_kg*int(variants_quantity[id]))*float(flat_scheme.incentive_amount)
        #             total_unit.append(incentive)
        #         scheme_name = flat_scheme.scheme_name    
        #     else:
        #         scheme_name = ''
        total_unit = sum(total_unit)
        
        if total_unit > 0:
            bonus_scheme_text             +=  str(total_unit)+' Incentive amount has been applied under the '+scheme_name+' Scheme'
        else:
            bonus_scheme_text             +=  ''
    if free_scheme:
        flat_scheme = '<br/>'+flat_scheme
        
    response['free_scheme']         = free_scheme
    response['flat_scheme']         = flat_scheme
    response['bonus_scheme_text']   = bonus_scheme_text
    return JsonResponse(response)

# Variant option View
@login_required
def getBonusSchemeDetails(request):
    variants            = request.GET.getlist('variants[]')
    variants_quantity   = request.GET.getlist('variants_quantity[]')
    if len(variants_quantity) > 0:
        variant_quantity = sum(int(x) for x in variants_quantity)
    else:
        variant_quantity = 0

    response = {} 
    bonus_scheme_text = ''

    try:
        quantitative_scheme = SpUserSchemes.objects.get(user_id=request.GET['user_id'], scheme_type=2, status=1)
    except SpUserSchemes.DoesNotExist:
        quantitative_scheme = None
    
    if quantitative_scheme and variant_quantity >= quantitative_scheme.minimum_order_quantity:
        free = 'Free '+getModelColumnById(SpProductVariants, quantitative_scheme.free_variant_id, 'variant_name')+'-'
        if quantitative_scheme.container_quantity>0:
            product_id = getModelColumnById(SpProductVariants, quantitative_scheme.free_variant_id, 'product_id')
            free += str(quantitative_scheme.container_quantity)+' free '+getModelColumnById(SpProducts, product_id, 'container_name')+''
            quantitative_container = quantitative_scheme.container_quantity
        else:
            quantitative_container = 0
        if quantitative_scheme.container_quantity>0:
            free += ' and '     
        if quantitative_scheme.pouch_quantity>0:
            quantity = int(quantitative_scheme.pouch_quantity)
            if quantity == 1:
                free += ' '+str(quantity)+' free Pouch under the '+quantitative_scheme.scheme_name+' Scheme'
            else:    
                free += ' '+str(quantity)+' free Pouches under the '+quantitative_scheme.scheme_name+' Scheme'
            quantitative_pouch = quantitative_scheme.pouch_quantity    
        else:
            quantitative_pouch = 0
        quantitative_scheme_id = quantitative_scheme.scheme_id        
        bonus_scheme_text += free
        quantitative_free_variant_id = quantitative_scheme.free_variant_id
    else:
        bonus_scheme_text += ''
        quantitative_scheme_id       = ''
        quantitative_pouch           = 0
        quantitative_container       = 0
        quantitative_free_variant_id = ''   


    if len(variants) > 0:
        total_unit = []
        # for id, variant in enumerate(variants):        
        #     try:
        #         flat_scheme = SpUserFlatSchemes.objects.get(user_id=request.GET['user_id'], status=1)
        #     except SpUserFlatSchemes.DoesNotExist:
        #         flat_scheme = None     
        #     if flat_scheme:
        #         class_list = flat_scheme.product_class_id
        #         class_list = class_list.split(',')    
        #         product_classes =  SpProductClass.objects.filter(pk__in=class_list)    
        #         if SpUserProductVariants.objects.filter(product_variant_id=variant, is_bulk_pack=0, included_in_scheme=1, product_class_id__in=product_classes).exists():
        #             total_unit_in_ltr_kg = int(getModelColumnById(SpProductVariants, variant, 'no_of_pouch'))*float(getModelColumnById(SpProductVariants, variant, 'variant_size'))
        #             incentive = (total_unit_in_ltr_kg*int(variants_quantity[id]))*float(flat_scheme.incentive_amount)
        #             total_unit.append(incentive)
        #         scheme_name         = flat_scheme.scheme_name 
        #         flat_scheme_id      = flat_scheme.scheme_id    
        #         flat_unit_id        = flat_scheme.unit_id    
        #         flat_unit_name      = flat_scheme.unit_name    
        #     else:
        scheme_name         = ''
        flat_scheme_id      = ''
        flat_unit_id        = ''    
        flat_unit_name      = '' 
                    
        total_unit = sum(total_unit)
        
        if total_unit > 0:
            bonus_scheme_text           +=  '<br/>'
            bonus_scheme_text           +=  str(total_unit)+' Incentive amount has been applied under the '+scheme_name+' Scheme'
            flat_scheme_incentive       = str(total_unit)
        else:
            bonus_scheme_text           +=  ''
            flat_scheme_incentive       = ''
    

    if len(variants) > 0:
        total_unit_in_ltrs_kgs = []
        for id, variant in enumerate(variants):        
            try:
                bulk_pack_scheme = SpUserBulkpackSchemes.objects.get(user_id=request.GET['user_id'], status=1)
            except SpUserBulkpackSchemes.DoesNotExist:
                bulk_pack_scheme = None     
            if bulk_pack_scheme:
                class_list = bulk_pack_scheme.product_class_id
                class_list = class_list.split(',')    
                product_classes =  SpProductClass.objects.filter(pk__in=class_list)    
                if SpUserProductVariants.objects.filter(product_variant_id=variant, is_bulk_pack=1, product_class_id__in=product_classes).exists():
                    total_unit_in_ltr_kg = int(getModelColumnById(SpProductVariants, variant, 'no_of_pouch'))*float(getModelColumnById(SpProductVariants, variant, 'variant_size'))
                    total_unit_in_ltr_kg = (total_unit_in_ltr_kg*int(variants_quantity[id]))
                    total_unit_in_ltrs_kgs.append(total_unit_in_ltr_kg)
                bulk_scheme_name = bulk_pack_scheme.scheme_name  
                bulk_scheme_id   = bulk_pack_scheme.scheme_id
                bulk_unit_id     = bulk_pack_scheme.unit_id    
                bulk_unit_name   = bulk_pack_scheme.unit_name        
            else:
                bulk_scheme_name = ''
                bulk_scheme_id   = ''
                bulk_unit_id     = ''  
                bulk_unit_name   = ''
                    
        total_unit_in_ltrs_kgs = sum(total_unit_in_ltrs_kgs)
        
        bulk_pack_incentive = []
        if total_unit_in_ltrs_kgs > 0:
            try:
                bulk_pack_scheme = SpUserBulkpackSchemeBifurcation.objects.filter(user_id=request.GET['user_id'])
            except SpUserBulkpackSchemeBifurcation.DoesNotExist:
                bulk_pack_scheme = None

            if bulk_pack_scheme:
                for bulk_pack in bulk_pack_scheme:
                    if total_unit_in_ltrs_kgs > bulk_pack.above_upto_quantity:   
                        incentive =  float(bulk_pack.incentive_amount)*float(total_unit_in_ltrs_kgs)
                        bulk_pack_incentive.append(incentive)
        if len(bulk_pack_incentive) > 0:
            bonus_scheme_text +=  '<br/>'
            bonus_scheme_text +=  str(bulk_pack_incentive[len(bulk_pack_incentive)-1])+' Incentive amount has been applied under the '+bulk_scheme_name+' Scheme'
            bulk_scheme_incentive = str(bulk_pack_incentive[len(bulk_pack_incentive)-1])
        else:
            bonus_scheme_text += ''
            bulk_scheme_incentive = ''      
    
    response['bonus_scheme_text']               = bonus_scheme_text
    response['bulk_scheme_id']                  = bulk_scheme_id
    response['bulk_scheme_incentive']           = bulk_scheme_incentive
    response['bulk_unit_id']                    = bulk_unit_id
    response['bulk_unit_name']                  = bulk_unit_name
    response['flat_scheme_id']                  = flat_scheme_id
    response['flat_scheme_incentive']           = flat_scheme_incentive
    response['flat_unit_id']                    = flat_unit_id
    response['flat_unit_name']                  = flat_unit_name
    response['quantitative_scheme_id']          = quantitative_scheme_id
    response['quantitative_container']          = quantitative_container
    response['quantitative_pouch']              = quantitative_pouch
    response['quantitative_free_variant_id']    = quantitative_free_variant_id
    return JsonResponse(response)