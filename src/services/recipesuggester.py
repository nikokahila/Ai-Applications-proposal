import html
import json
import random
import re
import urllib.parse
import urllib.request

from pydantic import ValidationError

from src.services.recipegenerator import MODEL_ID, Recipe, model_client

# some sites (like allrecipes) block python, so we say we are a normal browser
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


# 1. Get the recipe text and the exact link to the recipe from a website
def read_source(url: str):
    # add https if user wrote only the domain
    if "://" not in url:
        url = "https://" + url

    # only normal web links, no file:// links
    if not (url.startswith("http://") or url.startswith("https://")):
        raise ValueError("Recipe sources must be http or https links.")

    page = download_page(url)

    # the link is already a recipe page (and not a list of recipes)
    if recipe_json(page) and not is_list_page(url):
        return page_to_text(page), url

    # the link is a list of recipes (like kotikokki.net/reseptit),
    # so we open some recipe links from it and use the first real recipe
    recipe_links = find_recipe_links(page, url)
    random.shuffle(recipe_links)
    for link in recipe_links[:10]:
        try:
            link_page = download_page(link)
        except Exception:
            continue
        if recipe_json(link_page):
            return page_to_text(link_page), link

    # no recipe found, so use the text of the page
    return page_to_text(page), url


def download_page(url: str):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read().decode("utf-8", errors="ignore")


# find links to recipe pages on the same website
def find_recipe_links(page: str, url: str):
    # bbcgoodfood.com and www.bbcgoodfood.com are the same site
    site = urllib.parse.urlparse(url).netloc.replace("www.", "")
    links = []
    for href in re.findall(r'href="([^"#]+)"', page):
        link = urllib.parse.urljoin(url, href)
        if urllib.parse.urlparse(link).netloc.replace("www.", "") != site:
            continue

        # skip lists of recipes like collections and categories
        if is_list_page(link):
            continue

        path = urllib.parse.urlparse(link).path.lower()
        if "recipe" in path or "resept" in path:
            if link not in links and link != url:
                links.append(link)
    return links


# pages like collections and categories have many recipes, not one
def is_list_page(url: str):
    path = urllib.parse.urlparse(url).path.lower()
    for word in ["collection", "category", "kategoria"]:
        if word in path:
            return True
    return False


# most recipe sites have the recipe as json for google (ld+json)
def recipe_json(page: str):
    json_blocks = re.findall(r"<script[^>]*ld\+json[^>]*>(.*?)</script>", page, flags=re.DOTALL)
    for block in json_blocks:
        # a real recipe has ingredients and steps (lists and articles have no steps)
        if "recipeIngredient" in block and "recipeInstructions" in block:
            return block
    return ""


# 2. Take the recipe out of the html page
def page_to_text(page: str):
    block = recipe_json(page)
    if block:
        text = html.unescape(block)
        text = " ".join(text.split())
        return text[:6000]

    # no recipe json, so use the text of the page
    # remove scripts, styles and html tags
    text = re.sub(r"<script.*?</script>", " ", page, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = " ".join(text.split())

    # recipe is usually near the word "ingredients"
    start = text.lower().find("ingredients") - 500
    if start < 0:
        start = 0

    return text[start:start + 3000]


# 3. Suggest a recipe using preferences, blacklist and recipe sources
def suggest_recipe(user_preferences: list, user_blacklist: list, user_sources: list):
    # pick one random source
    source = ""
    if user_sources:
        source = random.choice(user_sources)

    user_prompt_parts = ["Suggest one recipe for me."]
    if user_preferences:
        pref_str = ", ".join(user_preferences)
        user_prompt_parts.append(f"My preferences: {pref_str}")
    if user_blacklist:
        black_str = ", ".join(user_blacklist)
        user_prompt_parts.append(f"NEVER use these ingredients: {black_str}")

    if source:
        try:
            website_text, recipe_link = read_source(source)
        except Exception as error:
            print(f"Could not read {source}: {error}")
            return f"Could not open the recipe source: {source}", "", "", "", "", ""
        user_prompt_parts.append(f"Use the recipe from this website text. Keep ALL its ingredients and steps:\n{website_text}")

    try:
        user_content = "\n".join(user_prompt_parts)

        response = model_client.chat(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful cooking assistant. "
                        "Suggest one practical recipe that fits the user's preferences. "
                        "IMPORTANT: NEVER use ingredients from the blacklist. "
                        "If the user gives text from a recipe website, choose a recipe from that text. "
                        "Return a JSON object with exactly five fields: "
                        "'message' (name of the recipe), "
                        "'tags' (a list of tags relevant to the recipe), "
                        "'ingredients' (a list of strings with quantities), "
                        "'instructions' (a list of cooking steps), "
                        "'macros' (a list of counted macronutrients: calories, proteins, carbohydrates, fat)."
                    ),
                },
                {
                    "role": "user",
                    "content": user_content,
                },
            ],
            format=Recipe.model_json_schema(),
        )

        # JSON Validation
        recipe = Recipe.model_validate_json(response.message.content)

    except (ValidationError, json.JSONDecodeError):
        return "The AI returned an invalid recipe. Please try again.", "", "", "", "", ""
    except Exception as error:
        print(f"Recipe suggestion error: {error}")
        return (
            "Unable to suggest a recipe. Check that Ollama is running "
            "and the model is installed.",
            "", "", "", "", "",
        )

    # check that the recipe has nothing from the blacklist
    for item in recipe.ingredients:
        for bad in user_blacklist:
            if bad.lower() in item.lower():
                return f"The recipe had a blacklisted ingredient ({item}). Please try again.", "", "", "", "", ""

    # Structure Model Output
    message_text = recipe.message

    tags_text = "\n".join(
        f"• {item}" for item in recipe.tags
    )

    ingredients_text = "\n".join(
        f"• {item}" for item in recipe.ingredients
    )

    instructions_text = "\n".join(
        f"• {item}" for item in recipe.instructions
    )

    macros_text = "\n".join(recipe.macros)

    if source:
        source_text = f"Recipe found in: {recipe_link}"
    else:
        source_text = "Recipe suggested by AI"

    return message_text, tags_text, ingredients_text, instructions_text, macros_text, source_text
