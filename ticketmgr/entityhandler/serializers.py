"""Django REST Framework serializers for ``entityhandler`` models.
"""
from .models import *
from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """DRF serializer for Django's ``User`` model.
    """
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

class TktUserSerializer(serializers.ModelSerializer):
    """DRF serializer for ``entityhandler.models.TktUser``.
    """
    user = UserSerializer(read_only=True)
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = TktUser
        fields = ['user', 'uuid', 'event_count']
        read_only_fields = ['user', 'uuid', 'event_count']
        depth = 1
    
    def get_event_count(self, obj):
        return obj.events.count()

class TktAdminSerializer(serializers.ModelSerializer):
    """DRF serializer for ``entityhandler.models.TktAdmin``.
    """
    admin = UserSerializer(read_only=True)
    event_count = serializers.SerializerMethodField()

    class Meta:
        model = TktAdmin
        fields = ['admin', 'event_count']
        read_only_fields = ['admin', 'event_count']
        depth = 1

    def get_event_count(self, obj):
        return obj.events.count()

class TktAgentSerializer(serializers.ModelSerializer):
    """DRF serializer for ``entityhandler.models.TktAgent``.
    """
    agent = UserSerializer()

    class Meta:
        model = TktAgent
        fields = ['agent']
        read_only_fields = ['agent']
        depth = 1

class EventSerializer(serializers.ModelSerializer):
    """DRF serializer for ``entityhandler.models.Event``.
    """
    class Meta:
        model = Event
        fields = ['title', 'description', 'datetime', 'uuid']
        read_only_fields = ['uuid']
