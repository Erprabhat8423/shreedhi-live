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
from io import BytesIO
from django.template.loader import get_template
from django.views import View
from django.conf import settings
from ..decorators import *

# Create your views here.

@login_required
@has_par(sub_module_id=33,permission='list')
def index(request):
    context = {}
    roles = SpRoles.objects.filter(status=1) 
    permissions = SpPermissions.objects.filter(status=1) 
    modules = SpModules.objects.filter(status=1)
    for module in modules : 
        module.sub_modules = SpSubModules.objects.filter(status=1,module_id=module.id)

    departments = SpDepartments.objects.filter(status=1)
    for department in departments : 
        department.roles = SpRoles.objects.filter(status=1,department_id=department.id)
    
    for module in modules:
        for sub_module in module.sub_modules:
            permission_data = []
            for permission in permissions:
                temp = {}
                temp['id'] = permission.id
                temp['permission'] = permission.permission
                temp['slug'] = permission.slug
                if SpModulePermissions.objects.filter(module_id=module.id,sub_module_id=sub_module.id,permission_id=permission.id).exists():
                    module_permission = SpModulePermissions.objects.get(module_id=module.id,sub_module_id=sub_module.id,permission_id=permission.id)
                    temp['module_permission'] = module_permission
                    workflow = json.loads(module_permission.workflow)
                    temp['workflow_length'] = len(workflow)
                else:
                    temp['module_permission'] = None
                    temp['workflow_length'] = 0

                permission_data.append(temp)

            sub_module.permissions = permission_data
                

    context['modules'] = modules
    context['permissions'] = permissions
    context['departments'] = departments
    context['page_title'] = "Manage Workflows & Permission "
    context['first_workflow_level'] =  SpWorkflowLevels.objects.get(priority='first')
    context['last_workflow_level'] =  SpWorkflowLevels.objects.get(priority='last')
    context['middle_workflow_level'] =  SpWorkflowLevels.objects.get(priority='middle')
    

    template = 'permission-workflows/index.html'

    return render(request, template, context)



@login_required
@has_par(sub_module_id=33,permission='edit')
def updatePermissionWorkflows(request):
    if request.method == "POST":

        #delete all user permissions
        SpUserModulePermissions.objects.all().delete()
        SpUserRolePermissions.objects.all().delete()
        SpUserRoleWorkflowPermissions.objects.all().delete()

        permissions = SpPermissions.objects.filter(status=1)
        sub_modules = SpSubModules.objects.filter(status=1)
        for sub_module in sub_modules :
            for permission in permissions :
                var_name = 'permission_'+ str(sub_module.id) + '_' + str(permission.id)
                # delete old data
                SpModulePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                SpRolePermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                
                if var_name in request.POST:
                    module_permission = SpModulePermissions()
                    module_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                    module_permission.sub_module_id = sub_module.id
                    module_permission.permission_id = permission.id
                    module_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                    module_permission.save()
                    total_work_flows_var = 'workflow_'+str(sub_module.id)+'_'+str(permission.id)
                    if request.POST[total_work_flows_var] :

                        module_permission.workflow = request.POST[total_work_flows_var]
                        module_permission.save()

                        total_work_flows = json.loads(request.POST[total_work_flows_var])

                        # delete old data
                        SpPermissionWorkflows.objects.filter(sub_module_id=sub_module.id,permission_id=permission.id).delete()
                        
                        for total_work_flow in total_work_flows :
                            permission_workflow = SpPermissionWorkflows()
                            permission_workflow.sub_module_id = sub_module.id
                            permission_workflow.permission_id = permission.id
                            permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                            permission_workflow.level_id = total_work_flow['level_id']
                            permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                            permission_workflow.description = total_work_flow['description']
                            permission_workflow.status = 1
                            permission_workflow.save()

                            level_roles = total_work_flow['role_id'].split(',')
                            # delete old data
                            SpPermissionWorkflowRoles.objects.filter(level_id=total_work_flow['level_id'],sub_module_id=sub_module.id,permission_id=permission.id).delete()
                            
                            
                            for level_role in level_roles:
                                permission_workflow_role = SpPermissionWorkflowRoles()
                                permission_workflow_role.sub_module_id = sub_module.id
                                permission_workflow_role.permission_id = permission.id
                                permission_workflow_role.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                permission_workflow_role.level_id = total_work_flow['level_id']

                                if int(level_role) > 0 :
                                    permission_workflow_role.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                    permission_workflow_role.workflow_level_dept_name = getModelColumnById(SpDepartments,permission_workflow_role.workflow_level_dept_id,'department_name')
                                    permission_workflow_role.workflow_level_role_id = level_role
                                    permission_workflow_role.workflow_level_role_name = getModelColumnById(SpRoles,level_role,'role_name')
                                else:
                                    permission_workflow_role.workflow_level_dept_id = None
                                    permission_workflow_role.workflow_level_dept_name = None
                                    permission_workflow_role.workflow_level_role_id = level_role
                                    permission_workflow_role.workflow_level_role_name = "Super Admin"

                                permission_workflow_role.save()

                                # add role permission & workflow
                                if int(level_role) > 0 :
                                    if not SpRolePermissions.objects.filter(role_id=level_role,sub_module_id=sub_module.id,permission_id=permission.id).exists():
                                        role_permission = SpRolePermissions()
                                        role_permission.role_id = level_role
                                        role_permission.module_id = getModelColumnById(SpSubModules,sub_module.id,'module_id')
                                        role_permission.sub_module_id = sub_module.id
                                        role_permission.permission_id = permission.id
                                        role_permission.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission.save()

                                        role_permission_workflow = SpRoleWorkflowPermissions()
                                        role_permission_workflow.role_id = level_role
                                        role_permission_workflow.sub_module_id = sub_module.id
                                        role_permission_workflow.permission_id = permission.id
                                        role_permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission.id,'slug')
                                        role_permission_workflow.level_id = total_work_flow['level_id']
                                        role_permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                        role_permission_workflow.description = total_work_flow['description']
                                        role_permission_workflow.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                        role_permission_workflow.workflow_level_role_id = level_role
                                        role_permission_workflow.status = 1
                                        role_permission_workflow.save()

                                        # update user role
                                        updateUsersRole(level_role)


        response = {}
        response['flag'] = True
        response['message'] = "Record has been updated successfully."
        return JsonResponse(response)
    else:
        return HttpResponse('Method not allowed')
    

