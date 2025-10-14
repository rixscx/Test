from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import GuestbookEntry
from .serializers import GuestbookEntrySerializer
from allauth.socialaccount.models import SocialAccount

class GuestbookEntryListCreate(generics.ListCreateAPIView):
    queryset = GuestbookEntry.objects.all()
    serializer_class = GuestbookEntrySerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class CurrentUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            social_account = SocialAccount.objects.get(user=request.user, provider='github')
            data = {
                'username': social_account.extra_data.get('login'),
                'avatar_url': social_account.extra_data.get('avatar_url')
            }
            return Response(data)
        except SocialAccount.DoesNotExist:
            return Response({'error': 'Not logged in with GitHub'}, status=status.HTTP_404_NOT_FOUND)