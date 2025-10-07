import os
import joblib
import logging
import pandas as pd
import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from sklearn.pipeline import Pipeline
from transformers import AutoTokenizer, AutoModel
import torch

# --- Setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "nutrition_model_pipeline.pkl"

# --- Load Locally Trained Pipeline ---
try:
    pipeline: Pipeline = joblib.load(MODEL_PATH)
    logging.info(f"✅ Loaded trained model pipeline from {MODEL_PATH}")
except FileNotFoundError:
    logging.error(f"Model not found at {MODEL_PATH}. Please run train_model.py first.")
    raise

# --- Local Embedding Model (no API required) ---
HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
logging.info(f"📦 Loading local transformer model: {HF_MODEL_ID}")

tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID)
model = AutoModel.from_pretrained(HF_MODEL_ID)

def get_text_embedding(text: str) -> np.ndarray:
    """Generate a sentence embedding from a food description."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
    return embedding

# --- Simple Local Nutrient Estimator ---
def estimate_nutrients_from_embedding(embedding: np.ndarray) -> dict:
    """
    Convert text embeddings into rough nutrient estimates.
    This uses a deterministic mapping to simulate nutrient estimation.
    """
    # Normalize the embedding
    embedding = (embedding - embedding.min()) / (embedding.max() - embedding.min() + 1e-8)
    mean_val = np.mean(embedding)

    return {
        "protein": round(10 + 15 * mean_val, 2),
        "fat": round(5 + 10 * (1 - mean_val), 2),
        "carbohydrates": round(20 + 30 * mean_val, 2),
        "fiber": round(2 + 5 * mean_val, 2),
        "sugar": round(3 + 7 * (1 - mean_val), 2),
        "sodium": round(0.3 + 0.5 * mean_val, 2),  # grams
    }

# --- Hybrid Prediction ---
def hybrid_predict(food_description: str):
    logging.info(f"--- Starting Local Hybrid Prediction for: '{food_description}' ---")

    # Step 1: Generate text embedding
    embedding = get_text_embedding(food_description)

    # Step 2: Convert embedding → nutrient estimates
    nutrient_estimates = estimate_nutrients_from_embedding(embedding)
    logging.info(f"🔍 Estimated Nutrients: {nutrient_estimates}")

    # Step 3: Predict calories using trained pipeline
    input_df = pd.DataFrame([nutrient_estimates])
    predicted_calories = pipeline.predict(input_df)[0]

    logging.info(f"✅ Final Predicted Calories: {predicted_calories:.2f}")

    return {
        "description": food_description,
        "estimated_nutrients": nutrient_estimates,
        "predicted_calories": float(f"{predicted_calories:.2f}")
    }

# --- Example Run ---
if __name__ == "__main__":
    example_food = "A hearty bowl of chicken and vegetable soup with whole grain bread on the side"
    result = hybrid_predict(example_food)
    
    if result:
        print("\n" + "="*30)
        print("    Local Hybrid Prediction Result")
        print("="*30)
        print(f"Description: {result['description']}")
        print("\n--- Estimated Nutrients (Step 1) ---")
        for nutrient, value in result['estimated_nutrients'].items():
            print(f"  - {nutrient.capitalize()}: {value} g")

        print("\n--- Final Calorie Prediction (Step 2) ---")
        print(f"  🔥 Predicted Calories: {result['predicted_calories']}")
        print("="*30)