def updatePermissionAndWorkflows(request):
    response = {}
    if request.method == "POST":
        if request.POST['type'] == "":
            sub_module_id = request.POST['sub_module_id']
            permission_id = request.POST['permission_id']
            module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
            if not SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                module_permission = SpModulePermissions()
                module_permission.module_id = module_id
                module_permission.sub_module_id = sub_module_id
                module_permission.permission_id = permission_id
                module_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                module_permission.save()
            else:
                module_permission = SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).first()


            if request.POST['workflow'] :

                module_permission.workflow = request.POST['workflow']
                module_permission.save()

                total_work_flows = json.loads(request.POST['workflow'])

                # delete old data
                SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                
                for total_work_flow in total_work_flows :
                    permission_workflow = SpPermissionWorkflows()
                    permission_workflow.sub_module_id = sub_module_id
                    permission_workflow.permission_id = permission_id
                    permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                    permission_workflow.level_id = total_work_flow['level_id']
                    permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                    permission_workflow.description = total_work_flow['description']
                    permission_workflow.status = 1
                    permission_workflow.save()

                    level_roles = total_work_flow['role_id'].split(',')
                    # delete old data
                    SpPermissionWorkflowRoles.objects.filter(level_id=total_work_flow['level_id'],sub_module_id=sub_module_id,permission_id=permission_id).delete()
                    
                    
                    for level_role in level_roles:
                        permission_workflow_role = SpPermissionWorkflowRoles()
                        permission_workflow_role.sub_module_id = sub_module_id
                        permission_workflow_role.permission_id = permission_id
                        permission_workflow_role.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                        permission_workflow_role.level_id = total_work_flow['level_id']

                        if int(level_role) > 0 :
                            permission_workflow_role.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                            permission_workflow_role.workflow_level_dept_name = getModelColumnById(SpDepartments,permission_workflow_role.workflow_level_dept_id,'department_name')
                            permission_workflow_role.workflow_level_role_id = level_role
                            permission_workflow_role.workflow_level_role_name = getModelColumnById(SpRoles,level_role,'role_name')
                        else:
                            permission_workflow_role.workflow_level_dept_id = None
                            permission_workflow_role.workflow_level_dept_name = None
                            permission_workflow_role.workflow_level_role_id = level_role
                            permission_workflow_role.workflow_level_role_name = "Super Admin"

                        permission_workflow_role.save()

                        # add role permission & workflow
                        if int(level_role) > 0 :
                            if not SpRolePermissions.objects.filter(role_id=level_role,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                                role_permission = SpRolePermissions()
                                role_permission.role_id = level_role
                                role_permission.module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                                role_permission.sub_module_id = sub_module_id
                                role_permission.permission_id = permission_id
                                role_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                role_permission.save()

                                role_permission_workflow = SpRoleWorkflowPermissions()
                                role_permission_workflow.role_id = level_role
                                role_permission_workflow.sub_module_id = sub_module_id
                                role_permission_workflow.permission_id = permission_id
                                role_permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                role_permission_workflow.level_id = total_work_flow['level_id']
                                role_permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                role_permission_workflow.description = total_work_flow['description']
                                role_permission_workflow.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                role_permission_workflow.workflow_level_role_id = level_role
                                role_permission_workflow.status = 1
                                role_permission_workflow.save()

                                # update user role
                                updateUsersRole(level_role)

        elif request.POST['type'] == "verticle":
            sub_modules = SpSubModules.objects.filter(status=1)
            for sub_module in sub_modules:
                sub_module_id = sub_module.id

                permission_id = request.POST['permission_id']
                module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                if not SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                    module_permission = SpModulePermissions()
                    module_permission.module_id = module_id
                    module_permission.sub_module_id = sub_module_id
                    module_permission.permission_id = permission_id
                    module_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                    module_permission.save()
                else:
                    module_permission = SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).first()


                if request.POST['workflow'] :

                    module_permission.workflow = request.POST['workflow']
                    module_permission.save()

                    total_work_flows = json.loads(request.POST['workflow'])

                    # delete old data
                    SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                    
                    for total_work_flow in total_work_flows :
                        permission_workflow = SpPermissionWorkflows()
                        permission_workflow.sub_module_id = sub_module_id
                        permission_workflow.permission_id = permission_id
                        permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                        permission_workflow.level_id = total_work_flow['level_id']
                        permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                        permission_workflow.description = total_work_flow['description']
                        permission_workflow.status = 1
                        permission_workflow.save()

                        level_roles = total_work_flow['role_id'].split(',')
                        # delete old data
                        SpPermissionWorkflowRoles.objects.filter(level_id=total_work_flow['level_id'],sub_module_id=sub_module_id,permission_id=permission_id).delete()
                        
                        
                        for level_role in level_roles:
                            permission_workflow_role = SpPermissionWorkflowRoles()
                            permission_workflow_role.sub_module_id = sub_module_id
                            permission_workflow_role.permission_id = permission_id
                            permission_workflow_role.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                            permission_workflow_role.level_id = total_work_flow['level_id']

                            if int(level_role) > 0 :
                                permission_workflow_role.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                permission_workflow_role.workflow_level_dept_name = getModelColumnById(SpDepartments,permission_workflow_role.workflow_level_dept_id,'department_name')
                                permission_workflow_role.workflow_level_role_id = level_role
                                permission_workflow_role.workflow_level_role_name = getModelColumnById(SpRoles,level_role,'role_name')
                            else:
                                permission_workflow_role.workflow_level_dept_id = None
                                permission_workflow_role.workflow_level_dept_name = None
                                permission_workflow_role.workflow_level_role_id = level_role
                                permission_workflow_role.workflow_level_role_name = "Super Admin"

                            permission_workflow_role.save()

                            # add role permission & workflow
                            if int(level_role) > 0 :
                                if not SpRolePermissions.objects.filter(role_id=level_role,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                                    role_permission = SpRolePermissions()
                                    role_permission.role_id = level_role
                                    role_permission.module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                                    role_permission.sub_module_id = sub_module_id
                                    role_permission.permission_id = permission_id
                                    role_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                    role_permission.save()

                                    role_permission_workflow = SpRoleWorkflowPermissions()
                                    role_permission_workflow.role_id = level_role
                                    role_permission_workflow.sub_module_id = sub_module_id
                                    role_permission_workflow.permission_id = permission_id
                                    role_permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                    role_permission_workflow.level_id = total_work_flow['level_id']
                                    role_permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                    role_permission_workflow.description = total_work_flow['description']
                                    role_permission_workflow.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                    role_permission_workflow.workflow_level_role_id = level_role
                                    role_permission_workflow.status = 1
                                    role_permission_workflow.save()

                                    # update user role
                                    updateUsersRole(level_role)
            

        elif request.POST['type'] == "horizontal":
            permissions = SpPermissions.objects.all()
            for permission in permissions:
                permission_id = permission.id
                sub_module_id = request.POST['sub_module_id']
                module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                if not SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                    module_permission = SpModulePermissions()
                    module_permission.module_id = module_id
                    module_permission.sub_module_id = sub_module_id
                    module_permission.permission_id = permission_id
                    module_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                    module_permission.save()
                else:
                    module_permission = SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).first()


                if request.POST['workflow'] :

                    module_permission.workflow = request.POST['workflow']
                    module_permission.save()

                    total_work_flows = json.loads(request.POST['workflow'])

                    # delete old data
                    SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                    
                    for total_work_flow in total_work_flows :
                        permission_workflow = SpPermissionWorkflows()
                        permission_workflow.sub_module_id = sub_module_id
                        permission_workflow.permission_id = permission_id
                        permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                        permission_workflow.level_id = total_work_flow['level_id']
                        permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                        permission_workflow.description = total_work_flow['description']
                        permission_workflow.status = 1
                        permission_workflow.save()

                        level_roles = total_work_flow['role_id'].split(',')
                        # delete old data
                        SpPermissionWorkflowRoles.objects.filter(level_id=total_work_flow['level_id'],sub_module_id=sub_module_id,permission_id=permission_id).delete()
                        
                        
                        for level_role in level_roles:
                            permission_workflow_role = SpPermissionWorkflowRoles()
                            permission_workflow_role.sub_module_id = sub_module_id
                            permission_workflow_role.permission_id = permission_id
                            permission_workflow_role.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                            permission_workflow_role.level_id = total_work_flow['level_id']

                            if int(level_role) > 0 :
                                permission_workflow_role.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                permission_workflow_role.workflow_level_dept_name = getModelColumnById(SpDepartments,permission_workflow_role.workflow_level_dept_id,'department_name')
                                permission_workflow_role.workflow_level_role_id = level_role
                                permission_workflow_role.workflow_level_role_name = getModelColumnById(SpRoles,level_role,'role_name')
                            else:
                                permission_workflow_role.workflow_level_dept_id = None
                                permission_workflow_role.workflow_level_dept_name = None
                                permission_workflow_role.workflow_level_role_id = level_role
                                permission_workflow_role.workflow_level_role_name = "Super Admin"

                            permission_workflow_role.save()

                            # add role permission & workflow
                            if int(level_role) > 0 :
                                if not SpRolePermissions.objects.filter(role_id=level_role,sub_module_id=sub_module_id,permission_id=permission_id).exists():
                                    role_permission = SpRolePermissions()
                                    role_permission.role_id = level_role
                                    role_permission.module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                                    role_permission.sub_module_id = sub_module_id
                                    role_permission.permission_id = permission_id
                                    role_permission.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                    role_permission.save()

                                    role_permission_workflow = SpRoleWorkflowPermissions()
                                    role_permission_workflow.role_id = level_role
                                    role_permission_workflow.sub_module_id = sub_module_id
                                    role_permission_workflow.permission_id = permission_id
                                    role_permission_workflow.permission_slug = getModelColumnById(SpPermissions,permission_id,'slug')
                                    role_permission_workflow.level_id = total_work_flow['level_id']
                                    role_permission_workflow.level = getModelColumnById(SpWorkflowLevels,total_work_flow['level_id'],'level')
                                    role_permission_workflow.description = total_work_flow['description']
                                    role_permission_workflow.workflow_level_dept_id = getModelColumnById(SpRoles,level_role,'department_id')
                                    role_permission_workflow.workflow_level_role_id = level_role
                                    role_permission_workflow.status = 1
                                    role_permission_workflow.save()

                                    # update user role
                                    updateUsersRole(level_role)
            
        response['flag'] = True
        response['message'] = "Record updated Successfully"
    else:
        response['flag'] = False
        response['message'] = "Method not allowed."

    return JsonResponse(response)

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

def removePermissionAndWorkflows(request):
    response = {}
    if request.method == "POST":
        if request.POST['type'] == "":
        
            sub_module_id = request.POST['sub_module_id']
            permission_id = request.POST['permission_id']
            module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')

            SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpPermissionWorkflowRoles.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpUserRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
            SpUserRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
        
        elif request.POST['type'] == "verticle":
            sub_modules = SpSubModules.objects.filter(status=1)
            for sub_module in sub_modules:
                sub_module_id = sub_module.id
                permission_id = request.POST['permission_id']

                module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpPermissionWorkflowRoles.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpUserRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpUserRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
        
        elif request.POST['type'] == "horizontal":
            permissions = SpPermissions.objects.all()
            for permission in permissions:
                permission_id = permission.id
                sub_module_id = request.POST['sub_module_id']

                module_id = getModelColumnById(SpSubModules,sub_module_id,'module_id')
                SpModulePermissions.objects.filter(module_id=module_id,sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpPermissionWorkflowRoles.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpUserRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()
                SpUserRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).delete()

        response['flag'] = True
        response['message'] = "Record updated Successfully"
        
    else:
        response['flag'] = False
        response['message'] = "Method not allowed."

    return JsonResponse(response)

