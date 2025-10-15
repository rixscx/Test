from rest_framework import serializers
from .models import GuestbookEntry
from django.contrib.auth.models import User

# This serializer will be used to get the current user's information.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

# This serializer handles the guestbook entries.
class GuestbookEntrySerializer(serializers.ModelSerializer):
    # This will display the user's username as a string.
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GuestbookEntry
        # The 'user' is handled automatically by the view, so it's read-only here.
        fields = ['id', 'user', 'message', 'created_at']