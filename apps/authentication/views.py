from django.http import HttpResponse
from utils import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from ..src.models import *
from uuid import uuid4
from django.core import serializers
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.auth.hashers import make_password

import sys
import os
sys.path.append(os.getcwd()+'/..')
from sales_port.decorators import unauthenticated_user
baseurl = settings.BASE_URL

@unauthenticated_user
def index(request):
    context = {'logo': getConfigurationResult('logo')}
    try:
            if request.POST:
                username = request.POST['username']
                password = request.POST['password']

                error_count = 0
                if username == '' and password == '':
                    messages.error(request, 'Please enter email id & password', extra_tags='invalid')
                    error_count = error_count+1
                    return redirect('login')
                if username == '':
                    messages.error(request, 'Please enter email id', extra_tags='invalid')
                    error_count = error_count+1
                if password == '':
                    messages.error(request, 'Please enter password', extra_tags='invalid')
                    error_count = error_count+1
                if(error_count > 0):
                    return redirect('login')
                else:
                    user = authenticate(username=username, password=password)
                    # return HttpResponse(user)
                    if user is not None:
                        login(request, user)
                        user_name = user.first_name +' '+ user.middle_name +' '+ user.last_name
                        if 'next' in request.POST:

                            # get user favourites
                            current_user = request.user
                            user_favorites = []
                            favorites = SpFavorites.objects.filter(user_id = current_user.id)
                            for favorite in favorites :
                                temp = {}
                                temp['favorite'] = favorite.favorite
                                temp['link'] = favorite.link
                                user_favorites.append(temp)

                            # get users modules
                            menus = []
                            if current_user.role_id == 0 :
                                modules = SpModules.objects.filter(status=1)
                            else:
                                modules = SpModules.objects.raw(''' select * from sp_modules where id in (select module_id from sp_user_role_permissions where user_id = %s) ''', [current_user.id])                                
                            
                            for module in modules : 
                                menu = {}
                                menu['menu'] = module.module_name
                                
                                if current_user.role_id == 0 :
                                    sub_modules = SpSubModules.objects.filter(module_id=module.id).exclude(link='')
                                else:
                                    sub_modules = SpSubModules.objects.raw(''' select * from sp_sub_modules where link != "" and module_id = %s and id in (select sub_module_id from sp_user_role_permissions where user_id = %s) ''', [module.id,current_user.id])
                                
                                submenus = []
                                for sub_module in sub_modules :
                                    sub_menu = {}
                                    sub_menu['sub_menu'] = sub_module.sub_module_name
                                    sub_menu['link'] = sub_module.link
                                    submenus.append(sub_menu)
                                menu['submenus'] = submenus
                                menus.append(menu)

                            request.session['modules'] = menus
                            request.session['favorites'] = user_favorites
                            messages.success(request, 'Hello '+user_name+', Welcome to Sales Port!', extra_tags='success')
                            return redirect(request.POST.get('next'))
                        else:
                            # get user favourites
                            current_user = request.user
                            user_favorites = []
                            favorites = SpFavorites.objects.filter(user_id = current_user.id)
                            for favorite in favorites :
                                temp = {}
                                temp['favorite'] = favorite.favorite
                                temp['link'] = favorite.link
                                user_favorites.append(temp)

                             # get users modules

                            menus = []
                            if current_user.role_id == 0 :
                                modules = SpModules.objects.filter(status=1)
                            else:
                                modules = SpModules.objects.raw(''' select * from sp_modules where id in (select module_id from sp_user_role_permissions where user_id = %s) ''', [current_user.id])                                
                            
                            for module in modules : 
                                menu = {}
                                menu['menu'] = module.module_name
                                if current_user.role_id == 0 :
                                    sub_modules = SpSubModules.objects.filter(module_id=module.id).exclude(link='')
                                else:
                                    sub_modules = SpSubModules.objects.raw(''' select * from sp_sub_modules where link != "" and module_id = %s and id in (select sub_module_id from sp_user_role_permissions where user_id = %s) ''', [module.id,current_user.id])                                
                                
                                submenus = []
                                for sub_module in sub_modules :
                                    sub_menu = {}
                                    sub_menu['sub_menu'] = sub_module.sub_module_name
                                    sub_menu['link'] = sub_module.link
                                    submenus.append(sub_menu)

                                
                                menu['submenus'] = submenus
                                menus.append(menu)

                            request.session['modules'] = menus
                            request.session['favorites'] = user_favorites
                            messages.success(request, 'Hello '+user_name+', Welcome to Sales Port!', extra_tags='success')
                            return redirect('/dashboard')
                    else:
                        messages.error(request, 'Invalid email id & password', extra_tags='invalid')
                        return redirect('login')
    except Exception as e:
        print(e)
    return render(request, 'authentication/login.html', context)

def forgotPassword(request):
    if request.method == "POST":
        if request.POST['email'] == "" or not isValidEmail(request.POST['email']):
            messages.error(request, 'Invalid email.', extra_tags='invalid')
            return redirect('/forgot-password')
        else:
            if SpUsers.objects.filter(official_email=request.POST['email']).exists():

                SpPasswordResets.objects.filter(email=request.POST['email']).delete()

                user = SpUsers.objects.get(official_email=request.POST['email'])
                user_name = user.first_name
                if user.middle_name is not None:
                    user_name += ' '+user.middle_name
                user_name += ' '+user.last_name

                auth_token = uuid4()
                password_reset = SpPasswordResets()
                password_reset.email = request.POST['email']
                password_reset.auth_token = auth_token
                password_reset.save()

                # send email.
                payload = {}
                payload['token'] = auth_token
                payload['link'] = baseurl+'/'+'reset-password/'+str(auth_token)
                msg_html = render_to_string('email-templates/forgot-password.html', payload)
                result = send_mail('Password reset','','noreply@sakhimilk.com',[request.POST['email']],html_message=msg_html)
            messages.success(request, 'If you are registered with us, a reset password link has been sent to your email.', extra_tags='success')
            return redirect('/forgot-password')
    else:
        context = {}
        return render(request, 'authentication/forgot-password.html', context)


def resetPassword(request,token):
    if request.method == "POST":
        if SpPasswordResets.objects.filter(email=request.POST['email'],auth_token=request.POST['token']).exists():

            password_reset = SpPasswordResets.objects.get(email=request.POST['email'],auth_token=request.POST['token'])
            user = SpUsers.objects.get(official_email=password_reset.email)
            user.password = make_password(request.POST['new_password'])
            user.save()
            
            # delete token
            SpPasswordResets.objects.filter(email=request.POST['email'],auth_token=request.POST['token']).delete()
    
            messages.success(request, 'Password reset successfully.', extra_tags='success')
            return redirect('/login')

        else:
            messages.error(request, 'Invalid or expired token', extra_tags='invalid')
            return redirect('/forgot-password')
    else:
        if SpPasswordResets.objects.filter(auth_token=token).exists():
            password_reset = SpPasswordResets.objects.get(auth_token=token)
            context = {}
            context['password_reset'] = password_reset
            return render(request, 'authentication/reset-password.html', context)
        else:
            messages.error(request, 'Invalid or expired token', extra_tags='invalid')
            return redirect('/forgot-password')

def logout_view(request):
    try:
        messages.success(request, 'You have successfully logout!', extra_tags='success')
        logout(request)
    except Exception as e:
        print(e)
    return redirect('login')

def handler404(request, exception):
    return render(request, 'authentication/404.html', status=404)     
   
