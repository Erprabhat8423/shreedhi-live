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
from ...models import *
from django.db.models import Q
from utils import *
from django.forms.models import model_to_dict

@login_required
def ajaxZoneList(request):
    context = {}
    context['zones'] = SpZones.objects.all().order_by('-id')
    template = 'master/location/ajax-zone-list.html'
    return render(request, template, context)

@login_required
def ajaxTownList(request):
    context = {}
    context['towns'] = SpTowns.objects.all().order_by('-id')
    template = 'master/location/ajax-town-list.html'
    return render(request, template, context)


@login_required
def ajaxRouteList(request):
    context = {}
    context['routes'] = SpRoutes.objects.all().order_by('-id')
    template = 'master/location/ajax-route-list.html'
    return render(request, template, context)

@login_required
def ajaxProductionUnitList(request):
    context = {}
    context['production_units'] = SpProductionUnit.objects.all().order_by('-id')
    template = 'master/location/ajax-production-unit-list.html'
    return render(request, template, context)

@login_required
def ajaxTimeSlotList(request):
    context = {}
    context['timeslots'] = SpTimeSlots.objects.all().order_by('-id')
    template = 'master/location/ajax-time-slot-list.html'
    return render(request, template, context)

    

@login_required
def addZone(request):
    if request.method == "POST":
        response = {}
        if SpZones.objects.filter(zone=request.POST['zone_name']).exists() :
            response['flag'] = False
            response['message'] = "Zone already exists."
        else:
            zone = SpZones()
            zone.state_id = request.POST['state_id']
            zone.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            zone.zone = request.POST['zone_name']
            zone.status=1
            zone.save()
            if zone.id :
                towns = request.POST.getlist('town[]')
                for id, val in enumerate(towns):
                    town = SpTowns.objects.get(id=towns[id])
                    town.zone_id = zone.id
                    town.zone_name = zone.zone
                    town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['towns'] = SpTowns.objects.all()
        template = 'master/location/add-zone.html'
        return render(request, template, context)



@login_required
def editZone(request,zone_id):
    if request.method == "POST":
        response = {}
        zone_id = request.POST['zone_id']
        if SpZones.objects.filter(zone=request.POST['zone_name']).exclude(id=zone_id).exists() :
            response['flag'] = False
            response['message'] = "Zone already exists."
        else:
            zone = SpZones.objects.get(id=zone_id)
            zone.state_id = request.POST['state_id']
            zone.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            zone.zone = request.POST['zone_name']

            zone.save()
            if zone.id :
                towns = request.POST.getlist('town[]')
                for id, val in enumerate(towns):
                    town = SpTowns.objects.get(id=towns[id])
                    town.zone_id = zone.id
                    town.zone_name = zone.zone
                    town.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['zone'] = SpZones.objects.get(id=zone_id)
        context['states'] = SpStates.objects.all()
        context['towns'] = SpTowns.objects.all()
        zone_towns = SpTowns.objects.filter(zone_id=zone_id)
        zone_town_list = []
        if len(zone_towns):
            for zone_town in zone_towns:
                zone_town_list.append(zone_town.id)
        context['zone_town_list'] = zone_town_list
        template = 'master/location/edit-zone.html'
        return render(request, template, context)






@login_required
def addTown(request):
    if request.method == "POST":
        response = {}
        if SpTowns.objects.filter(town=request.POST['town_name']).exists() :
            response['flag'] = False
            response['message'] = "Town name already exists."
        else:
            town = SpTowns()
            if request.POST['zone_id'] != "" :
                town.zone_id = request.POST['zone_id']
                town.zone_name = getModelColumnById(SpZones,request.POST['zone_id'],'zone')
            else:
                town.zone_id = None
                town.zone_name = None
                
            town.state_id = request.POST['state_id']
            town.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            town.town = request.POST['town_name']
            town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['zones'] = SpZones.objects.all()
        template = 'master/location/add-town.html'
        return render(request, template, context)

