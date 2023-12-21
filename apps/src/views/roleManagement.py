import sys
import os
import json
from django.core import serializers
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
from utils import getConfigurationResult,getModelColumnById
from datetime import datetime
from datetime import timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

from io import BytesIO
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.conf import settings
from ..decorators import *

# Create your views here.

# roleManagement View
@login_required
@has_par(sub_module_id=2,permission='list')
def index(request):
    context = {}
    permissions = SpPermissions.objects.filter(status=1) 
    modules = SpModules.objects.filter(status=1)
    for module in modules : 
        module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)

    page = request.GET.get('page')
    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, 100)

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
    if page is not None:
           page = page
    else:
           page = 1
    
    total_pages = int(paginator.count/100) 
    if(paginator.count == 0):
        paginator.count = 1
        
    temp = int(total_pages) % paginator.count
    if(temp > 0 and 100!= paginator.count):
        total_pages = total_pages+1
    else:
        total_pages = total_pages
        
        
    role_details = SpRoles.objects.order_by('-id').first()
    if role_details:
        context['role_details'] = role_details
        
        role_permission_workflows = SpRoleWorkflowPermissions.objects.filter(role_id=role_details.id)
        context['role_permission_workflows'] = role_permission_workflows
        for role_permission in role_permission_workflows:
            role_permission.sub_module_name = getModelColumnById(SpSubModules, role_permission.sub_module_id, 'sub_module_name')

    context['roles'] = roles
    context['total_pages'] = total_pages
    context['page_limit'] = 100
    context['permissions'] = permissions
    context['modules'] = modules
    context['page_title'] = "Manage Roles"
    context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
    context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
    context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
    

    template = 'role-permission/role-management/roles.html'

    return render(request, template, context)


@login_required
@has_par(sub_module_id=2,permission='view')
def roleDetails(request,role_id):

    context = {}

    permissions = SpPermissions.objects.filter(status=1) 
    modules = SpModules.objects.filter(status=1)
    for module in modules : 
        module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
    role_details = SpRoles.objects.get(id=role_id)

    role_permission_workflows = SpRoleWorkflowPermissions.objects.filter(role_id=role_id)
    for role_permission in role_permission_workflows:
        role_permission.sub_module_name = getModelColumnById(SpSubModules, role_permission.sub_module_id, 'sub_module_name')

    context['role_details'] = role_details
    context['permissions'] = permissions
    context['modules'] = modules
    context['role_permission_workflows'] = role_permission_workflows
    context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
    context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
    context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')

    template = 'role-permission/role-management/role-details.html'

    return render(request, template, context)


@login_required
@has_par(sub_module_id=2,permission='list')
def ajaxRoleList(request):
    page = request.GET.get('page')
    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, getConfigurationResult('page_limit'))

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
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

    organization_details = SpRoles.objects.order_by('-id').first()

    return render(request, 'role-permission/role-management/ajax-roles.html', {'roles': roles, 'total_pages':total_pages, 'organization_details': organization_details})


@login_required
@has_par(sub_module_id=2,permission='list')
def ajaxRoleLists(request):
    page = request.GET.get('page')

    roles = SpRoles.objects.all().order_by('-id')
    paginator = Paginator(roles, getConfigurationResult('page_limit'))

    try:
        roles = paginator.page(page)
    except PageNotAnInteger:
        roles = paginator.page(1)
    except EmptyPage:
        roles = paginator.page(paginator.num_pages)  
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

    return render(request, 'role-permission/role-management/ajax-organization-lists.html', {'roles': roles, 'total_pages':total_pages})







@login_required
@has_par(sub_module_id=2,permission="add")
def addRole(request):

    if request.method == "POST":
        response = {}
        if SpRoles.objects.filter(department_id=request.POST['department_id'], role_name=request.POST['role_name']).exists():
            response['message'] = "Role already exist"
            response['flag'] = False
        else:
            role = SpRoles()
            role.organization_id = request.POST['organization_id']
            role.organization_name = getModelColumnById(SpOrganizations,request.POST['organization_id'],'organization_name')
            role.department_id = request.POST['department_id']
            role.department_name = getModelColumnById(SpDepartments,request.POST['department_id'],'department_name')
            role.role_name = request.POST['role_name']
            role.responsibilities = request.POST['responsibilities']

            if request.POST['reporting_role_id'] != "" :
                if int(request.POST['reporting_role_id']) > 0 :
                    reporting_department_id = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'department_id')
                    role.reporting_department_id = reporting_department_id
                    role.reporting_department_name = getModelColumnById(SpDepartments,reporting_department_id,'department_name')
                else:
                    role.reporting_department_id = None
                    role.reporting_department_name = None

                role.reporting_role_id = request.POST['reporting_role_id']
                
                if int(request.POST['reporting_role_id']) > 0 :
                    role.reporting_role_name = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'role_name')
                else :
                    role.reporting_role_name = "Super User"

            else :
                role.reporting_department_id = None
                role.reporting_department_name = None
                role.reporting_role_id = None
                role.reporting_role_name = None

            role.status = 1
            role.save()
            if role.id != "" :
                response['role_id'] = role.id
                response['message'] = "Record has been saved successfully."
                response['flag'] = True
            else:
                response['message'] = "Failed to saved"
                response['flag'] = False

        return JsonResponse(response)

    else:

        context = {}
        permissions = SpPermissions.objects.filter(status=1)
        organizations = SpOrganizations.objects.filter(status=1)
        departments = SpDepartments.objects.filter(status=1)

        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        
        for department in departments : 
            department.roles = SpRoles.objects.filter(status=1,department_id=department.id)

        context['permissions'] = permissions
        context['organizations'] = organizations
        context['departments'] = departments
        context['modules'] = modules
        template = 'role-permission/role-management/add-role.html'
        return render(request,template , context)

