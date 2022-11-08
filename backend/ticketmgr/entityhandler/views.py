from .serializers import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def user_signup(request):
    """Creates a new ``User`` which is then linked to a new ``TktUser``.
    """
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user_raw = serializer.save()
        tktuser_raw = TktUser.objects.create(user=user_raw)

        return Response(TktUserSerializer(tktuser_raw).data,
                        status.HTTP_201_CREATED)

    return Response(serializer.errors, status.HTTP_409_CONFLICT)

@api_view(['GET'])
def user_info(request, username):
    """Returns a JSON representation of a ``TktUser`` with ``username``.
    """
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username).tktuser
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = TktUserSerializer(user)

        return Response(serializer.data, status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def user_events(request, username):
    """``GET``: Returns a JSON representation of all ``Event`` objects referenced by
    a ``TktUser`` with ``username``.
    ``POST``: Adds a reference to an ``Event`` if it exists.
    """
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
    """``GET``: Returns a JSON representation of all ``Event`` objects.
    ``POST``: Creates a new ``Event``.
    """
    if request.method == 'GET':
        events = EventSerializer(list(Event.objects.all()), many=True)
        return Response(events.data)
    elif request.method == 'POST':
        serial = EventSerializer(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def event_info(request, event_id):
    """Returns a JSON representation of an ``Event`` with ``event_id``.
    """
    if request.method == 'GET':
        try:
            event = EventSerializer(Event.objects.get(pk=event_id))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(event.data)

@api_view(['GET', 'POST'])
def event_users(request, event_id):
    """``GET``: Returns a JSON representation of all ``TktUser``s that reference
    ``Event`` with ``event_id``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(pk=event_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        users = TktUserSerializer(event.tktuser_set.all(), many=True)
        return Response(users.data)
    elif request.methods == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET', 'POST'])
def event_agents(request, event_id):
    """``GET``: Returns a JSON representation of all ``TktAgent``s that reference
    ``Event`` with ``event_id``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(pk=event_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        agents = TktAgentSerializer(event.tktagent_set.all(), many=True)
        return Response(agents.data)
    elif request.method == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET', 'POST'])
def event_admins(request, event_id):
    """``GET``: Returns a JSON representation of all ``TktAdmin``s that reference
    ``Event`` with ``event_id``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(pk=event_id)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        admins = TktAdminSerializer(event.tktadmin_set.all(), many=True)
        return Response(admins.data)
    elif request.methods == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
