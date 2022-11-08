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
        user = serializer.save()
        tktuser = TktUser.objects.create(user=user)
        return Response(TktUserSerializer(tktuser).data,
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
    """First queries a ``TktUser`` with ``username``. Then on
    ``GET``: Returns a JSON representation of all ``Event`` objects referenced by
    the queried ``TktUser``.
    ``POST``: Adds a reference to an ``Event`` with ``event_uuid``
    to the queried ``TktUser``.
    JSON format: ``{'event_uuid': <str:uuid>}``
    """
    try:
        user = User.objects.get(username=username).tktuser
    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # TODO: Define separate serializers for list/detail view
        serializer = EventSerializer(list(user.events.all()), many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    elif request.method == 'POST':
        try:
            event = Event.objects.get(uuid=request.data['event_uuid'])
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        user.events.add(event)
        return Response(EventSerializer(event).data)

@api_view(['GET', 'POST'])
def event(request):
    """``GET``: Returns a JSON representation of all ``Event`` objects.
    ``POST``: Creates a new ``Event``.
    """
    if request.method == 'GET':
        serializer = EventSerializer(list(Event.objects.all()), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serial = EventSerializer(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status=status.HTTP_201_CREATED)
        return Response(serial.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def event_info(request, event_uuid):
    """Returns a JSON representation of an ``Event`` with ``event_uuid``.
    """
    if request.method == 'GET':
        try:
            event = EventSerializer(Event.objects.get(uuid=event_uuid))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(event.data, status.HTTP_200_OK)

@api_view(['GET', 'POST'])
def event_users(request, event_uuid):
    """``GET``: Returns a JSON representation of all ``TktUser``s that reference
    ``Event`` with ``event_uuid``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(uuid=event_uuid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        users = TktUserSerializer(event.tktuser_set.all(), many=True)
        return Response(users.data)

    elif request.methods == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET', 'POST'])
def event_agents(request, event_uuid):
    """``GET``: Returns a JSON representation of all ``TktAgent``s that reference
    ``Event`` with ``event_id``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(uuid=event_uuid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        agents = TktAgentSerializer(event.tktagent_set.all(), many=True)
        return Response(agents.data)

    elif request.method == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)

@api_view(['GET', 'POST'])
def event_admins(request, event_uuid):
    """``GET``: Returns a JSON representation of all ``TktAdmin``s that reference
    ``Event`` with ``event_id``.
    ``POST``: Adds a reference to ``Event`` if it exists.
    """
    if request.method == 'GET':
        try:
            event = Event.objects.get(uuid=event_uuid)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        admins = TktAdminSerializer(event.tktadmin_set.all(), many=True)
        return Response(admins.data)

    elif request.methods == 'POST':
        return Response(status=status.HTTP_501_NOT_IMPLEMENTED)
