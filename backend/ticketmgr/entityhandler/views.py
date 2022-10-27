from django.http import JsonResponse
from django.shortcuts import render
from . import models

# Create your views here.
def user_signup(request):
    return JsonResponse({'user_signup': 'none'})

def user_info(request, username):
    return JsonResponse({'user_info': username})

def user_events(request, username):
    return JsonResponse({'user_events': username})

def event_new(request):
    return JsonResponse({'event_new': 'none'})

def event_info(request, event_id):
    return JsonResponse({'event_info': str(event_id)})

def event_query(request):
    return JsonResponse({'event_query': 'none'})

def event_users(request, event_id):
    return JsonResponse({'event_users': 'none'})

def event_agents(request, event_id):
    return JsonResponse({'event_agents': 'none'})

def event_admins(request, event_id):
    return JsonResponse({'event_admins': 'none'})
