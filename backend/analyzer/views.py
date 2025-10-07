from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from transformers import pipeline
import requests

try:
    image_classifier = pipeline("image-classification", model="nateraw/food")
except Exception:
    image_classifier = None

def get_usda_nutrition(food_name: str):
    api_key = settings.USDA_API_KEY
    if not api_key: return {}
    try:
        search_params = {"query": food_name, "api_key": api_key, "pageSize": 1}
        search_response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=search_params)
        search_data = search_response.json()
        if not search_data.get('foods'): return {}
        fdc_id = search_data['foods'][0]['fdcId']

        details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
        details_response = requests.get(details_url, params={"api_key": api_key})
        details_data = details_response.json()

        nutrients = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
        for nutrient in details_data.get('foodNutrients', []):
            num = nutrient.get("nutrient", {}).get("number")
            if num == "208": nutrients['calories'] = nutrient.get('amount', 0)
            elif num == "203": nutrients['proteins'] = nutrient.get('amount', 0)
            elif num == "204": nutrients['fats'] = nutrient.get('amount', 0)
            elif num == "205": nutrients['carbs'] = nutrient.get('amount', 0)
        return nutrients
    except Exception:
        return {}

class ImageAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file: return Response({"error": "No image file provided"}, status=400)
        if not image_classifier: return Response({"error": "AI model is not available."}, status=500)

        try:
            image = Image.open(image_file).convert("RGB")
            predictions = image_classifier(image)
            top_prediction = predictions[0]['label'].replace("_", " ").title() if predictions else "Unknown"
            
            nutrition_data = get_usda_nutrition(top_prediction)

            analysis_response = {
                "total_profile": nutrition_data,
                "ingredient_breakdown": [{"ingredient": {"name": top_prediction}, "nutrients": nutrition_data, "cost": None}],
                "metadata": {
                    "dish_name": top_prediction,
                    "detected_items": [p['label'].replace("_", " ") for p in predictions[:3]],
                }
            }
            return Response({"analysis": analysis_response})
        except Exception as e:
            return Response({"error": f"An error occurred: {e}"}, status=500)