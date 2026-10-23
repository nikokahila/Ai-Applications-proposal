
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

    ingredients: list[str] = Field(
        description="A list of ingredients with quantities"
    )
    instructions: list[str] = Field(
        description="A list of ordered cooking instructions"
    )


# 2. Generate a recipe using Ollama
def generate_recipe(user_ingredients: str):
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
                        "Create a practical recipe using the ingredients "
                        "provided by the user. You may include basic "
                        "pantry staples when necessary. Do not assume "
                        "the user has other major ingredients. "
                        "Return a JSON object with exactly three fields: "
                        "'message' (a string, a short friendly message)"
                        "'ingredients' (a list of strings with quantities) "
                        "and 'instructions' (a list of numbered cooking "
                        "steps). Make the instructions clear and safe."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Create a recipe using these ingredients: "
                        f"{user_ingredients}"
                    ),
                },
            ],
            format=Recipe.model_json_schema(),
        )
        

        # 3. Parse and validate the AI response
        recipe = Recipe.model_validate_json(
            response.message.content
        )


        # 3. TALLENNETAAN UUSI RESEPTI MUISTIIN
        memory.save_to_memory(recipe.model_dump())

        message_text = f" {recipe.message}"

        # 4. Return the two lists to Gradio
        ingredients_text = "\n".join(
            f"• {item}" for item in recipe.ingredients
        )

        instructions_text = "\n".join(
            f"• {item}" for item in recipe.instructions

            #old with indexes
            # f"{index}. {step}"
            # for index, step in enumerate(
            #     recipe.instructions, start=1
            # )
        )

        return message_text, ingredients_text, instructions_text

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
