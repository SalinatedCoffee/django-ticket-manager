from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
def ticket_new(response):
    return JsonResponse({'ticket_new': 'none'})

def ticket_auth(response):
    return JsonResponse({'ticket_auth': 'none'})
