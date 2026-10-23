from pathlib import Path

import gradio as gr
from src.services.recipegenerator import generate_recipe
from src.services.recipesuggester import suggest_recipe

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
    new_button = gr.Button("Generate a new recipe", icon=icon("refresh"))

    # generate_recipe returns only 2 values if there is an error
    if len(result) < 5:
        return result[0], "", "", "", "", new_button

    message, tags_text, ingredients_text, instructions_text, macros_text = result
    return message, tags_text, ingredients_text, instructions_text, macros_text, new_button


def on_suggest(preferences, blacklist, sources):
    """Shows the suggested recipe."""
    result = suggest_recipe(preferences, blacklist, sources)
    new_button = gr.Button("Suggest another one", icon=icon("refresh"))

    message, tags_text, ingredients_text, instructions_text, macros_text, source_text = result
    return message, tags_text, ingredients_text, instructions_text, macros_text, source_text, new_button


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

    macros = gr.Markdown("### Macros", visible=show_macros, line_breaks=True)

    if show_source:
        source = gr.Markdown("Recipe found in: —")
        return message, tags, ingredients, instructions, macros, source

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
            sources = gr.Dropdown(
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
                suggested_view = recipe_view(show_source=True)

                suggested_macros = suggested_view[4]

                show_macros.change(
                    fn=lambda checked: gr.update(visible=checked),
                    inputs=show_macros,
                    outputs=suggested_macros,
                )
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
        create_inputs = [ingredients, preferences, blacklist]
        create_outputs = list(created_view) + [create_btn]
        create_btn.click(on_create, inputs=create_inputs, outputs=create_outputs)
        ingredients.submit(on_create, inputs=create_inputs, outputs=create_outputs)

        suggest_inputs = [preferences, blacklist, sources]
        suggest_outputs = list(suggested_view) + [suggest_btn]
        suggest_btn.click(on_suggest, inputs=suggest_inputs, outputs=suggest_outputs)

        for button in (edit_btn, remove_btn):
            button.click(not_connected)

    return demo

from pathlib import Path

import gradio as gr
from src.capabilities.memory import MemoryManager
from src.services.recipegenerator import generate_recipe

memory = MemoryManager(filename="recipe_history.json")

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

def on_create(ingredients):
    """Shows the recipe from the recipe generator."""
    result = generate_recipe(ingredients)
    message, ingredients_text, instructions_text = (*result, "", "")[:3]
    return message, ingredients_text, instructions_text, gr.Button("Generate a new recipe", icon=icon("refresh"))


def not_connected():
    """Used by buttons whose logic is not implemented yet."""
    gr.Info("This feature is not connected yet.")


# --- Layout ---------------------------------------------------------------

def recipe_view(show_source: bool = False):
    """Recipe card: message, ingredients and instructions side by side."""
    message = gr.Markdown("*No recipe yet.*")
    with gr.Row():
        with gr.Column():
            gr.Markdown("### Ingredients")
            ingredients = gr.Markdown(line_breaks=True)
        with gr.Column():
            gr.Markdown("### Instructions")
            instructions = gr.Markdown(line_breaks=True)
    if show_source:
        gr.Markdown("Recipe found in: —")
    return message, ingredients, instructions


def build_ui() -> gr.Blocks:
    """
    Constructs the Gradio web interface.
    """
    with gr.Blocks(title="AI Kitchen Assistant") as demo:
        with gr.Sidebar():
            gr.Markdown("### Preferences")
            gr.Dropdown(
                PREFERENCE_CHOICES, value=[], multiselect=True, allow_custom_value=True,
                label="Recipe preferences", info="Pick one or type your own and press Enter",
            )
            gr.Checkbox(label="Count macros", info="Show calories and macros")
            gr.Dropdown(
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
                created_view = recipe_view()
                
                with gr.Row():
                    like_btn = gr.Button("Like", icon=icon("thumbs-up"))
                    dislike_btn = gr.Button("Dislike", icon=icon("thumbs-down"))
                    save_btn = gr.Button("Save recipe", variant="primary", icon=icon("bookmark"))

            with gr.Tab("Suggest a recipe"):
                gr.Markdown("Get a recipe idea based on your preferences and sources.")
                suggest_btn = gr.Button("Suggest a recipe", variant="primary", icon=icon("sparkles"))
                recipe_view(show_source=True)
                
                with gr.Row():
                    like_btn_2 = gr.Button("Like", icon=icon("thumbs-up"))
                    dislike_btn_2 = gr.Button("Dislike", icon=icon("thumbs-down"))
                    save_btn_2 = gr.Button("Save recipe", variant="primary", icon=icon("bookmark"))

            with gr.Tab("Cookbook"):
                saved_recipes = memory.load_cookbook()
                recipe_choices = [
                    item.get("message", f"Resepti {i+1}")
                    for i, item in enumerate(saved_recipes)
                ]

                cookbook_radio = gr.Radio(
                    choices=recipe_choices,
                    label="Saved recipes",
                    info="Saved recipes will appear here",
                )
                cookbook_output = gr.Markdown("*Pick a recipe from the list.*")

                def show_saved_recipe(selected_title):
                    for item in saved_recipes:
                        if item.get("message") == selected_title:
                            ingrs = "\n".join(f"• {i}" for i in item.get("ingredients", []))
                            insts = "\n".join(f"• {i}" for i in item.get("instructions", []))
                            return f"### {item.get('message')}\n\n**Ingredients:**\n{ingrs}\n\n**Instructions:**\n{insts}"
                    return "*No recipe selected.*"

                cookbook_radio.change(
                    show_saved_recipe, inputs=cookbook_radio, outputs=cookbook_output
                )

                with gr.Accordion("Edit recipe", open=False):
                    gr.Textbox(label="Title")
                    gr.Textbox(label="Tags", placeholder="Indian, Vegetarian")
                    gr.Textbox(label="Ingredients (one per line)", lines=5)
                    gr.Textbox(label="Instructions (one per line)", lines=5)
                    edit_btn = gr.Button("Save changes", variant="primary", icon=icon("check"))
                remove_btn = gr.Button("Remove recipe", variant="stop", icon=icon("trash"))

        def save_current_recipe(message_text, ingredients_text, instructions_text):
            if not message_text or "*No recipe yet*" in message_text:
                gr.Warning("No recipe to save yet!")
                return gr.update()
                
            ing_list = [i.replace("• ", "").strip() for i in ingredients_text.split("\n") if i.strip()]
            ins_list = [i.replace("• ", "").strip() for i in instructions_text.split("\n") if i.strip()]
            
            recipe_dict = {
                "message": message_text.strip(),
                "ingredients": ing_list,
                "instructions": ins_list
            }
            
            memory.save_to_cookbook(recipe_dict)
            gr.Info("Recipe saved to Cookbook!")
            
            updated_saved = memory.load_cookbook()
            new_choices = [item.get("message", "Resepti") for item in updated_saved]
            return gr.update(choices=new_choices)

        save_btn.click(
            save_current_recipe,
            inputs=[created_view[0], created_view[1], created_view[2]],
            outputs=[cookbook_radio]
        )

        for event in (create_btn.click, ingredients.submit):
            event(on_create, inputs=ingredients, outputs=[*created_view, create_btn])

        for button in (like_btn, dislike_btn, suggest_btn, save_btn_2, like_btn_2, dislike_btn_2, edit_btn, remove_btn):
            button.click(not_connected)

    return demo