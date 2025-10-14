from rest_framework import serializers
from .models import GuestbookEntry
from allauth.socialaccount.models import SocialAccount

class UserSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar_url = serializers.URLField()

class GuestbookEntrySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = GuestbookEntry
        fields = ['id', 'user', 'message', 'created_at']

    def get_user(self, obj):
        try:
            social_account = SocialAccount.objects.get(user=obj.user, provider='github')
            return {
                'username': social_account.extra_data.get('login'),
                'avatar_url': social_account.extra_data.get('avatar_url')
            }
        except SocialAccount.DoesNotExist:
            return {'username': obj.user.username, 'avatar_url': ''}