@login_required
def editTown(request,town_id):
    if request.method == "POST":
        response = {}
        town_id = request.POST['town_id']
        if SpTowns.objects.filter(town=request.POST['town_name']).exclude(id=town_id).exists() :
            response['flag'] = False
            response['message'] = "Town name already exists."
        else:
            town = SpTowns.objects.get(id=town_id)
            if request.POST['zone_id'] != "" :
                town.zone_id = request.POST['zone_id']
                town.zone_name = getModelColumnById(SpZones,request.POST['zone_id'],'zone')
            else:
                town.zone_id = None
                town.zone_name = None
                
            town.state_id = request.POST['state_id']
            town.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            town.town = request.POST['town_name']
            town.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['town'] = SpTowns.objects.get(id=town_id)
        context['states'] = SpStates.objects.all()
        context['zones'] = SpZones.objects.all()
        template = 'master/location/edit-town.html'
        return render(request, template, context)


@login_required
def addRoute(request):
    if request.method == "POST":
        response = {}
        if SpRoutes.objects.filter(route=request.POST['route_name']).exists():
            response['flag'] = False
            response['message'] = "Sub Route name already exists."
        elif SpRoutes.objects.filter(route_code=request.POST['route_code']).exists() :
            response['flag'] = False
            response['message'] = "Sub Route Code already exists."
        else:
            route = SpRoutes()
            route.state_id = request.POST['state_id']
            route.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            route.route = request.POST['route_name']
            route.route_code = request.POST['route_code']
            route.production_unit_id = request.POST['production_unit_id']
            route.status = 1
            route.save()
            if route.id :
                towns = request.POST.getlist('town[]') 
                orders = request.POST.getlist('order[]') 

                for id, val in enumerate(towns):
                    route_town = SpRoutesTown()
                    route_town.route_id = route.id
                    route_town.route_name = request.POST['route_name']
                    route_town.town_id = towns[id]
                    route_town.town_name = getModelColumnById(SpTowns,towns[id],'town')
                    route_town.order_index = orders[id]
                    route_town.save()

            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['states'] = SpStates.objects.all()
        context['towns'] = SpTowns.objects.all()
        context['production_unit'] = SpProductionUnit.objects.all()
        template = 'master/location/add-route.html'
        return render(request, template, context)


@login_required
def editRoute(request,route_id):
    if request.method == "POST":
        response = {}
        route_id = request.POST['route_id']
        if SpRoutes.objects.filter(route=request.POST['route_name']).exclude(id=route_id).exists() :
            response['flag'] = False
            response['message'] = "Sub Route name already exists."
        elif SpRoutes.objects.filter(route_code=request.POST['route_code']).exclude(id=route_id).exists() :
            response['flag'] = False
            response['message'] = "Sub Route Code already exists."
        else:
            route = SpRoutes.objects.get(id=route_id)
            route.state_id = request.POST['state_id']
            route.state_name = getModelColumnById(SpStates,request.POST['state_id'],'state')
            route.route = request.POST['route_name']
            route.route_code = request.POST['route_code']
            route.production_unit_id = request.POST['production_unit_id']
            route.status = 1
            route.save()
            if route.id :

                #delete old record
                SpRoutesTown.objects.filter(route_id=route_id).delete()

                towns = request.POST.getlist('town[]') 
                orders = request.POST.getlist('order[]') 

                for id, val in enumerate(towns):
                    route_town = SpRoutesTown()
                    route_town.route_id = route.id
                    route_town.route_name = request.POST['route_name']
                    route_town.town_id = towns[id]
                    route_town.town_name = getModelColumnById(SpTowns,towns[id],'town')
                    route_town.order_index = orders[id]
                    route_town.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['route'] = route = SpRoutes.objects.get(id=route_id)
        context['route_towns'] = SpRoutesTown.objects.filter(route_id=route_id)
        context['states'] = SpStates.objects.all()
        context['production_unit'] = SpProductionUnit.objects.all()
        context['towns'] = SpTowns.objects.filter(state_id=route.state_id).all()
        template = 'master/location/edit-route.html'
        return render(request, template, context)
 
    
