"""Module that contains Django Models representing events and users.
"""
import uuid
from django.db import models
from django.contrib.auth.models import User

class Event(models.Model):
    """Django Model that represents an event.

    Attributes:
        ``title``: A ``TextField`` that contains the event name.
        ``description``: A ``TextField`` that contains the event description.
        ``date``: A ``DateTimefield`` that contains the starting date and time of the event.
        ``uuid``: A ``UUIDField`` that contains the v4 UUID of the event.
    """
    title = models.TextField()
    description = models.TextField()
    datetime = models.DateTimeField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def user_is_registered(self, user: 'TktUser') -> bool:
        """Checks if a user is registered for an event.

        Args:
            ``user`` (``TktUser``): The user being checked for registration.

        Returns:
            ``bool``: ``True`` if user references this ``Event`` object.
            ``False`` otherwise.
        """
        # Effectively equivalent to TktUser.registered_to_event()
        # Django only caches forward lookups, so prefer whenever possible
        return user.events.filter(pk=self.pk).exists()

    def agent_is_registered(self, agent: 'TktAgent') -> bool:
        """Checks if an agent is assigned to an event.

        Args:
            ``agent`` (``TktAgent``): The agent being checked for assignment.

        Returns:
            ``bool``: ``True`` if agent references this ``Event`` object.
            ``False`` otherwise.
        """
        return agent.event.pk == self.pk

class TktUser(models.Model):
    """Django model that represents a typical user.
    A user cannot create, modify, and register for events.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)

    def registered_to_event(self, event: Event) -> bool:
        """Checks if an event contains a user in its roster.

        Args:
            ``event`` (``Event``): The event of which roster is being checked.

        Returns:
            ``bool``: ``True`` if this ``TktUser`` object references event.
            ``False`` otherwise.
        """
        return self.events.filter(pk=event.pk).exists()

class TktAdmin(models.Model):
    """Django model that represents event administrators.
    An admin can create, modify, and register users and agents for events.
    """
    admin = models.OneToOneField(User, on_delete=models.CASCADE)
    events = models.ManyToManyField(Event, blank=True)

class TktAgent(models.Model):
    # TODO: Consider allowing event to be blank on init but write-once
    """Django model that represents event agents.
    An agent can verify user tickets for events.
    """
    agent = models.OneToOneField(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=False)
