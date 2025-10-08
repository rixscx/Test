from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from transformers import pipeline, T5ForConditionalGeneration, T5Tokenizer
import requests
import logging

# It is recommended to set up a logger in your project
logger = logging.getLogger(__name__)

try:
    image_classifier = pipeline("image-classification", model="nateraw/food")
except Exception as e:
    image_classifier = None
    logger.error(f"Failed to load image classifier model: {e}")

def get_usda_nutrition(food_name: str):
    """
    Fetches nutritional data for a given food from the USDA API.
    """
    api_key = settings.USDA_API_KEY
    if not api_key:
        logger.warning("USDA_API_KEY not found in settings.")
        return {}
    try:
        search_params = {"query": food_name, "api_key": api_key, "pageSize": 1}
        search_response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=search_params)
        search_response.raise_for_status()  # Raise an exception for bad status codes
        search_data = search_response.json()

        if not search_data.get('foods'):
            logger.info(f"No food found for '{food_name}' in USDA database.")
            return {}

        fdc_id = search_data['foods'][0]['fdcId']

        details_url = f"https://api.nal.usda.gov/fdc/v1/food/{fdc_id}"
        details_response = requests.get(details_url, params={"api_key": api_key})
        details_response.raise_for_status()
        details_data = details_response.json()

        nutrients = {"calories": 0, "proteins": 0, "fats": 0, "carbs": 0}
        for nutrient in details_data.get('foodNutrients', []):
            num = nutrient.get("nutrient", {}).get("number")
            if num == "208":
                nutrients['calories'] = nutrient.get('amount', 0)
            elif num == "203":
                nutrients['proteins'] = nutrient.get('amount', 0)
            elif num == "204":
                nutrients['fats'] = nutrient.get('amount', 0)
            elif num == "205":
                nutrients['carbs'] = nutrient.get('amount', 0)
        return nutrients
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching USDA data for '{food_name}': {e}")
        return {}
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing USDA data for '{food_name}': {e}")
        return {}

class ImageAnalysisView(APIView):
    def post(self, request, *args, **kwargs):
        image_file = request.FILES.get('image')
        if not image_file:
            return Response({"error": "No image file provided"}, status=status.HTTP_400_BAD_REQUEST)

        if not image_classifier:
            return Response({"error": "AI model is not available."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            image = Image.open(image_file).convert("RGB")
            predictions = image_classifier(image)
            if not predictions:
                return Response({"error": "Could not classify the image."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            top_prediction = predictions[0]['label'].replace("_", " ").title()
            
            nutrition_data = get_usda_nutrition(top_prediction)

            analysis_response = {
                "total_profile": nutrition_data,
                "ingredient_breakdown": [{
                    "ingredient": {"name": top_prediction},
                    "nutrients": nutrition_data,
                    "cost": None
                }],
                "metadata": {
                    "dish_name": top_prediction,
                    "detected_items": [p['label'].replace("_", " ") for p in predictions[:3]],
                }
            }
            return Response({"analysis": analysis_response})
        except Exception as e:
            logger.error(f"An error occurred during image analysis: {e}")
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)