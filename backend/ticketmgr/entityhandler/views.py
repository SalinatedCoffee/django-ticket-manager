from . import models
from .serializers import *
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def user_signup(request):
    return Response({'user_signup': 'none'})

@api_view(['GET'])
def user_info(request, username):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username).tktuser
            print(type(user))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serial = TktUserSerializer(user)
        return Response(serial.data)

@api_view(['GET', 'POST'])
def user_events(request, username):
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username).tktuser
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        events = EventSerializer(list(user.events.all()), many=True)
        return Response(events.data)
    elif request.method == 'POST':
        try:
            user = User.objects.get(username=username).tktuser
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            event = Event.objects.get(pk=request.data['ev_id'])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.events.add(event)
        return Response(EventSerializer(event).data)

@api_view(['GET', 'POST'])
def events(request):
    return Response({'event_new': 'none'})

@api_view(['GET'])
def event_info(request, event_id):
    return Response({'event_info': str(event_id)})

@api_view(['GET', 'POST'])
def event_users(request, event_id):
    return Response({'event_users': 'none'})

@api_view(['GET', 'POST'])
def event_agents(request, event_id):
    return Response({'event_agents': 'none'})

@api_view(['GET', 'POST'])
def event_admins(request, event_id):
    return Response({'event_admins': 'none'})
