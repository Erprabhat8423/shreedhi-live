import sys
import os
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from ..models import *
from utils import *

def has_par(sub_module_id,permission):
    def has_perm(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.role_id > 0:

                # get current url
                # url_name = request.resolver_match.url_name
                # namespaces = request.resolver_match.namespaces[0]
                # namespaces = namespaces.replace("'","")
                # link = namespaces+":"+url_name

                is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

                if(is_ajax):
                    is_allowed = 1
                    role_permission = SpUserRolePermissions.objects.filter(user_id=request.user.id,role_id=request.user.role_id,sub_module_id=sub_module_id,permission_slug=permission).exists()
                    if not role_permission:
                        is_allowed = 0
                        
                    if is_allowed == 0 :
                        response = {}
                        response['flag'] = False
                        response['message'] = "You are not authorized for this action. Please contact system administrator.."
                        return JsonResponse(response)
                    else:
                        return view_func(request, *args, **kwargs)
                    
                else:
                    is_allowed = 1
                    role_permission = SpUserRolePermissions.objects.filter(user_id=request.user.id,role_id=request.user.role_id,sub_module_id=sub_module_id,permission_slug=permission).exists()
                    if not role_permission:
                        is_allowed = 0
                    
                    if is_allowed == 0 :
                        context = {}
                        context['message'] = "You are not authorized for this action. Please contact system administrator."
                        return render(request, 'errors/permission-denied.html',context)
                    else:
                        return view_func(request, *args, **kwargs)
            else:
                return view_func(request, *args, **kwargs)
        return wrapper_func
    return has_perm
  