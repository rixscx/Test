# backend/analyzer/urls.py

from django.urls import path
# Make sure to import the new view
from .views import ImageAnalysisView, GenerateRecipesView

urlpatterns = [
    path('analyze/', ImageAnalysisView.as_view(), name='analyze_image'),
    # Add this new URL pattern for the recipe generator
    path('recipes/', GenerateRecipesView.as_view(), name='generate_recipes'),
]