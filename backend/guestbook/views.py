from rest_framework import generics, permissions
from .models import GuestbookEntry
from .serializers import GuestbookEntrySerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.response import Response

# This view allows anyone to see the guestbook entries.
class GuestbookEntryList(generics.ListAPIView):
    queryset = GuestbookEntry.objects.all().order_by('-created_at')
    serializer_class = GuestbookEntrySerializer
    permission_classes = [permissions.AllowAny]

# This view allows ONLY logged-in users to create a new entry.
class GuestbookEntryCreate(generics.CreateAPIView):
    queryset = GuestbookEntry.objects.all()
    serializer_class = GuestbookEntrySerializer
    permission_classes = [permissions.IsAuthenticated] # Requires user to be logged in

    # This method automatically assigns the logged-in user to the new entry.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# This new view will tell your frontend who is currently logged in.
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user