import services
from entityhandler.models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['POST'])
def ticket_new(request):
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

    if request.header == 'POST':
        if event.user_is_registered(user):
            return Response({'error': 'User already registered to event.'},
                            status.HTTP_409_CONFLICT)
        user.events.add(event)
        tkt_secret = services.generate_ticket_secret(user, event)
        return Response({'success': tkt_secret},
                        status.HTTP_200_OK)

@api_view(['POST'])
def ticket_auth(request):
    return Response({'ticket_auth': 'none'})