@login_required
def addProductionUnit(request):
    if request.method == "POST":
        response = {}
        if SpProductionUnit.objects.filter(production_unit_name=request.POST['production_unit_name']).exists():
            response['flag'] = False
            response['message'] = "Production Unit Name already exists."
        elif SpProductionUnit.objects.filter(production_unit_code=request.POST['production_unit_code']).exists() and request.POST['production_unit_code']!='':
            response['flag'] = False
            response['message'] = "Production Unit Code already exists."
        else:
            print(','.join([str(elem) for elem in request.POST.getlist('organization[]')]))
            production = SpProductionUnit()
            production.production_unit_name = request.POST['production_unit_name']
            production.production_unit_code = request.POST['production_unit_code']
            production.production_unit_address = request.POST['production_unit_address']
            production.organization_id = ','.join([str(elem) for elem in request.POST.getlist('organization[]')])
            production.status = 1
            production.save()
            
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['organizations'] = SpOrganizations.objects.all()
        template = 'master/location/add-production-unit.html'
        return render(request, template, context)


@login_required
def editProductionUnit(request,production_unit_id):
    if request.method == "POST":
        response = {}
        production_unit_id = request.POST['production_unit_id']
        if SpProductionUnit.objects.filter(production_unit_name=request.POST['production_unit_name']).exclude(id=production_unit_id).exists() :
            response['flag'] = False
            response['message'] = "Production Unit Name already exists."
        elif SpProductionUnit.objects.filter(production_unit_code=request.POST['production_unit_code']).exclude(id=production_unit_id).exists() and request.POST['production_unit_code']!='' :
            response['flag'] = False
            response['message'] = "Production Unit Code already exists."
        else:
            production = SpProductionUnit.objects.get(id=production_unit_id)
            production.production_unit_name = request.POST['production_unit_name']
            production.production_unit_code = request.POST['production_unit_code']
            production.production_unit_address = request.POST['production_unit_address']
            production.organization_id = ','.join([str(elem) for elem in request.POST.getlist('organization[]')])
            production.status = 1
            production.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['production_unit_details'] = route = SpProductionUnit.objects.get(id=production_unit_id)
        context['organizations']  = SpOrganizations.objects.all()
        template = 'master/location/edit-production-unit.html'
        return render(request, template, context)
         
@login_required
def editTimeSlot(request):
    if request.method == "POST":
        response = {}
        SpTimeSlots.objects.filter().delete()
        start_timing       = request.POST.getlist('start_timing[]')
        end_timing         = request.POST.getlist('end_timing[]')
        timing_order       = request.POST.getlist('timing_order[]')
       

        for id, val in enumerate(start_timing): 
            timeSlot                = SpTimeSlots()
            timeSlot.start_timing   = start_timing[id]
            timeSlot.end_timing     = end_timing[id]
            timeSlot.timing_order   = timing_order[id]
            timeSlot.status         = 1
            timeSlot.save()

        response['flag'] = True
        response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['timeslots'] = SpTimeSlots.objects.all()
        template = 'master/location/edit-time-slot.html'
        return render(request, template, context)

@login_required
def updateStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = SpTimeSlots.objects.get(id=id)
            data.status = is_active
            data.save()

            if is_active == '1':
                status = 'Unblock'
            else:
                status = 'Block'
                
            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    
    

@login_required
def ajaxMainRouteList(request):
    context = {}
    context['routes'] = SpMainRoutes.objects.all().order_by('-id')
    template = 'master/location/ajax-main-route-list.html'
    return render(request, template, context)



@login_required
def addMainRoute(request):
    if request.method == "POST":
        response = {}
        
        if SpMainRoutes.objects.filter(Q(main_route=request.POST['route_name']) | Q(main_route_code=request.POST['route_code'])).exists() :
            response['flag'] = False
            response['message'] = "Main Route name or code already exists."
        else:
            route = SpMainRoutes()
            route.main_route = request.POST['route_name']
            route.main_route_code = request.POST['route_code']
            route.sub_route = ','.join([str(elem) for elem in request.POST.getlist('sub_route[]')])
            route.status = 1
            route.save()
            
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['routes'] = SpRoutes.objects.filter(status=1).all()
        template = 'master/location/add-main-route.html'
        return render(request, template, context)


