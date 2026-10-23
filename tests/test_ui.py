import gradio as gr

from app import ui


def test_build_ui_creates_app():
    """UI builds without errors."""
    assert isinstance(ui.build_ui(), gr.Blocks)


def test_create_shows_generator_result(monkeypatch):
    """UI shows what generate_recipe returns."""
    recipe = (" Rice bowl", "• Asian", "• rice", "• Cook the rice.", " 300 kcal")

    def fake_generate_recipe(text, preferences, blacklist):
        return recipe

    monkeypatch.setattr(ui, "generate_recipe", fake_generate_recipe)
    result = ui.on_create("rice", [], [])
    assert result[0:5] == recipe


def test_create_handles_two_value_error(monkeypatch):
    """UI does not crash when generate_recipe returns 2 values."""
    def fake_generate_recipe(text, preferences, blacklist):
        return "Unable to generate a recipe.", ""

    monkeypatch.setattr(ui, "generate_recipe", fake_generate_recipe)
    result = ui.on_create("rice", [], [])
    assert result[0] == "Unable to generate a recipe."
    assert result[1:5] == ("", "", "", "")


def test_suggest_shows_suggester_result(monkeypatch):
    """Suggest tab shows the recipe and the source."""
    recipe = ("Chickpea Curry", "• Indian", "• chickpeas", "• Cook.", "400 kcal", "Recipe found in: example.com")

    def fake_suggest_recipe(preferences, blacklist, sources):
        return recipe

    monkeypatch.setattr(ui, "suggest_recipe", fake_suggest_recipe)
    result = ui.on_suggest(["Indian"], [], ["example.com"])
    assert result[0:6] == recipe