@login_required
def getAddRolePermission(request,role_id):
    try:
        context = {}
        role = SpRoles.objects.get(id=role_id)

        other_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for department in other_departments : 
            department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id).exclude(id=role.id)
        
        permissions = SpPermissions.objects.filter(status=1)
        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        
        context['permissions'] = permissions
        context['modules'] = modules
        context['role'] = role
        context['other_departments'] = other_departments
        context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
        context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
        context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
        template = 'role-permission/role-management/add-role-permission.html'
        return render(request,template ,context)
    except SpRoles.DoesNotExist:
        return HttpResponse('role not found')

@login_required
def addRolePermission(request):
    if request.method == "POST":
        role = SpRoles.objects.get(id=request.POST['role_id'])
        permissions = SpPermissions.objects.filter(status=1)
        sub_modules = SpSubModules.objects.filter(status=1)
        for sub_module in sub_modules :
            for permission in permissions :
                var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                if var_name in request.POST:
                    role_permission = SpRolePermissions()
                    role_permission.role_id = role.id
                    role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                    role_permission.sub_module_id = sub_module.id
                    role_permission.permission_id = permission.id
                    role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                    role_permission.save()
                    total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                    if request.POST[total_work_flows_var] :

                        role_permission.workflow = request.POST[total_work_flows_var]
                        role_permission.save()

                        total_work_flows = json.loads(request.POST[total_work_flows_var])
                        
                        SpRoleWorkflowPermissions.objects.filter(role_id=role.id,sub_module_id=sub_module.id,permission_id=permission.id).delete()
                        
                        for total_work_flow in total_work_flows :
                            role_permission_level = SpRoleWorkflowPermissions()
                            role_permission_level.role_id = role.id
                            role_permission_level.sub_module_id = sub_module.id
                            role_permission_level.permission_id = permission.id
                            role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                            role_permission_level.level_id = total_work_flow['level_id']
                            role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                            role_permission_level.description = total_work_flow['description']
                            if int(total_work_flow['role_id']) > 0 :
                                role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                            else:
                                role_permission_level.workflow_level_dept_id = None

                            role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                            role_permission_level.status = 1
                            role_permission_level.save()

        response = {}
        response['flag'] = True
        response['message'] = "Record has been updated successfully."
        return JsonResponse(response)
    else:
        return HttpResponse('Method not allowed')
    


def orgDepartmentOption(request,organization_id):
    response = {}
    options = '<option value="" selected>Select</option>'
    departments = SpDepartments.objects.filter(status=1,organization_id=organization_id)
    for department in departments : 
        options += "<option value="+str(department.id)+">"+department.department_name+"</option>"

    response['options'] = options
    return JsonResponse(response)

def orgRoleOption(request,organization_id):
    response = {}
    options = '<option value="">Select</option>'
    options += '<option value="0">Super Admin</option>'
    departments = SpDepartments.objects.filter(status=1,organization_id=organization_id)
    for department in departments : 
        roles = SpRoles.objects.filter(status=1,department_id=department.id)
        if roles:
            options += '<optgroup label="' + department.department_name + '">'
            for role in roles : 
                options += "<option value="+str(role.id)+">"+role.role_name+"</option>"
            options += '</optgroup>'
    

    response['options'] = options
    return JsonResponse(response)

def departmentRoleOption(request,department_id):
    response = {}
    options = '<option value="" selected>Select</option>'
    roles = SpRoles.objects.filter(status=1,department_id=department_id)
    for role in roles : 
        options += "<option value="+str(role.id)+">"+role.role_name+"</option>"

    response['options'] = options
    return JsonResponse(response)