@login_required
def editMainRoute(request,route_id):
    if request.method == "POST":
        response = {}
        route_id = request.POST['route_id']
        if SpMainRoutes.objects.filter(Q(main_route=request.POST['route_name']) | Q(main_route_code=request.POST['route_code'])).exclude(id=route_id).exists() :
            response['flag'] = False
            response['message'] = "Route name already exists."
        else:
            route = SpMainRoutes.objects.get(id=route_id)
            route.main_route = request.POST['route_name']
            route.main_route_code = request.POST['route_code']
            route.sub_route = ','.join([str(elem) for elem in request.POST.getlist('sub_route[]')])
            route.status = 1
            route.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        route = SpMainRoutes.objects.get(id=route_id)
        sub_route_id=(route.sub_route).split(",")
        route.sub_route=sub_route_id
        context['main_route'] = route
        context['routes'] = SpRoutes.objects.filter(status=1).all()
        template = 'master/location/edit-main-route.html'
        return render(request, template, context)
    

@login_required
def updateMainRoute(request):
    if request.method == "POST":
        response = {}
        route_id = request.POST['route_id']
        if SpMainRoutes.objects.filter(id=route_id).exists() :
            route = SpMainRoutes.objects.get(id=route_id)
            route.status = request.POST['is_active']
            route.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Route name does not exists."
            
            
        return JsonResponse(response)

    
  

@login_required
def ajaxPackagingTypeList(request):
    context = {}
    context['packaging_types'] = SpPackagingType.objects.all().order_by('-id')
    template = 'master/location/ajax-packaging-type-list.html'
    return render(request, template, context)



@login_required
def addPackagingType(request):
    if request.method == "POST":
        response = {}
        
        if SpPackagingType.objects.filter(packaging_type=request.POST['packaging_type']).exists() :
            response['flag'] = False
            response['message'] = "Packaging Type already exists."
        else:
            packaging_type = SpPackagingType()
            packaging_type.packaging_type = request.POST['packaging_type']
            packaging_type.status = 1
            packaging_type.save()
            
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        template = 'master/location/add-packaging-type.html'
        return render(request, template, context)


@login_required
def editPackagingType(request,id):
    if request.method == "POST":
        response = {}
        id = request.POST['id']
        if SpPackagingType.objects.filter(packaging_type=request.POST['packaging_type']).exclude(id=id).exists() :
            response['flag'] = False
            response['message'] = "Packaging Type already exists."
        else:
            packaging_type = SpPackagingType.objects.get(id=id)
            packaging_type.packaging_type = request.POST['packaging_type']
            packaging_type.save()
            
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['packaging_type'] = SpPackagingType.objects.get(id=id)
        template = 'master/location/edit-packaging-type.html'
        return render(request, template, context)
    


@login_required
def updatePackagingTypeStatus(request):
    if request.method == "POST":
        response = {}
        id = request.POST['id']
        if SpPackagingType.objects.filter(id=id).exists() :
            packaging_type = SpPackagingType.objects.get(id=id)
            packaging_type.status = request.POST['is_active']
            packaging_type.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Route name does not exists."
            
            
        return JsonResponse(response)

    
    

@login_required
def ajaxContainersList(request):
    context = {}
    context['containers'] = SpContainers.objects.all().order_by('-id')
    template = 'master/location/ajax-containers-list.html'
    return render(request, template, context)



@login_required
def addContainers(request):
    if request.method == "POST":
        response = {}
        
        if SpContainers.objects.filter(container=request.POST['containers']).exists() :
            response['flag'] = False
            response['message'] = "Container name already exists."
        else:
            containers = SpContainers()
            containers.container = request.POST['containers']
            containers.is_returnable = request.POST['is_returnable']
            containers.status = 1
            containers.save()
            
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        template = 'master/location/add-containers.html'
        return render(request, template, context)


@login_required
def editContainers(request,id):
    if request.method == "POST":
        response = {}
        if SpContainers.objects.filter(container=request.POST['containers']).exclude(id=id).exists() :
            response['flag'] = False
            response['message'] = "Container name already exists."
        else:
            containers = SpContainers.objects.get(id=id)
            containers.container = request.POST['containers']
            containers.is_returnable = request.POST['is_returnable']
            containers.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['containers'] = SpContainers.objects.get(id=id)
        template = 'master/location/edit-containers.html'
        return render(request, template, context)
    


@login_required
def updateContainersStatus(request):
    if request.method == "POST":
        response = {}
        id = request.POST['id']
        if SpContainers.objects.filter(id=id).exists() :
            containers = SpContainers.objects.get(id=id)
            containers.status = request.POST['is_active']
            containers.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Route name does not exists."
            
            
        return JsonResponse(response)


