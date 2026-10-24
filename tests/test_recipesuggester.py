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
    # text of the recipe and the exact link to it
    return "Chickpea curry recipe text", "https://example.com/recipes/chickpea-curry"


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
    assert result[5] == "Recipe found in: https://example.com/recipes/chickpea-curry"


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


def test_page_to_text_uses_recipe_json():
    """Recipe json on the page is used instead of the menu text."""
    page = (
        "<html><nav>Home Recipes Ingredients Cuisines</nav>"
        '<script type="application/ld+json">{"@type": "Recipe", "name": "Kanakeitto", '
        '"recipeIngredient": ["1 kg kanaa", "5 dl vettä"], "recipeInstructions": ["Keitä"]}</script></html>'
    )
    text = recipesuggester.page_to_text(page)
    assert "Kanakeitto" in text
    assert "1 kg kanaa" in text
    assert "Cuisines" not in text


def test_suggest_source_cannot_be_opened(monkeypatch):
    """If the website does not open, the message says so."""
    fake_model(monkeypatch)

    def broken_read_source(url):
        raise OSError("HTTP Error 403")

    monkeypatch.setattr(recipesuggester, "read_source", broken_read_source)
    result = recipesuggester.suggest_recipe([], [], ["example.com"])
    assert "Could not open the recipe source" in result[0]


def test_find_recipe_links():
    """Only recipe links from the same website are found."""
    page = (
        '<a href="/reseptit/nayta/600/Broileripata/">Broileripata</a>'
        '<a href="/about">About</a>'
        '<a href="/recipes/collection/vegetarian-recipes">Collection</a>'
        '<a href="https://other.com/recipe/1">Other site</a>'
    )
    links = recipesuggester.find_recipe_links(page, "https://www.kotikokki.net/reseptit")
    assert links == ["https://www.kotikokki.net/reseptit/nayta/600/Broileripata/"]


def test_read_source_opens_recipe_from_list_page(monkeypatch):
    """If the source is a list of recipes, one recipe is opened and its exact link is returned."""
    list_page = '<a href="/reseptit/nayta/600/Broileripata/">Broileripata</a>'
    recipe_page = '<script type="application/ld+json">{"name": "Broileripata", "recipeIngredient": ["1 broileri"], "recipeInstructions": ["Cook"]}</script>'

    def fake_download_page(url):
        if url == "https://www.kotikokki.net/reseptit":
            return list_page
        return recipe_page

    monkeypatch.setattr(recipesuggester, "download_page", fake_download_page)
    text, link = recipesuggester.read_source("https://www.kotikokki.net/reseptit")
    assert "1 broileri" in text
    assert link == "https://www.kotikokki.net/reseptit/nayta/600/Broileripata/"


def test_read_source_home_page_is_not_a_recipe(monkeypatch):
    """A home page that only mentions recipeIngredient in other code is not used as the recipe."""
    home_page = '<script>var x = "recipeIngredient";</script><a href="/recipes/focaccia">Focaccia</a>'
    recipe_page = '<script type="application/ld+json">{"name": "Focaccia", "recipeIngredient": ["500g flour"], "recipeInstructions": ["Bake"]}</script>'

    def fake_download_page(url):
        if url == "https://www.bbcgoodfood.com/":
            return home_page
        return recipe_page

    monkeypatch.setattr(recipesuggester, "download_page", fake_download_page)
    text, link = recipesuggester.read_source("https://www.bbcgoodfood.com/")
    assert "500g flour" in text
    assert link == "https://www.bbcgoodfood.com/recipes/focaccia"


def test_find_recipe_links_with_and_without_www():
    """bbcgoodfood.com and www.bbcgoodfood.com are the same website."""
    page = '<a href="https://www.bbcgoodfood.com/recipes/focaccia">Focaccia</a>'
    links = recipesuggester.find_recipe_links(page, "https://bbcgoodfood.com")
    assert links == ["https://www.bbcgoodfood.com/recipes/focaccia"]


def test_read_source_collection_page_opens_one_recipe(monkeypatch):
    """A collection of recipes is not used as one recipe, one recipe from it is opened."""
    collection_url = "https://www.bbcgoodfood.com/recipes/collection/vegetarian-recipes"
    collection_page = (
        '<script type="application/ld+json">{"name": "Vegetarian recipes", "recipeIngredient": ["many"]}</script>'
        '<a href="/recipes/vegan-bolognese">Vegan bolognese</a>'
    )
    recipe_page = '<script type="application/ld+json">{"name": "Vegan bolognese", "recipeIngredient": ["lentils"], "recipeInstructions": ["Cook"]}</script>'

    def fake_download_page(url):
        if url == collection_url:
            return collection_page
        return recipe_page

    monkeypatch.setattr(recipesuggester, "download_page", fake_download_page)
    text, link = recipesuggester.read_source(collection_url)
    assert "lentils" in text
    assert link == "https://www.bbcgoodfood.com/recipes/vegan-bolognese"


def test_recipe_json_needs_steps():
    """Article pages with ingredients but no steps are not recipes."""
    article = '<script type="application/ld+json">{"name": "15 best cakes", "recipeIngredient": ["cake"]}</script>'
    recipe = '<script type="application/ld+json">{"name": "Cake", "recipeIngredient": ["flour"], "recipeInstructions": ["Bake"]}</script>'
    assert recipesuggester.recipe_json(article) == ""
    assert "Cake" in recipesuggester.recipe_json(recipe)
