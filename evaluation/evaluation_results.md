# Evaluation Results Summary

Document your team's evaluation results below.

## Summary Overview

- **Date of Evaluation:** YYYY-MM-DD
- **Model Evaluated:** (e.g., `llama3.2:latest`)
- **Total Test Cases Executed:** 0
- **Passed:** 0
- **Failed:** 0
- **Pass Rate:** 0%

## Performance by Category

| Category | Total Cases | Passed | Failed | Pass Rate |
| :--- | :---: | :---: | :---: | :---: |
| Successful Cases | 0 | 0 | 0 | 0% |
| Difficult Cases | 0 | 0 | 0 | 0% |
| Failure / Edge Cases | 0 | 0 | 0 | 0% |

## Key Findings & Failure Analysis
official testing and evaluation was not done, but unofficial testing was done during the developement. Here are some obervations made during the developement.

### What worked well
- Recipe generator
    - Giving a list of 
- Recipe Suggester
    - Uses the user preferences, blacklisted ingredients and recipe sources to suggest a recipe.
    - With a recipe page as a source (e.g. BBC Good Food, Kotikokki) the app uses the real recipe from the page and keeps all its ingredients and steps. But with a whole website or a list of recipes as a source (e.g. bbcgoodfood.com or kotikokki.net/reseptit) the app opens one real recipe from it and shows the exact link in "Recipe found in". This worked in 9 of 9 tries.
    - Suggestion takes about 3-10 seconds with llama3.2.
    - Suggestion that has blacklisted ingredient is not shown to the user.
    - Suggested recipe can be saved to the Cookbook together with its link.
- Cookbook
    - a

### Observed failure modes
- Recipe generator
    - a
- Recipe Suggester
    - Without any sources small model sometimes puts all ingredients on one line or mixes ingredients.
    - Some websites blocks app or load their recipes with js, so no recipe can be found there and model makes its own recipe.
    - Sometimes the model repeats the same ingredients twice.
- Cookbook
    - a

## Action Items & Improvements
- Recipe generator
    - a
- Recipe Suggester
    - Save found recipes into memory and pick the one that fits the preferences best, instead of a random page.
    - Make model output more stable when there are no sources.
    - Allow only trusted recipe websites as sources.
- Cookbook
    - a
