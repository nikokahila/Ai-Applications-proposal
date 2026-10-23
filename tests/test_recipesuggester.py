import json
from unittest.mock import MagicMock

import pytest

from src.services import recipesuggester

# fake answer from the AI
RECIPE_JSON = json.dumps({
    "message": "Chickpea Curry",
    "tags": ["Indian", "Vegetarian"],
    "ingredients": ["1 can chickpeas", "1 onion"],
    "instructions": ["Fry the onion.", "Add the chickpeas."],
    "macros": ["Calories: 400 kcal"],
})


def fake_model(monkeypatch):
    client = MagicMock()
    client.chat.return_value.message.content = RECIPE_JSON
    monkeypatch.setattr(recipesuggester, "model_client", client)
    return client


def fake_read_source(url):
    return "Chickpea curry recipe text"


def test_suggest_with_source(monkeypatch):
    """Preferences, blacklist and website text go to the AI."""
    client = fake_model(monkeypatch)
    monkeypatch.setattr(recipesuggester, "read_source", fake_read_source)

    result = recipesuggester.suggest_recipe(["Indian"], ["peanut"], ["example.com"])

    prompt = client.chat.call_args.kwargs["messages"][1]["content"]
    assert "Indian" in prompt
    assert "peanut" in prompt
    assert "Chickpea curry recipe text" in prompt
    assert result[0] == "Chickpea Curry"
    assert result[5] == "Recipe found in: example.com"


def test_suggest_without_source(monkeypatch):
    """Without sources the AI suggests a recipe itself."""
    fake_model(monkeypatch)
    result = recipesuggester.suggest_recipe([], [], [])
    assert result[5] == "Recipe suggested by AI"


def test_suggest_blacklist(monkeypatch):
    """Recipe with a blacklisted ingredient is not shown."""
    fake_model(monkeypatch)
    result = recipesuggester.suggest_recipe([], ["chickpea"], [])
    assert "blacklisted" in result[0]


def test_read_source_no_files():
    """file:// links are not allowed."""
    with pytest.raises(ValueError):
        recipesuggester.read_source("file:///etc/passwd")
