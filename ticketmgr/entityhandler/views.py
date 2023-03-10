# TODO: Consider catching multiple exceptions and returning appropriate
#       HTTP response codes
# TODO: Check disclosed information through serialized models with nested relationships
#       (do endpoints accidentally show other user info to user through event endpoints, etc)
# TODO: Support DELETE methods for appropriate endpoints (unregister entities from events, etc)
# TODO: Pagination for user/event list requests
from .serializers import *
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@api_view()
def csrf(request):
  return Response({'csrfToken': get_token(request)})

@api_view(['POST'])
@csrf_protect
def tkt_login(request):
    """Logs in a Tkt-entity and sets a session cookie upon success.
    JSON format: ``{'username': <str>, 'password': <str>}``
    """
    username = request.data.get('username')
    password = request.data.get('password')

    if username is None or password is None:
        return Response({'error': 'Malformed payload.'}, status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'User with given credentials does not exist.'},
                        status.HTTP_400_BAD_REQUEST)

    login(request, user)
    if hasattr(user, 'tktuser'):
        serializer = TktUserSerializer(user.tktuser)
    elif hasattr(user, 'tktagent'):
        serializer = TktAgentSerializer(user.tktagent)
    elif hasattr(user, 'tktadmin'):
        serializer = TktAdminSerializer(user.tktadmin)
    elif user.is_superuser:
        return Response({'message': 'Logged in as superuser.'})
    else:
        return Response({'error': 'Failed to resolve user type.'},
                        status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(serializer.data, status.HTTP_200_OK)

@api_view(['GET'])
@csrf_protect
def tkt_logout(request):
    logout(request)
    return Response(status=status.HTTP_200_OK)

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
    return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request, username):
    """Returns a JSON representation of a ``TktUser`` with ``username``.
    """
    if request.method == 'GET':
        try:
            user = User.objects.get(username=username).tktuser
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # All admins and agents can access user info
        # Users can only access own info
        # TODO: Consider adding event enrollment checks so admins and agents
        #       can only access users registered to assigned events
        if not request.user.is_superuser and hasattr(request.user, 'tktuser'):
            if request.user.tktuser.uuid != user.uuid:
                return Response(status=status.HTTP_403_FORBIDDEN)
        
        serializer = TktUserSerializer(user)
        return Response(serializer.data, status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_events(request, username):
    """Queries a ``TktUser`` with ``username``, then returns a JSON response
    containing all ``Event`` objects referenced by the queried ``TktUser``.
    """
    try:
        user = User.objects.get(username=username).tktuser
    except:
        return Response({'error': 'User does not exist.'},
                        status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # TODO: Consider defining separate serializers for list/detail view
        serializer = EventSerializer(list(user.events.all()), many=True)
        return Response(serializer.data, status.HTTP_200_OK)
    
    """
    elif request.method == 'POST':
        # TODO: Admins should only be able to register users to events that
        #       it is responsible for
        if not request.user.is_superuser and not hasattr(request.user, 'tktadmin'):
            return Response({'error': 'Only admin accounts can enroll users to events.'},
                            status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(uuid=request.data['event_uuid'])
        except:
            return Response({'error': 'Event does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        user.events.add(event)
        return Response(EventSerializer(event).data, status.HTTP_200_OK)
    """

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event(request):
    """``GET``: Returns a JSON representation of all ``Event`` objects.
    ``POST``: Creates a new ``Event``.
    """
    if request.method == 'GET':
        serializer = EventSerializer(list(Event.objects.all()), many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_superuser and not hasattr(request.user, 'tktadmin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        serial = EventSerializer(data=request.data)
        if serial.is_valid():
            serial.save()
            return Response(serial.data, status.HTTP_201_CREATED)
        return Response(serial.errors, status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def event_users(request, event_uuid):
    """First queries an ``Event`` with ``event_uuid``. Then on
    ``GET``: Returns a JSON representation of all ``TktUser``s that reference
    the queried ``Event``.
    ``POST``: Adds a reference to the queried ``Event`` to a ``TktUser`` with
    ``user_uuid``.
    JSON format: ``{'user_uuid': <str>}``
    """
    try:
        event = Event.objects.get(uuid=event_uuid)
    except:
        return Response({'error': 'Event does not exist.'},
                        status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if not request.user.is_superuser and hasattr(request.user, 'tktuser'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        users = TktUserSerializer(event.tktuser_set.all(), many=True)
        return Response(users.data)

    elif request.method == 'POST':
        if not request.user.is_superuser and not hasattr(request.user, 'tktadmin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            user = TktUser.objects.get(uuid=request.data['user_uuid'])
        except:
            return Response({'error': 'User does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        user.events.add(event)
        return Response(TktUserSerializer(user).data, status.HTTP_200_OK)
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def event_agents(request, event_uuid):
    """Returns a JSON representation of all ``TktAgent``s that reference
    an ``Event`` with ``event_uuid``.
    """
    if request.method == 'GET':
        if not request.user.is_superuser and not hasattr(request.user, 'tktadmin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            event = Event.objects.get(uuid=event_uuid)
        except:
            return Response({'error': 'Event does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        agents = TktAgentSerializer(event.tktagent_set.all(), many=True)
        return Response(agents.data, status.HTTP_200_OK)

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def event_admins(request, event_uuid):
    """First queries an ``Event`` with ``event_uuid``. Then on
    ``GET``: Returns a JSON representation of all ``TktAdmin``s that reference
    the queried ``Event``.
    ``POST``: Adds a reference to the queried ``Event`` to a ``TktAdmin`` with
    ``admin_username``.
    JSON format: ``{'admin_username': <str>}``
    """
    try:
        event = Event.objects.get(uuid=event_uuid)
    except:
        return Response({'error': 'Event does not exist.'},
                        status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        if not request.user.is_superuser and hasattr(request.user, 'tktuser'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        admins = TktAdminSerializer(event.tktadmin_set.all(), many=True)
        return Response(admins.data, status.HTTP_200_OK)

    elif request.method == 'POST':
        if not request.user.is_superuser and not hasattr(request.user, 'tktadmin'):
            return Response(status=status.HTTP_403_FORBIDDEN)
        try:
            admin = User.objects.get(username=request.data['admin_username']).tktadmin
        except:
            return Response({'error': 'Admin does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        admin.events.add(event)
        return Response(TktAdminSerializer(admin).data, status.HTTP_200_OK)
