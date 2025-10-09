from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from transformers import pipeline
import requests
import logging
from google import genai
import json

logger = logging.getLogger(__name__)

# --- This part of your code for image analysis remains the same ---
try:
    image_classifier = pipeline("image-classification", model="nateraw/food")
except Exception as e:
    image_classifier = None
    logger.error(f"Failed to load image classifier model: {e}")

def get_usda_nutrition(food_name: str):
    # (Your existing get_usda_nutrition function code goes here, unchanged)
    api_key = settings.USDA_API_KEY
    if not api_key:
        logger.warning("USDA_API_KEY not found in settings.")
        return {}
    try:
        search_params = {"query": food_name, "api_key": api_key, "pageSize": 1}
        search_response = requests.get("https://api.nal.usda.gov/fdc/v1/foods/search", params=search_params)
        search_response.raise_for_status()
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
            if num == "208": nutrients['calories'] = nutrient.get('amount', 0)
            elif num == "203": nutrients['proteins'] = nutrient.get('amount', 0)
            elif num == "204": nutrients['fats'] = nutrient.get('amount', 0)
            elif num == "205": nutrients['carbs'] = nutrient.get('amount', 0)
        return nutrients
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching USDA data for '{food_name}': {e}")
        return {}
    except (KeyError, IndexError) as e:
        logger.error(f"Error parsing USDA data for '{food_name}': {e}")
        return {}

class ImageAnalysisView(APIView):
    # (Your existing ImageAnalysisView code goes here, unchanged)
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
                "ingredient_breakdown": [{"ingredient": {"name": top_prediction}, "nutrients": nutrition_data, "cost": None}],
                "metadata": {"dish_name": top_prediction, "detected_items": [p['label'].replace("_", " ") for p in predictions[:3]]}
            }
            return Response({"analysis": analysis_response})
        except Exception as e:
            logger.error(f"An error occurred during image analysis: {e}")
            return Response({"error": f"An error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# --- CORRECTED DYNAMIC RECIPE VIEW ---
class GenerateRecipesView(APIView):
    def get(self, request, *args, **kwargs):
        category = request.query_params.get('category', 'popular global dishes')
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            logger.error("Gemini API key is not configured in .env file.")
            return Response({"error": "Gemini API key not configured."}, status=500)

        try:
            genai.configure(api_key=api_key)
            
            # Using the standard model name which will now work correctly
            model = genai.GenerativeModel('gemini-pro')

            prompt = f"""
            Generate a list of 12 diverse and authentic recipes for the theme: "{category}".
            For each recipe, provide: a unique id, a creative title, a short description (15-20 words), and a high-quality, royalty-free image URL from Unsplash or Pexels.
            Return the response as a valid JSON array only.
            """
            
            response = model.generate_content(prompt)
            
            cleaned_response = response.text.strip().lstrip("```json").rstrip("```")
            recipes_data = json.loads(cleaned_response)
            
            return Response(recipes_data)

        except Exception as e:
            logger.error(f"A critical Gemini API error occurred for category '{category}': {e}")
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)