@login_required
@has_par(sub_module_id=2,permission="edit")
def editRole(request,role_id):
    if request.method == "POST":
        response = {}
        if SpRoles.objects.filter(role_name=request.POST['role_name'],department_id=request.POST['department_id']).exclude(id=role_id).exists() :
            response['flag'] = False
            response['message'] = "Role name already exist"
        else:
            role = SpRoles.objects.get(id=role_id)
            role.organization_id = request.POST['organization_id']
            role.organization_name = getModelColumnById(SpOrganizations,request.POST['organization_id'],'organization_name')
            role.department_id = request.POST['department_id']
            role.department_name = getModelColumnById(SpDepartments,request.POST['department_id'],'department_name')
            role.role_name = request.POST['role_name']
            role.responsibilities = request.POST['responsibilities']

            if request.POST['reporting_role_id'] != "" :
                if int(request.POST['reporting_role_id']) > 0 :
                    reporting_department_id = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'department_id')
                    role.reporting_department_id = reporting_department_id
                    role.reporting_department_name = getModelColumnById(SpDepartments,reporting_department_id,'department_name')
                else:
                    role.reporting_department_id = None
                    role.reporting_department_name = None

                role.reporting_role_id = request.POST['reporting_role_id']
                
                if int(request.POST['reporting_role_id']) > 0 :
                    role.reporting_role_name = getModelColumnById(SpRoles,request.POST['reporting_role_id'],'role_name')
                else :
                    role.reporting_role_name = "Super User"

            else :
                role.reporting_department_id = None
                role.reporting_department_name = None
                role.reporting_role_id = None
                role.reporting_role_name = None

            role.save()

            permissions = SpPermissions.objects.filter(status=1)
            sub_modules = SpSubModules.objects.filter(status=1)
             
            SpRolePermissions.objects.filter(role_id=role.id).delete()
            SpRoleWorkflowPermissions.objects.filter(role_id=role.id).delete()

            for sub_module in sub_modules :
                for permission in permissions :                    
                    other_roles = SpRolePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).values('role_id').distinct().exclude(role_id=role.id)
                    if len(other_roles) :
                        for other_role in other_roles :
                            SpRolePermissions.objects.filter(role_id=other_role['role_id']).delete()
                            SpRoleWorkflowPermissions.objects.filter(role_id=other_role['role_id']).delete()

                            var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                            if var_name in request.POST:
                                role_permission = SpRolePermissions()
                                role_permission.role_id = other_role['role_id']
                                role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                                role_permission.sub_module_id = sub_module.id
                                role_permission.permission_id = permission.id
                                role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                role_permission.save()
                                total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                                if request.POST[total_work_flows_var] :

                                    role_permission.workflow = request.POST[total_work_flows_var]
                                    role_permission.save()

                                    total_work_flows = json.loads(request.POST[total_work_flows_var])
                                    
                                    SpRoleWorkflowPermissions.objects.filter(role_id=other_role['role_id'],sub_module_id=sub_module.id,permission_id=permission.id).delete()
                                    
                                    for total_work_flow in total_work_flows :
                                        role_permission_level = SpRoleWorkflowPermissions()
                                        role_permission_level.role_id = other_role['role_id']
                                        role_permission_level.sub_module_id = sub_module.id
                                        role_permission_level.permission_id = permission.id
                                        role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission_level.level_id = total_work_flow['level_id']
                                        role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                        role_permission_level.description = total_work_flow['description']
                                        if int(total_work_flow['role_id']) > 0 :
                                            role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                                        else:
                                            role_permission_level.workflow_level_dept_id = None
                                        role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                                        if 'status' in total_work_flow :
                                            role_permission_level.status = total_work_flow['status']
                                        else:
                                            role_permission_level.status = 1
                                        role_permission_level.save()

                    var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                    if var_name in request.POST:
                        role_permission = SpRolePermissions()
                        role_permission.role_id = role.id
                        role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                        role_permission.sub_module_id = sub_module.id
                        role_permission.permission_id = permission.id
                        role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                        role_permission.save()
                        total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                        if request.POST[total_work_flows_var] :

                            role_permission.workflow = request.POST[total_work_flows_var]
                            role_permission.save()

                            total_work_flows = json.loads(request.POST[total_work_flows_var])
                            
                            SpRoleWorkflowPermissions.objects.filter(role_id=role.id,sub_module_id=sub_module.id,permission_id=permission.id).delete()
                            
                            for total_work_flow in total_work_flows :
                                role_permission_level = SpRoleWorkflowPermissions()
                                role_permission_level.role_id = role.id
                                role_permission_level.sub_module_id = sub_module.id
                                role_permission_level.permission_id = permission.id
                                role_permission_level.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                role_permission_level.level_id = total_work_flow['level_id']
                                role_permission_level.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                role_permission_level.description = total_work_flow['description']
                                if int(total_work_flow['role_id']) > 0 :
                                    role_permission_level.workflow_level_dept_id = getModelColumnById(SpRoles,total_work_flow['role_id'],'department_id')
                                else:
                                    role_permission_level.workflow_level_dept_id = None
                                role_permission_level.workflow_level_role_id = total_work_flow['role_id']
                                if 'status' in total_work_flow :
                                    role_permission_level.status = total_work_flow['status']
                                else:
                                    role_permission_level.status = 1
                                role_permission_level.save()
                                
                                
            # update users role & permission
            updateUsersRole(role.id)
            response['flag']    = True
            response['message'] = "Record has been updated successfully."
        return JsonResponse(response)
    else:
        context = {}
        role = SpRoles.objects.get(id=role_id)
        other_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for department in other_departments : 
            # department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id).exclude(id=role.id)
            department.other_roles = SpRoles.objects.filter(status=1,department_id=department.id)

        permissions = SpPermissions.objects.filter(status=1)
        organizations = SpOrganizations.objects.filter(status=1)
        departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        
        reporting_departments = SpDepartments.objects.filter(status=1,organization_id=role.organization_id)
        for reporting_department in reporting_departments:
            reporting_department.roles = SpRoles.objects.filter(status=1,department_id=reporting_department.id).exclude(id=role_id)
            
        modules = SpModules.objects.filter(status=1)
        for module in modules : 
            module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)
        

        context['role'] = role
        context['other_departments'] = other_departments
        context['permissions'] = permissions
        context['organizations'] = organizations
        context['departments'] = departments
        context['reporting_departments'] = reporting_departments
        context['modules'] = modules
        context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
        context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
        context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
        template = 'role-permission/role-management/edit-role.html'
    return render(request,template , context)



