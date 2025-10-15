from rest_framework import generics, permissions
from .models import GuestbookEntry
from .serializers import GuestbookEntrySerializer, UserSerializer

# --- View to LIST all guestbook entries ---
# This endpoint is public and can be accessed by anyone.
class GuestbookEntryList(generics.ListAPIView):
    queryset = GuestbookEntry.objects.all().order_by('-created_at')
    serializer_class = GuestbookEntrySerializer
    permission_classes = [permissions.AllowAny]


# --- View to CREATE a new guestbook entry ---
# This endpoint requires the user to be logged in.
class GuestbookEntryCreate(generics.CreateAPIView):
    queryset = GuestbookEntry.objects.all()
    serializer_class = GuestbookEntrySerializer
    permission_classes = [permissions.IsAuthenticated]

    # This method is called when a new entry is saved.
    # It automatically assigns the currently logged-in user to the entry.
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# --- View to GET the currently logged-in user's data ---
# This is the crucial endpoint for your Vue frontend to check login status.
# It requires authentication and uses the UserSerializer to include the GitHub avatar.
class CurrentUserView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    # This method returns the user object of the current request.
    def get_object(self):
        return self.request.user