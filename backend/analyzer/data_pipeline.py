import os
import asyncio
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple # <-- Added Tuple here

import aiohttp
import pandas as pd
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from tqdm.asyncio import tqdm_asyncio

# --- Setup ---
# Load environment variables from .env file
load_dotenv()
USDA_API_KEY = os.getenv("USDA_API_KEY")
if not USDA_API_KEY:
    raise ValueError("USDA_API_KEY not found in .env file. Please add it.")

# Configure logging for clear output
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- Configuration ---
CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)
BASE_URL = "https://api.nal.usda.gov/fdc/v1/foods/search"

# Flexible nutrient mapping. Easily add or change nutrients to extract.
NUTRIENT_MAPPING = {
    "description": ("description", ""),
    "brand": ("brandOwner", ""),
    "calories": ("Energy", None),
    "protein": ("Protein", None),
    "fat": ("Total lipid (fat)", None),
    "carbohydrates": ("Carbohydrate, by difference", None),
    "fiber": ("Fiber, total dietary", None),
    "sugar": ("Sugars, total including NLEA", None),
    "sodium": ("Sodium, Na", None),
}


# --- Core Fetching Logic (Concurrent & Robust) ---
@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(aiohttp.ClientError),
    before_sleep=lambda retry_state: logging.warning(f"Retrying API call (attempt {retry_state.attempt_number})...")
)
async def _fetch_page_async(session: aiohttp.ClientSession, query: str, page_number: int = 1) -> Dict[str, Any]:
    """Asynchronously fetch one page of results from the USDA API with retries."""
    params = {
        "query": query,
        "pageSize": 200,
        "pageNumber": page_number,
        "api_key": USDA_API_KEY,
    }
    async with session.get(BASE_URL, params=params) as response:
        response.raise_for_status()
        return await response.json()

async def fetch_query_async(session: aiohttp.ClientSession, query: str, limit_per_query: int = 400) -> List[Dict]:
    """Fetch all pages for a single query until the limit is reached."""
    all_foods_for_query = []
    page = 1
    while len(all_foods_for_query) < limit_per_query:
        try:
            data = await _fetch_page_async(session, query=query, page_number=page)
            foods = data.get("foods", [])
            if not foods:
                logging.info(f"No more results for '{query}' on page {page}.")
                break
            all_foods_for_query.extend(foods)
            page += 1
        except aiohttp.ClientResponseError as e:
            logging.error(f"API Error for '{query}' on page {page}: {e.status} {e.message}")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred for '{query}': {e}")
            break
    return all_foods_for_query[:limit_per_query]

async def fetch_usda_data_concurrently(queries_to_fetch: List[str]) -> Dict[str, List[Dict]]:
    """Fetches data for a list of queries concurrently and returns a dictionary."""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_query_async(session, query) for query in queries_to_fetch]
        results_list = await tqdm_asyncio.gather(*tasks, desc="Fetching USDA Data")
        
        fetched_data = {query: result for query, result in zip(queries_to_fetch, results_list)}
        
        total_items = sum(len(items) for items in fetched_data.values())
        logging.info(f"✅ Fetched a total of {total_items} items for {len(queries_to_fetch)} queries.")
        return fetched_data


# --- Caching Logic (Granular) ---
def cache_data(data: Dict[str, List[Dict]]):
    """Save fetched data to cache, one file per query."""
    if not data:
        return
    for query, items in data.items():
        cache_file = CACHE_DIR / f"{query.replace(' ', '_')}.json"
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(items, f, indent=2)
    logging.info(f"💾 Cached data for {len(data)} queries in {CACHE_DIR}")

def load_cached_data(query_list: List[str]) -> Tuple[Dict[str, List[Dict]], List[str]]: # <-- CORRECTED HERE
    """
    Loads data from cache if available.
    Returns a tuple of (cached_data, queries_that_need_fetching).
    """
    cached_data = {}
    queries_to_fetch = []
    for query in query_list:
        cache_file = CACHE_DIR / f"{query.replace(' ', '_')}.json"
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as f:
                cached_data[query] = json.load(f)
        else:
            queries_to_fetch.append(query)
            
    if cached_data:
        total_items = sum(len(v) for v in cached_data.values())
        logging.info(f"📂 Loaded {total_items} items for {len(cached_data)} queries from cache.")
    if queries_to_fetch:
        logging.info(f"⚠️ Queries to fetch from API: {queries_to_fetch}")
        
    return cached_data, queries_to_fetch


# --- Data Processing ---
def extract_nutrient_table(all_food_data: Dict[str, List[Dict]]) -> pd.DataFrame:
    """Converts the raw USDA data dictionary into a clean, structured DataFrame."""
    records = []
    flat_food_list = [food for foods in all_food_data.values() for food in foods]

    for food in flat_food_list:
        nutrients = {n["nutrientName"]: n.get("value", 0) for n in food.get("foodNutrients", [])}
        record = {}
        for df_col, (api_key, default_val) in NUTRIENT_MAPPING.items():
            if api_key in nutrients:
                record[df_col] = nutrients.get(api_key, default_val)
            else:
                record[df_col] = food.get(api_key, default_val)
        records.append(record)
        
    if not records:
        logging.warning("No records were processed. Returning an empty DataFrame.")
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df = df.dropna(subset=["calories", "protein", "fat", "carbohydrates"])
    logging.info(f"📊 Created DataFrame with {len(df)} valid rows from {len(flat_food_list)} total items.")
    return df


# --- Main Orchestrator ---
async def build_dataset(query_list: List[str]) -> pd.DataFrame:
    """High-level function to orchestrate the entire pipeline."""
    cached_data, queries_to_fetch = load_cached_data(query_list)
    
    if queries_to_fetch:
        newly_fetched_data = await fetch_usda_data_concurrently(queries_to_fetch)
        cache_data(newly_fetched_data)
        cached_data.update(newly_fetched_data)
    else:
        logging.info("✅ All queries were found in the cache. No API calls needed.")

    df = extract_nutrient_table(cached_data)
    return df


# --- Example Usage ---
if __name__ == "__main__":
    food_categories = ["raw apple", "banana", "whole wheat bread", "brown rice", "almond milk", "grilled chicken breast", "boiled egg"]
    
    final_df = asyncio.run(build_dataset(food_categories))

    if not final_df.empty:
        output_csv = CACHE_DIR.parent / "usda_nutrition_dataset.csv"
        final_df.to_csv(output_csv, index=False)
        logging.info(f"✅ Final dataset with {len(final_df)} rows saved to {output_csv}")
        
        print("\n--- Sample of Final Dataset ---")
        print(final_df.head())
        print("\n-------------------------------\n")