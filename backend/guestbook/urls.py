from django.urls import path
from .views import GuestbookEntryListCreate

urlpatterns = [
    path('', GuestbookEntryListCreate.as_view(), name='guestbook-list-create'),
]