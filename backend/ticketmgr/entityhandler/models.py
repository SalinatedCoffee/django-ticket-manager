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

    def user_is_registered(self, user: 'TktUser') -> bool:
        """Checks if a user is registered for an event.

        Args:
            user (TktUser): The user being checked for registration.

        Returns:
            bool: True if user references this Event object.
            False otherwise.
        """
        # Effectively equivalent to TktUser.registered_to_event()
        # Django only caches forward lookups, so prefer whenever possible
        return user.events.filter(pk=self.pk).exists()

    def agent_is_registered(self, agent: 'TktAgent') -> bool:
        """Checks if an agent is assigned to an event.

        Args:
            agent (TktAgent): The agent being checked for assignment.

        Returns:
            bool: True if agent references this Event object.
            False otherwise.
        """
        return agent.event.pk == self.pk

class TktUser(models.Model):
    """Django User that represents your typical user.
    A user cannot create, modify, and register for events.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)

    def registered_to_event(self, event: Event) -> bool:
        """Checks if an event contains a user in its roster.

        Args:
            event (Event): The event of which roster is being checked.

        Returns:
            bool: True if this TktUser object references event.
            False otherwise.
        """
        return self.events.filter(pk=event.pk).exists()

class TktAdmin(models.Model):
    """Django User that represents event administrators.
    An admin can create, modify, and register users and agents for events.
    """
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)

class TktAgent(models.Model):
    # TODO: check and enforce that an agent always gets assigned an event
    # upon init
    """Django User that represents event agents.
    An agent can verify user tickets for events.
    """
    agent = models.OneToOneField(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
