import logging
import joblib
import pandas as pd
from typing import Tuple # <-- Import Tuple
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator
from pathlib import Path

# --- Setup ---
# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Configuration ---
BASE_DIR = Path(__file__).resolve().parent
# Correctly locate the data file in the parent directory of the script's location
DATA_FILE = BASE_DIR / "usda_nutrition_dataset.csv" 
MODEL_FILE = BASE_DIR / "nutrition_model_pipeline.pkl"

# Model configuration
TARGET_COLUMN = "calories"
FEATURE_COLUMNS = ["protein", "fat", "carbohydrates", "fiber", "sugar", "sodium"]


# --- Data Loading and Preparation ---
def load_dataset():
    """Loads the dataset from the specified CSV file."""
    if not DATA_FILE.exists():
        logging.error(f"Dataset not found at {DATA_FILE}. It should be in the same directory as the script.")
        raise FileNotFoundError(f"Dataset not found at {DATA_FILE}.")
    df = pd.read_csv(DATA_FILE)
    logging.info(f"📂 Loaded dataset with {len(df)} rows and {len(df.columns)} columns.")
    return df

def prepare_data(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]: # <-- CORRECTED TUPLE SYNTAX
    """Cleans data and separates features and target."""
    df = df.dropna(subset=[TARGET_COLUMN] + ["protein", "fat", "carbohydrates"])
    df = df[(df[TARGET_COLUMN] > 0) & (df["protein"] >= 0) & (df["fat"] >= 0) & (df["carbohydrates"] >= 0)]
    
    X = df[FEATURE_COLUMNS].fillna(0)
    y = df[TARGET_COLUMN]
    
    logging.info(f"✅ Cleaned and prepared dataset, resulting in {len(X)} valid rows.")
    return X, y


# --- Model Training and Evaluation ---
def train_and_evaluate_model(X: pd.DataFrame, y: pd.Series) -> Pipeline:
    """Creates a pipeline, performs hyperparameter tuning, and evaluates the best model."""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipeline = Pipeline([
        ('scaler', StandardScaler()),
        ('regressor', RandomForestRegressor(random_state=42, n_jobs=-1))
    ])

    param_distributions = {
        'regressor__n_estimators': [100, 200, 300, 400],
        'regressor__max_depth': [10, 15, 20, 25, None],
        'regressor__min_samples_split': [2, 5, 10],
        'regressor__min_samples_leaf': [1, 2, 4],
    }

    search = RandomizedSearchCV(
        pipeline,
        param_distributions,
        n_iter=50, cv=5, verbose=1, random_state=42, n_jobs=-1
    )
    logging.info("⏳ Starting hyperparameter search...")
    search.fit(X_train, y_train)
    
    logging.info(f"🏆 Best parameters found: {search.best_params_}")

    # --- FIX FOR PYLANCE ERRORS ---
    # Retrieve the best estimator
    best_model: BaseEstimator = search.best_estimator_
    # Assert that the best estimator is a Pipeline. This informs the type checker.
    assert isinstance(best_model, Pipeline), "Best estimator is not a Pipeline!"
    # Now Pylance knows `best_model` is a Pipeline, and all subsequent calls are valid.
    
    y_pred = best_model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logging.info("📊 Final Model Evaluation:")
    logging.info(f"  - Mean Absolute Error (MAE): {mae:.2f}")
    logging.info(f"  - R² Score: {r2:.3f}")

    try:
        # Accessing `named_steps` is now valid because we asserted the type is Pipeline
        importances = best_model.named_steps['regressor'].feature_importances_
        feature_importance_df = pd.DataFrame({
            'feature': FEATURE_COLUMNS,
            'importance': importances
        }).sort_values('importance', ascending=False)
        
        logging.info("✨ Feature Importances:")
        print(feature_importance_df.to_string()) # Use .to_string() for better console format
    except Exception as e:
        logging.warning(f"Could not display feature importances: {e}")

    return best_model

# --- Save Final Pipeline ---
def save_pipeline(pipeline: Pipeline):
    """Saves the entire trained pipeline object."""
    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)
    logging.info(f"💾 Saved trained pipeline to {MODEL_FILE}")


# --- Main Orchestrator ---
if __name__ == "__main__":
    logging.info("🚀 Starting model training pipeline...")
    
    df = load_dataset()
    X, y = prepare_data(df)
    
    final_pipeline = train_and_evaluate_model(X, y)
    
    # Passing `final_pipeline` is now valid because the return type is correct
    save_pipeline(final_pipeline)
    
    logging.info("✅ Training pipeline complete.")