@login_required
@has_par(sub_module_id=2,permission='delete')
def updateRoleStatus(request):

    response = {}
    if request.method == "POST":
        try:
            id = request.POST.get('id')
            is_active = request.POST.get('is_active')

            data = SpRoles.objects.get(id=id)
            data.status = is_active
            data.save()
            response['error'] = False
            response['message'] = "Record has been updated successfully."
        except ObjectDoesNotExist:
            response['error'] = True
            response['message'] = "Method not allowed"
        except Exception as e:
            response['error'] = True
            response['message'] = e
        return JsonResponse(response)
    return redirect('/roles')


def updateUsersRole(role_id):
    users = SpUsers.objects.filter(role_id=role_id).values('id')
    if len(users):
        for user in users :
            role_permissions = SpRolePermissions.objects.filter(role_id=role_id)
            if len(role_permissions):
                SpUserRolePermissions.objects.filter(user_id=user['id'],role_id=role_id).delete()
                for role_permission in role_permissions:
                    user_role_permission = SpUserRolePermissions()
                    user_role_permission.user_id = user['id']
                    user_role_permission.role_id = role_id
                    user_role_permission.module_id = role_permission.module_id
                    user_role_permission.sub_module_id = role_permission.sub_module_id
                    user_role_permission.permission_id = role_permission.permission_id
                    user_role_permission.permission_slug = getModelColumnById(SpPermissions,role_permission.permission_id,'slug')
                    user_role_permission.workflow = role_permission.workflow
                    user_role_permission.save()

                
                role_permission_workflows = SpRoleWorkflowPermissions.objects.filter(role_id=role_id)
                if len(role_permission_workflows):
                    SpUserRoleWorkflowPermissions.objects.filter(user_id=user['id'],role_id=role_id).delete()
                    for role_permission_workflow in role_permission_workflows : 
                        user_role_permission_wf = SpUserRoleWorkflowPermissions()
                        user_role_permission_wf.user_id = user['id']
                        user_role_permission_wf.role_id = role_permission_workflow.role_id
                        user_role_permission_wf.sub_module_id = role_permission_workflow.sub_module_id
                        user_role_permission_wf.permission_id = role_permission_workflow.permission_id
                        user_role_permission_wf.permission_slug = getModelColumnById(SpPermissions,role_permission_workflow.permission_id,'slug')
                        user_role_permission_wf.level_id = role_permission_workflow.level_id
                        user_role_permission_wf.level = role_permission_workflow.level
                        user_role_permission_wf.description = role_permission_workflow.description
                        user_role_permission_wf.workflow_level_dept_id = role_permission_workflow.workflow_level_dept_id
                        user_role_permission_wf.workflow_level_role_id = role_permission_workflow.workflow_level_role_id
                        user_role_permission_wf.status = role_permission_workflow.status
                        user_role_permission_wf.save()