@login_required
def ajaxProductClassList(request):
    context = {}
    context['product_class'] = SpProductClass.objects.all().order_by('-id')
    template = 'master/location/ajax-product-class-list.html'
    return render(request, template, context)


@login_required
def addProductClass(request):
    if request.method == "POST":
        response = {}
        
        if SpProductClass.objects.filter(product_class=request.POST['product_class']).exists() :
            response['flag'] = False
            response['message'] = "Product Class already exists."
        elif SpProductClass.objects.filter(product_hsn=request.POST['product_hsn']).exists() :
            response['flag'] = False
            response['message'] = "Product HSN already exists."
        else:
            product_class = SpProductClass()
            product_class.product_class = request.POST['product_class']
            product_class.product_hsn = request.POST['product_hsn']
            product_class.order_of = request.POST['order_of']
            product_class.unit = request.POST['unit']
            product_class.status = 1
            product_class.save()
            
            response['flag'] = True
            response['message'] = "Record has been saved successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['units'] = SpProductUnits.objects.raw('''SELECT * FROM `sp_product_units` GROUP By largest_unit''')
        template = 'master/location/add-product-class.html'
        return render(request, template, context)


@login_required
def editProductClass(request,id):
    if request.method == "POST":
        response = {}
        if SpProductClass.objects.filter(product_class=request.POST['product_class']).exclude(id=id).exists() :
            response['flag'] = False
            response['message'] = "Product Class already exists."
        elif SpProductClass.objects.filter(product_hsn=request.POST['product_hsn']).exclude(id=id).exists() :
            response['flag'] = False
            response['message'] = "Product HSN already exists."
        else:
            product_class = SpProductClass.objects.get(id=id)
            product_class.product_class = request.POST['product_class']
            product_class.product_hsn = request.POST['product_hsn']
            product_class.order_of = request.POST['order_of']
            product_class.unit = request.POST['unit']
            product_class.status = 1
            product_class.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['units'] = SpProductUnits.objects.raw('''SELECT * FROM `sp_product_units` GROUP By largest_unit''')
        context['product_class'] = SpProductClass.objects.get(id=id)
        template = 'master/location/edit-product-class.html'
        return render(request, template, context)
    
@login_required
def updateProductClassStatus(request):
    if request.method == "POST":
        response = {}
        id = request.POST['id']
        if SpProductClass.objects.filter(id=id).exists() :
            product_class = SpProductClass.objects.get(id=id)
            product_class.status = request.POST['is_active']
            product_class.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Route name does not exists."
            
            
        return JsonResponse(response)

    
    
@login_required
def updateRouteStatus(request):
    if request.method == "POST":
        response = {}
        route_id = request.POST['route_id']
        if SpRoutes.objects.filter(id=route_id).exists() :
            route = SpRoutes.objects.get(id=route_id)
            route.status = request.POST['is_active']
            route.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Route name does not exists."
            
            
        return JsonResponse(response)

@login_required
def updateProductionUnitStatus(request):
    if request.method == "POST":
        response = {}
        production_unit_id = request.POST['production_unit_id']
        if SpProductionUnit.objects.filter(id=production_unit_id).exists() :
            production = SpProductionUnit.objects.get(id=production_unit_id)
            production.status = request.POST['is_active']
            production.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Production unit name does not exists."
            
            
        return JsonResponse(response) 

@login_required
def ajaxIncentiveSlabList(request):
    context = {}
    context['slab_lists'] = SpSlabMasterList.objects.raw(''' Select sl.*, pc.product_class from sp_slab_master_list sl left join sp_product_class pc on sl.product_class_id=pc.id order by sl.id desc''')
    template = 'master/location/ajax-incentive-slab-list.html'
    return render(request, template, context)



