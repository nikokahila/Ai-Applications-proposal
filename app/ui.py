from pathlib import Path

import gradio as gr
from src.services.recipegenerator import generate_recipe

THEME = gr.themes.Base(
    primary_hue="orange",
    neutral_hue="zinc",
    font=[gr.themes.GoogleFont("Inter"), "system-ui", "sans-serif"],
)
# Icons are dark grey: make them white on coloured buttons and in dark mode
CSS = "button.primary img, button.stop img, .dark button img { filter: brightness(0) invert(1); }"

# Line icons in the style of Lucide (lucide.dev, ISC license)
ICONS_DIR = Path(__file__).parent / "icons"
gr.set_static_paths(paths=[ICONS_DIR])
PREFERENCE_CHOICES = ["Indian", "Vegetarian", "Low on calories"]


def icon(name: str) -> str:
    """Path to an SVG icon in app/icons."""
    return str(ICONS_DIR / f"{name}.svg")


# --- Event handlers -------------------------------------------------------

def on_create(ingredients, preferences, blacklist):
    """Shows the recipe from the recipe generator."""
    result = generate_recipe(ingredients, preferences, blacklist)
    # Some error results have only two values; show the missing ones as empty
    message, tags_text, ingredients_text, instructions_text, macros_text = (*result, "", "")[:5]
    return message, tags_text, ingredients_text, instructions_text, macros_text, gr.Button("Generate a new recipe", icon=icon("refresh"))


def not_connected():
    """Used by buttons whose logic is not implemented yet."""
    gr.Info("This feature is not connected yet.")


# --- Layout ---------------------------------------------------------------

def recipe_view(show_source: bool = False, show_macros: bool = False):
    """Recipe card: message, ingredients and instructions side by side."""
    message = gr.Markdown("*No recipe yet.*")
    tags = gr.Markdown()

    with gr.Row():
        with gr.Column():
            gr.Markdown("### Ingredients")
            ingredients = gr.Markdown(line_breaks=True)

        with gr.Column():
            gr.Markdown("### Instructions")
            instructions = gr.Markdown(line_breaks=True)

    macros = gr.Markdown("### Macros", visible=show_macros)

    if show_source:
        gr.Markdown("Recipe found in: —")

    return message, tags, ingredients, instructions, macros


def recipe_actions() -> None:
    """Like / dislike / save buttons shown under a recipe."""
    with gr.Row():
        like_btn = gr.Button("Like", icon=icon("thumbs-up"))
        dislike_btn = gr.Button("Dislike", icon=icon("thumbs-down"))
        save_btn = gr.Button("Save recipe", variant="primary", icon=icon("bookmark"))
    for button in (like_btn, dislike_btn, save_btn):
        button.click(not_connected)

def build_ui() -> gr.Blocks:
    """
    Constructs the Gradio web interface.

    Architectural Principle: The UI talks only to the service layer
    and never directly with Ollama or the model client.
    """
    with gr.Blocks(title="AI Kitchen Assistant") as demo:
        with gr.Sidebar():
            gr.Markdown("### Preferences")
            preferences = gr.Dropdown(
                PREFERENCE_CHOICES, value=[], multiselect=True, allow_custom_value=True,
                label="Recipe preferences", info="Pick one or type your own and press Enter",
            )
            show_macros = gr.Checkbox(label="Show macros",
                info="Show calories and macros", value=False,
            )

            blacklist = gr.Dropdown(
                [], value=[], multiselect=True, allow_custom_value=True,
                label="Blacklisted ingredients", info="Never use these ingredients",
            )
            gr.Dropdown(
                [], value=[], multiselect=True, allow_custom_value=True,
                label="Recipe sources", info="Websites to search for recipes",
            )

        gr.Markdown("# AI Kitchen Assistant\nHello! How can I help you today? :)")

        with gr.Tabs():
            with gr.Tab("Cook from ingredients"):
                ingredients = gr.Textbox(
                    label="Your ingredients", placeholder="chicken, rice, onion", lines=3,
                )
                gr.Checkbox(label="Strict mode", info="Use only these ingredients")
                create_btn = gr.Button("Create a recipe", variant="primary", icon=icon("sparkles"))
                created_view = recipe_view(show_macros=False)

                macros_component = created_view[-1]

                show_macros.change(
                    fn=lambda checked: gr.update(visible=checked),
                    inputs=show_macros,
                    outputs=macros_component,
)
                recipe_actions()

            with gr.Tab("Suggest a recipe"):
                gr.Markdown("Get a recipe idea based on your preferences and sources.")
                suggest_btn = gr.Button("Suggest a recipe", variant="primary", icon=icon("sparkles"))
                recipe_view(show_source=True)
                recipe_actions()

            with gr.Tab("Cookbook"):
                gr.Radio([], label="Saved recipes", info="Saved recipes will appear here")
                gr.Markdown("*Pick a recipe from the list.*")
                with gr.Accordion("Edit recipe", open=False):
                    gr.Textbox(label="Title")
                    gr.Textbox(label="Tags", placeholder="Indian, Vegetarian")
                    gr.Textbox(label="Ingredients (one per line)", lines=5)
                    gr.Textbox(label="Instructions (one per line)", lines=5)
                    edit_btn = gr.Button("Save changes", variant="primary", icon=icon("check"))
                remove_btn = gr.Button("Remove recipe", variant="stop", icon=icon("trash"))

        # Connect UI actions to the recipe generator in the service layer
        for event in (create_btn.click, ingredients.submit):
            event(on_create, inputs=[ingredients, preferences, blacklist], outputs=[*created_view, create_btn])

        for button in (suggest_btn, edit_btn, remove_btn):
            button.click(not_connected)

    return demo
