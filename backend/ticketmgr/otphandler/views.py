import services
from entityhandler.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def ticket_new(request):
    """Adds a reference to an ``Event`` with ``event_uuid`` to a ``TktUser``
    with ``user_uuid``.
    On success, sends a JSON response with the ticket-unique secret.
    JSON format: {'user_uuid': <str>, 'event_uuid': <str>}
    """
    if request.header == 'POST':
        try:
            user = TktUser.objects.get(uuid=request.data['user_uuid'])
        except:
            return Response({'error': 'User does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        
        try:
            event = Event.objects.get(uuid=request.data['event_uuid'])
        except:
            return Response({'error': 'Event does not exist.'},
                            status.HTTP_404_NOT_FOUND)

        if event.user_is_registered(user):
            return Response({'error': 'User already registered to event.'},
                            status.HTTP_409_CONFLICT)
        user.events.add(event)
        tkt_secret = services.generate_ticket_secret(user, event)
        return Response({'success': tkt_secret},
                        status.HTTP_200_OK)

@api_view(['POST'])
def ticket_auth(request):
    """Verifies a ticket-generated TOTP code given an ``Event`` and ``TktUser``.
    JSON format: {'user_uuid': <str>, 'event_uuid': <str>, 'ticket_totp': <str>}
    """
    if request.method == 'POST':
        try:
            user = TktUser.objects.get(uuid=request.data['user_uuid'])
        except:
            return Response({'error': 'User does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        
        try:
            event = Event.objects.get(uuid=request.data['event_uuid'])
        except:
            return Response({'error': 'Event does not exist.'},
                            status.HTTP_404_NOT_FOUND)
        
        try:
            totp = request.data['ticket_totp']
        except:
            return Response({'error': 'TOTP code was not supplied.'},
                            status.HTTP_400_BAD_REQUEST)

        if not event.user_is_registered(user):
            return Response({'error': 'User is not registered to event.'},
                            status.HTTP_400_BAD_REQUEST)
        tkt_secret = services.generate_ticket_secret(user, event)
        totp_authority = str(services.generate_totp(tkt_secret))
        if totp == totp_authority:
            return Response({'ticket_is_valid': True},
                            status.HTTP_200_OK)
        else:
            return Response({'ticket_is_valid': False},
                            status.HTTP_200_OK)
