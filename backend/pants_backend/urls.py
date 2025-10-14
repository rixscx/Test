from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/analyze/', include('analyzer.urls')),
    path('api/recipes/', include('analyzer.urls')),
    path('api/guestbook/', include('guestbook.urls')),
    path('accounts/', include('allauth.urls')), # Add this for allauth login routes
    # Add a new endpoint to get current user info
    path('api/user/', include('guestbook.user_urls')), 
]