@login_required
def addIncentiveSlab(request):
    if request.method == "POST":
        response = {}
        
        if SpSlabMasterList.objects.filter(product_class_id=request.POST['product_class_id'],more_than_quantity=request.POST['more_than_quantity'],upto_quantity=request.POST['upto_quantity']).exists() :
            response['flag'] = False
            response['message'] = "Incentive Slab already exists."
        else:
            incentive_slab = SpSlabMasterList()
            incentive_slab.product_class_id = request.POST['product_class_id']
            incentive_slab.more_than_quantity = request.POST['more_than_quantity']
            incentive_slab.upto_quantity = request.POST['upto_quantity']
            incentive_slab.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['product_class_list'] = SpProductClass.objects.filter(status=1)
        template = 'master/location/add-incentive-slab.html'
        return render(request, template, context)


@login_required
def editIncentiveSlab(request,id):
    if request.method == "POST":
        response = {}
        if SpSlabMasterList.objects.filter(product_class_id=request.POST['product_class_id'],more_than_quantity=request.POST['more_than_quantity'],upto_quantity=request.POST['upto_quantity']).exclude(id=id).exists() :
            response['flag'] = False
            response['message'] = "Incentive Slab already exists."
        else:
            incentive_slab = SpSlabMasterList.objects.get(id=id)
            incentive_slab.product_class_id = request.POST['product_class_id']
            incentive_slab.more_than_quantity = request.POST['more_than_quantity']
            incentive_slab.upto_quantity = request.POST['upto_quantity']
            incentive_slab.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['product_class_list'] = SpProductClass.objects.filter(status=1)
        context['incentive_slab'] = SpSlabMasterList.objects.get(id=id)
        template = 'master/location/edit-incentive-slab.html'
        return render(request, template, context)        

def ajaxBanks(request):
    context = {}
    banks = SpBankDetails.objects.all().order_by('-id')
    for bank in banks:
        organization_id = bank.organization_id.split(',')
        bank.organization_name = SpOrganizations.objects.filter(id__in=organization_id)
    context['banks'] = banks
    template = 'master/location/ajax-banks.html'
    return render(request, template, context)


def addBankDetails(request):
    if request.method == "POST":
        response = {}
        production_unit_id   = ','.join([str(elem) for elem in request.POST.getlist('production_unit_id[]')])
        if SpBankDetails.objects.filter(account_no__icontains=request.POST['account_no'], organization_id__in=request.POST.getlist('production_unit_id[]')).exists():
            response['flag'] = False
            response['message'] = "Bank already exists."
        else:
            banks = SpBankDetails()
            banks.bank_name = request.POST['bank_name']
            banks.account_no = request.POST['account_no']
            banks.organization_id = production_unit_id
            banks.created_by = request.user.id
            banks.status = 1
            banks.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        context['production_unit'] = SpOrganizations.objects.filter()
        template = 'master/location/add-bank-details.html'
        return render(request, template, context)


def editBankDetails(request,bank_id):
    if request.method == "POST":
        response = {}
        organization_id = ','.join(
            [str(elem) for elem in request.POST.getlist('production_unit_id[]')])
        if SpBankDetails.objects.filter(account_no__icontains=request.POST['account_no'], organization_id__in=organization_id).exclude(id=bank_id).exists():
            response['flag'] = False
            response['message'] = "Bank already exists."
        else:
            banks = SpBankDetails.objects.get(id=bank_id)
            banks.bank_name = request.POST['bank_name']
            banks.account_no = request.POST['account_no']
            banks.organization_id = organization_id
            banks.created_by = request.user.id
            banks.status = 1
            banks.save()
            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)

    else:
        context = {}
        banks   = SpBankDetails.objects.get(id=bank_id)
        organization_id = banks.organization_id.split(',')
        organization = SpOrganizations.objects.all()
        for production_unit in organization:
            if str(production_unit.id) in organization_id:
                production_unit.selected = 'selected'
            else:
                production_unit.selected = ''

        context['production_unit'] = organization
        context['banks']            = banks
        template = 'master/location/edit-bank-details.html'
        return render(request, template, context)

def updateBankStatus(request):
    if request.method == "POST":
        response = {}
        id = request.POST['id']
        if SpBankDetails.objects.filter(id=id).exists():
            route = SpBankDetails.objects.get(id=id)
            route.status = request.POST['is_active']
            route.save()

            response['flag'] = True
            response['message'] = "Record has been updated successfully."
        else:
            response['flag'] = False
            response['message'] = "Bank does not exists."

        return JsonResponse(response)


