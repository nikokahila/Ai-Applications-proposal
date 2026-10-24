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
    - Giving a list of ingredients was simple to implement and recipe generation is straight forward when using english.
    - User Preferences and Blacklisted ingredients are also working
- Recipe Suggester
    - a
- Cookbook
    - a

### Observed failure modes
- Recipe generator
    - Using Finnish language generates wild and illogical recipes. json structure is fine, but instructions are nonsense. failure happens, because AI Model we used is so small and not trained on finnish language.
    - Generator kept suggesting foods with blacklisted ingredients. Error was a result of simple variable mix-up: preferences and blacklist were passed to the model in wrong order, causing Application to avoid preferences and preferring blacklisted items
- Recipe Suggester
    - a
- Cookbook
    - a

## Action Items & Improvements
- Recipe generator
    - Using finnish (and other languages) could be implemented by using larger model, or by connecting with a hosted model like ChatGPT. However API was not implemented and Lightweight local model was preferred
    - Blacklisted and Preferences mix-up fixed by changing variable order
- Recipe Suggester
    - a
- Cookbook
    - a
