from rest_framework import serializers
from .models import GuestbookEntry
from django.contrib.auth.models import User
from allauth.socialaccount.models import SocialAccount # <--- IMPORT THIS

# This serializer will be used to get the current user's information.
class UserSerializer(serializers.ModelSerializer):
    # This custom field will hold the URL for the user's GitHub avatar.
    avatar_url = serializers.SerializerMethodField() # <--- ADD THIS LINE

    class Meta:
        model = User
        # Add 'avatar_url' to the list of fields to be sent in the API response.
        fields = ['id', 'username', 'avatar_url'] # <--- UPDATE THIS LINE

    # This function tells the serializer how to get the value for 'avatar_url'.
    def get_avatar_url(self, obj): # <--- ADD THIS ENTIRE FUNCTION
        try:
            # Look up the social account linked to this user from the 'github' provider.
            social_account = SocialAccount.objects.get(user=obj, provider='github')
            return social_account.get_avatar_url()
        except SocialAccount.DoesNotExist:
            # If the user isn't logged in via GitHub, return nothing for the avatar.
            return None

# This serializer handles the guestbook entries.
class GuestbookEntrySerializer(serializers.ModelSerializer):
    # This will display the user's username as a string.
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = GuestbookEntry
        # The 'user' is handled automatically by the view, so it's read-only here.
        fields = ['id', 'user', 'message', 'created_at']