# guestbook/urls.py

from django.urls import path
# 👇 ADD THIS LINE to import your views
from .views import GuestbookEntryList, GuestbookEntryCreate, CurrentUserView

urlpatterns = [
    # Path to list all entries (e.g., /api/guestbook/)
    path('', GuestbookEntryList.as_view(), name='guestbook_list'),

    # Path to create a new entry (e.g., /api/guestbook/create/)
    path('create/', GuestbookEntryCreate.as_view(), name='guestbook_create'),

    # Path to get the current user's data (e.g., /api/guestbook/user/)
    path('user/', CurrentUserView.as_view(), name='current_user'),
]