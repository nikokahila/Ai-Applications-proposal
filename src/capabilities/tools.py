import csv
import json
from pathlib import Path
from src.capabilities.rag import get_rag_search

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
RECIPES_CSV_PATH = DATA_DIR / "PP_recipes.csv"


def search_recipes_with_ai(query: str, max_results: int = 3) -> str:
    """Searches for recipes using semantic RAG search based on the user's query description."""
    print(f"-> [RAG SEARCH ACTIVATED] Searching with query: '{query}'")
    try:
        rag = get_rag_search()
        results = rag.search(query, top_k=max_results)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def search_recipes(query: str, max_results: int = 5) -> str:
    """Searches for recipes from token columns (name or ingredients) based on a query keyword.

    Args:
        query (str): Search keyword (e.g., 'salmon', 'chicken').
        max_results (int): Maximum number of recipes to return.

    Returns:
        str: JSON formatted string of found recipes.
    """
    if not RECIPES_CSV_PATH.exists():
        return json.dumps({"error": f"File {RECIPES_CSV_PATH} not found."}, ensure_ascii=False)

    results = []
    query_lower = query.lower()

    with open(RECIPES_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name_tokens = row.get("name_tokens", "").lower()
            ingredient_tokens = row.get("ingredient_tokens", "").lower()

            if query_lower in name_tokens or query_lower in ingredient_tokens:
                results.append(row)
                if len(results) >= max_results:
                    break

    return json.dumps(results, ensure_ascii=False, indent=2)


def get_recipe_by_id(recipe_id: str) -> str:
    """Retrieves details of a specific recipe by its ID.

    Args:
        recipe_id (str): Recipe ID (from column 'id' or 'i').

    Returns:
        str: Recipe details in JSON format.
    """
    if not RECIPES_CSV_PATH.exists():
        return json.dumps({"error": f"File {RECIPES_CSV_PATH} not found."}, ensure_ascii=False)

    with open(RECIPES_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("id") == recipe_id or row.get("i") == recipe_id:
                return json.dumps(row, ensure_ascii=False, indent=2)

    return json.dumps({"error": "Recipe not found."}, ensure_ascii=False)


def filter_by_calories(max_calories: str, max_results: int = 5) -> str:
    """Filters recipes by calorie level (calorie_level)."""
    if not RECIPES_CSV_PATH.exists():
        return json.dumps({"error": "File not found."}, ensure_ascii=False)

    results = []
    with open(RECIPES_CSV_PATH, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("calorie_level") == str(max_calories):
                results.append(row)
                if len(results) >= max_results:
                    break

    return json.dumps(results, ensure_ascii=False, indent=2)


# All tools collected in a single dictionary
AVAILABLE_TOOLS = {
    "search_recipes_with_ai": search_recipes_with_ai,
    "search_recipes": search_recipes,
    "get_recipe_by_id": get_recipe_by_id,
    "filter_by_calories": filter_by_calories,
}