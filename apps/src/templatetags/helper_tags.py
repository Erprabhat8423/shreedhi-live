from django import template
from ...src.models import *
from datetime import datetime, timezone, date
from datetime import timedelta
from django.utils.encoding import force_text
from django.utils.translation import ungettext, ugettext as _
import math 

register = template.Library()
MOMENT = 60

@register.simple_tag
def checkedFavorite(favorite,link):
    if SpFavorites.objects.filter(favorite=favorite,link=link).exists() :
        return "checked"
    else: 
        return ""

@register.simple_tag
def get_workflow(role_id,sub_module_id,permission_id):
    if SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).exists():
        role_permission = SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).first()
        return role_permission.workflow
    else:
        return False

    

@register.simple_tag
def check_role_permission(role_id,sub_module_id,permission_id):
    if SpRolePermissions.objects.filter(role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists() :
        return True
    elif SpRoleWorkflowPermissions.objects.filter(workflow_level_role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists() :
        return True
    else:
        return False

@register.simple_tag
def get_workflow_count(role_id,sub_module_id,permission_id):
    if SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).exists():
        first_role = SpRolePermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).first()
        role_permission_workflow = SpRoleWorkflowPermissions.objects.filter(role_id=first_role.role_id,sub_module_id=sub_module_id,permission_id=permission_id).count()
    else:
        role_permission_workflow = SpRoleWorkflowPermissions.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).count()
    return role_permission_workflow


@register.simple_tag
def get_user_role_workflow(user_id,role_id,sub_module_id,permission_id):
    
    if SpUserRolePermissions.objects.filter(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists() :
        if SpUserModulePermissions.objects.filter(user_id=user_id,sub_module_id=sub_module_id,permission_id=permission_id).exists():
            module_permission = SpUserModulePermissions.objects.get(user_id=user_id,sub_module_id=sub_module_id,permission_id=permission_id)
            if module_permission.workflow:
                return module_permission.workflow
            else:
                return ""
        else:
            try:
                module_permission = SpModulePermissions.objects.get(sub_module_id=sub_module_id,permission_id=permission_id)
            except SpModulePermissions.DoesNotExist:
                module_permission = None
            if module_permission:    
                module_permission = SpModulePermissions.objects.get(sub_module_id=sub_module_id,permission_id=permission_id)
                if module_permission.workflow:
                    return module_permission.workflow
                else:
                    return ""
            else:
                return ""
    else:
         return ""


@register.simple_tag
def get_user_role_workflow_count(user_id,role_id,sub_module_id,permission_id):
    if SpUserRoleWorkflowPermissions.objects.filter(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists():
        user_role_permission_workflow = SpPermissionWorkflows.objects.filter(sub_module_id=sub_module_id,permission_id=permission_id).count()
        return user_role_permission_workflow  
    else:
        return 0

@register.simple_tag
def get_user_role_from_date(user_id,role_id,sub_module_id,permission_id):
    
    if SpUserRolePermissions.objects.filter(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists() :
        from_date = SpUserRolePermissions.objects.get(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id)
        if from_date.from_date:
            return datetime.strptime(str(from_date.from_date), '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            return ""    
    else:
         return ""        

@register.simple_tag
def get_user_role_to_date(user_id,role_id,sub_module_id,permission_id):
    
    if SpUserRolePermissions.objects.filter(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id).exists() :
        to_date = SpUserRolePermissions.objects.get(user_id=user_id,role_id=role_id,sub_module_id=sub_module_id,permission_id=permission_id)
        if to_date.to_date:
            return datetime.strptime(str(to_date.to_date), '%Y-%m-%d').strftime('%d/%m/%Y')
        else:
            return ""    
    else:
         return ""


@register.simple_tag
def sum(num1, num2):
    return round((num1 + num2),2)

@register.simple_tag
def subtract(value, arg):
    return round((value - arg),2)

def date_diff_in_seconds(dt2, dt1):
  timedelta = dt2 - dt1
  return timedelta.days * 24 * 3600 + timedelta.seconds

@register.filter
def natural_timesince(value):
    if isinstance(value, datetime):  
        value = value.replace(tzinfo=None)
        seconds = date_diff_in_seconds(datetime.now(), value)

        months = math.floor(seconds / (3600 * 24 * 30))
        day = math.floor(seconds / (3600 * 24))
        hours = math.floor(seconds / 3600)
        mins = math.floor((seconds - (hours * 3600)) / 60)
        secs = math.floor(seconds % 60)

        if seconds < 60:
            time = str(secs) + " sec ago"
        elif seconds < 60 * 60:
            time = str(mins)+" min "+str(secs)+" sec ago"
        elif seconds < 24 * 60 * 60:
            time = str(hours) + " hrs "+str(mins)+" min ago"
        elif seconds < 24 * 60 * 60 * 30:
            time = str(day) + " day ago"
        else:
            time = str(months) + " month ago"
        return time

@register.filter
def index(indexable, i):
    return indexable[i]

@register.simple_tag
def get_ho_report_quantity(user_id,product_variant_id):
    if SpHoReport.objects.filter(user_id=user_id,product_variant_id=product_variant_id).exists() :
        ho_report = SpHoReport.objects.get(user_id=user_id,product_variant_id=product_variant_id)
        return ho_report.quantity
    else:
        return 0

@register.simple_tag
def get_ho_report_foc(product_variant_id):
    if SpHoReport.objects.filter(user_id__isnull=True, product_variant_id=product_variant_id).exists() :
        ho_report = SpHoReport.objects.get(user_id__isnull=True, product_variant_id=product_variant_id)
        return ho_report.foc_pouch
    else:
        return 0
    
