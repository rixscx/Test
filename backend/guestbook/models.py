from django.db import models
from django.contrib.auth.models import User

class GuestbookEntry(models.Model):
    # This creates a direct link to a registered user.
    # If a user is deleted, all their guestbook entries will also be deleted.
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This will make entries easier to read in the Django admin panel.
        return f'{self.user.username}: {self.message[:20]}'