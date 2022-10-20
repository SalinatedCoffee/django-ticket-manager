# TODO: Revisit user models later, current implmentation of TktAgent is messy
"""Module that contains Django Models representing events and users.
"""

from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    """Djando Model that represents an event.

    Attributes:
        ev_title: A TextField() that contains the event name.
        ev_description: A TextField() that contains the event description.
        ev_date: A DateTimefield() that contains the starting date and time of the event.
        ev_hash: A CharField() that contains a 128bit hash unique to the event.
    """
    ev_title = models.TextField()
    ev_description = models.TextField()
    ev_datetime = models.DateTimeField()
    ev_hash = models.CharField(max_length = 16)

class TktUser(User):
    """Django User that represents your typical user.
    A user cannot create, modify, and register for events.
    """
    events = models.ManyToManyField(Event)

class TktAdmin(User):
    """Django User that represents event administrators.
    An admin can create, modify, and register users and agents for events.
    """
    events = models.ManyToManyField(Event)

class TktAgent(models.Model):
    """Django User that represents event agents.
    An agent can verify user tickets for events.
    """
    agent = models.OneToOneField(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
