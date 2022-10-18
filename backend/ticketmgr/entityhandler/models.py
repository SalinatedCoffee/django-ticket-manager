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

class TktEntity(User):
    """Django User used as a base class for entities.
    """
    class Meta: # pylint: disable=missing-class-docstring, too-few-public-methods
        abstract = True

class TktUser(TktEntity):
    """Django User that represents your typical user.
    A user cannot create, modify, and register for events.
    """
    events = models.ManyToManyField(Event)

class TktAdmin(TktEntity):
    """Django User that represents event administrators.
    An admin can create, modify, and register users and agents for events.
    """
    events = models.ManyToManyField(Event)

class TktAgent(TktEntity):
    """Django User that represents event agents.
    An agent can verify user tickets for events.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
