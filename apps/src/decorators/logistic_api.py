import sys
import os
from django.http import HttpResponse,JsonResponse
from django.shortcuts import render,redirect
from ..models import *
from utils import *

def validate_logistic_api(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if 'Authorization' in request.headers and request.headers['Authorization'] != "" :
            api_token = request.headers['Authorization']
            if SpVehicles.objects.filter(api_token=api_token).exists() :
                return view_func(request, *args, **kwargs)
            else:
                response['message'] = "Invalid Authorization token"
                
                return JsonResponse(response,status=401)
        else:
            response['message'] = "Authorization token is missing"
            return JsonResponse(response,status=404)

    return wrapper_func

def validatePOST(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if  request.method == "POST" :
            return view_func(request, *args, **kwargs)
        else:
            response['message'] = "Method Not Allowed"
            return JsonResponse(response,status=405)

    return wrapper_func
  
def validateGET(view_func):
    def wrapper_func(request, *args, **kwargs):
        response = {}
        if  request.method == "GET" :
            return view_func(request, *args, **kwargs)
        else:
            response['message'] = "Method Not Allowed"
            return JsonResponse(response,status=405)

    return wrapper_func