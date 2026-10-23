
import json

from ollama import Client
from pydantic import BaseModel, Field, ValidationError


MODEL_ID = "llama3.2:latest"  # Change if needed.
OLLAMA_HOST = "http://localhost:11434"

model_client = Client(host=OLLAMA_HOST, timeout=60.0)



# 1. Define the expected AI response
class Recipe(BaseModel):
    message: str = Field(description="A Friendly message")
    tags: list[str] = Field(description="A list of tags relevant to the recipe")
    ingredients: list[str] = Field(description="A list of ingredients with quantities")
    instructions: list[str] = Field(description="A list of ordered cooking instructions")
    macros: list[str] = Field(description="A macronutrients list")


# 2. Generate a recipe using Ollama
def generate_recipe(user_ingredients: str, user_preferences:list, user_blacklist:list):
    if not user_ingredients.strip():
        return "Please enter some ingredients.", ""
    else:
        user_prompt_parts = [f"Create a recipe using these ingredients: {user_ingredients.strip()}"]
        if user_blacklist:
            black_str = ", ".join(user_blacklist)
            user_prompt_parts.append(f"NEVER use these ingredients: {black_str.strip()}")
        if user_preferences:
            pref_str = ", ".join(user_preferences)
            user_prompt_parts.append(f"If possible, generate the recipe based on these preferences: {pref_str.strip()}")

        user_content = "\n".join(user_prompt_parts)

    try:
        response = model_client.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful cooking assistant. "
                        "Create a practical recipe using the ingredients provided by the user."
                        "You may include basic pantry staples when necessary."
                        "Do not assume the user has other major ingredients. "
                        "IMPORTANT: NEVER use ingredients from the blacklist."
                        "Return a JSON object with exactly five fields: "
                        "'message' (Name of the Recipe, or an error message if something went wrong)"
                        "'tags' (a list of tags relevant to the recipe)"
                        "'ingredients' (a list of strings with quantities) "
                        "'instructions' (a list of numbered cookingsteps)."
                        "'macros' (a list of counted macronutrients: calories, proteins, carbohydrates, fat)"
                        "Make the instructions clear and safe."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        user_content
                    ),
                },
            ],
            format=Recipe.model_json_schema(),
        )

        # Temp print JSON
        print(response.message.content)
        print(user_preferences)
        print(user_blacklist)
        print(user_content)

        # JSON Validation
        recipe = Recipe.model_validate_json(
            response.message.content
        )

        # Structure Model Output
        message_text = f" {recipe.message}"

        tags_text = "\n".join(
            f"• {item}" for item in recipe.tags
        )

        ingredients_text = "\n".join(
            f"• {item}" for item in recipe.ingredients
        )

        instructions_text = "\n".join(
            f"• {item}" for item in recipe.instructions
        )

        macros_text = "\n".join(
            f" {item}" for item in recipe.macros
        )

        return message_text, tags_text, ingredients_text, instructions_text, macros_text

    except (ValidationError, json.JSONDecodeError):
        return (
            "The AI returned an invalid recipe. Please try again.",
            "",
        )
    except Exception as error:
        print(f"Recipe generation error: {error}")
        return (
            "Unable to generate a recipe. Check that Ollama is "
            "running and the model is installed.",
            "",
        )
import json
import pathlib
from pathlib import Path

from ollama import Client
from pydantic import BaseModel, Field, ValidationError

from src.capabilities.memory import MemoryManager

MODEL_ID = "llama3.2:latest"  # Change if needed.
OLLAMA_HOST = "http://localhost:11434"

model_client = Client(host=OLLAMA_HOST, timeout=60.0)
memory = MemoryManager(filename="recipe_history.json")


# 1. Define the expected AI response
class Recipe(BaseModel):
    message: str = Field(description="A Friendly message")
    tags: list[str] = Field(description="A list of tags relevant to the recipe")
    ingredients: list[str] = Field(description="A list of ingredients with quantities")
    instructions: list[str] = Field(description="A list of ordered cooking instructions")
    macros: list[str] = Field(description="A macronutrients list")


# 2. Generate a recipe using Ollama
def generate_recipe(user_ingredients: str, user_preferences:list, user_blacklist:list):
    if not user_ingredients.strip():
        return "Please enter some ingredients.", ""

    try:

        # Haetaan aiempi historia kontekstiksi, jotta tekoäly ei toista itseään
        past_recipes_context = memory.get_recent_summary(limit=3)

        response = model_client.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful cooking assistant. "
                        "Create a practical recipe using the ingredients provided by the user."
                        "You may include basic pantry staples when necessary."
                        "Do not assume the user has other major ingredients. "
                        "IMPORTANT: NEVER use ingredients from the blacklist."
                        "Return a JSON object with exactly five fields: "
                        "'message' (Name of the Recipe, or an error message if something went wrong)"
                        "'tags' (a list of tags relevant to the recipe)"
                        "'ingredients' (a list of strings with quantities) "
                        "'instructions' (a list of numbered cookingsteps)."
                        "'macros' (a list of counted macronutrients: calories, proteins, carbohydrates, fat)"
                        "Make the instructions clear and safe."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        user_content
                    ),
                },
            ],
            format=Recipe.model_json_schema(),
        )

        # Temp print JSON
        print(response.message.content)
        print(user_preferences)
        print(user_blacklist)
        print(user_content)

        # JSON Validation
        recipe = Recipe.model_validate_json(
            response.message.content
        )

        # Structure Model Output


        # 3. TALLENNETAAN UUSI RESEPTI MUISTIIN
        memory.save_to_memory(recipe.model_dump())

        message_text = f" {recipe.message}"

        tags_text = "\n".join(
            f"• {item}" for item in recipe.tags
        )

        ingredients_text = "\n".join(
            f"• {item}" for item in recipe.ingredients
        )

        instructions_text = "\n".join(
            f"• {item}" for item in recipe.instructions
        )

        macros_text = "\n".join(
            f" {item}" for item in recipe.macros
        )

        return message_text, tags_text, ingredients_text, instructions_text, macros_text

    except (ValidationError, json.JSONDecodeError):
        return (
            "The AI returned an invalid recipe. Please try again.",
            "",
        )
    except Exception as error:
        print(f"Recipe generation error: {error}")
        return (
            "Unable to generate a recipe. Check that Ollama is "
            "running and the model is installed.",
            "",
        )