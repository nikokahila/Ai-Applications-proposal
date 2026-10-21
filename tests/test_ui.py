import gradio as gr

from app import ui


def test_build_ui_creates_app():
    """The interface builds without errors."""
    assert isinstance(ui.build_ui(), gr.Blocks)


def test_create_shows_generator_result(monkeypatch):
    """The UI shows exactly what the recipe generator returns."""
    monkeypatch.setattr(ui, "generate_recipe", lambda text: (" Enjoy!", "• rice", "• Cook the rice."))
    message, ingredients, instructions, _ = ui.on_create("rice")
    assert (message, ingredients, instructions) == (" Enjoy!", "• rice", "• Cook the rice.")


def test_create_handles_two_value_error(monkeypatch):
    """Error results with only two values do not break the UI."""
    monkeypatch.setattr(ui, "generate_recipe", lambda text: ("Unable to generate a recipe.", ""))
    message, ingredients, instructions, _ = ui.on_create("rice")
    assert message == "Unable to generate a recipe."
    assert ingredients == "" and instructions == ""
