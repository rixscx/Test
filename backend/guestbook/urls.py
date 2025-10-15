from django.urls import path
from .views import GuestbookEntryList, GuestbookEntryCreate

urlpatterns = [
    # GET requests to /api/guestbook/ will go to the list view.
    path('', GuestbookEntryList.as_view(), name='guestbook-list'),
    # POST requests to /api/guestbook/ will go to the create view.
    path('', GuestbookEntryCreate.as_view(), name='guestbook-create'),
]