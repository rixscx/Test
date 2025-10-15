from django.urls import path
from .views import CurrentUserView

urlpatterns = [
    # GET requests to /api/user/ will go to this new view.
    path('', CurrentUserView.as_view(), name='current-user'),
]