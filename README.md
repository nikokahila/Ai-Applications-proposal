# AI Kitchen assistan

Starter template for the **Development of AI Applications** course final group project.

## Team members

- Member 1 Niko Kahila (niko.kahila@stundent.hamk.fi)
- Member 2 Paavo Vertanen (paavo.vertanen@student.hamk.fi)
- Member 3 Ruslan Lysenko (ruslan.lysenko@student.hamk.fi)

## Problem

### Intended users
Who are the primary target users of this application?

Normal everyday people who have difficulty deciding what to cook. People who want to learn new ways of cooking.

### Problem statement
What specific problem does this application solve for those users?

Many people use a lot of mental energy for planning tasty and nutritious every day, week after week. Sometimes people get stuck on repeating meals and their quality of life suffers from that.

### Why AI is appropriate
Why does this problem require AI / LLM capabilities rather than traditional deterministic software?

AI has a lot better flexibility for meal planning than traditional applications. Conversational model allows customization. AI application can also use tools for searching new recipes around the internet.

## Solution
Briefly describe your application, its primary value proposition, and how it addresses the problem statement above.

AI Kitchen assistant. Application that helps with mealplanning by creating a recipe out of ingredients given by User. It can be used as a learning tool (finding out new recipes) or calorie counter. 

## Main user workflow

1. **User Input:** User has 3 different modes to choose from : Create Recipe form ingredients, Suggest a recipe and Cookbook. Each mode has its own Ai Service.(recipegenerator, recipesuggester and memory)
2. **Processing & Guardrails:** The application service layer (`src/services/ai_service.py`) validates and formats the request.
3. **Model Response:** The model client calls Ollama locally and returns the response back through the service layer to the UI.

## Architecture

Below is the initial starter architecture. As your project evolves with additional capabilities, replace or extend this diagram in [`docs/architecture.md`](docs/architecture.md).

```text
User
  ↓
Gradio UI with 3 tabs (app/ui.py)
(Recipe generator)(Recipe suggester)(Cookbook)
  ↓
Application / AI Service (src/services/{selected service}.py)
  ↓
Model Client (src/models/model_client.py)
  ↓
Ollama (Local LLM Server)
```

> **Core Architectural Rule:** The user interface must NEVER communicate directly with the model client or Ollama. All interactions must pass through the service layer (`ai_service.py`).

## Model

- **Model used:** e.g., `llama3.2:latest`
- **Selection rationale:** Lightweight with tool usage cabapility

## Additional AI capability

Select at least one additional capability to implement for your final project:

- [not used] RAG (Retrieval-Augmented Generation)
- [x] Tools / External API integration
- [ ] Model Context Protocol (MCP)
- [ ] Agentic workflow (Model-selected actions based on observations)
- [x] Memory / Persistent state
- [ ] Multimodal interaction (Text + Images)
- [x] Other: Web Search

### Capability justification
Simple tool usage is enough. All memory (user preferences, history, and saved recipes) is saved as JSON file, so the memory retrieval is quick and lightweight. Application searches web only when needed, and saves recipes only when user wants to. No need for RAG, it just complicates things unnecessary

## Setup

### 1. Create the Conda environment

```bash
conda env create -f environment.yml
```

### 2. Activate the environment

```bash
conda activate dev-ai-project
```

### 3. Configure environment variables

Copy `.env.example` to create your local `.env` configuration file:

On Linux / macOS:
```bash
cp .env.example .env
```

On Windows (Command Prompt / PowerShell):
```powershell
copy .env.example .env
```

Ensure `.env` contains valid values for `OLLAMA_BASE_URL` and `MODEL_NAME`:
```env
OLLAMA_BASE_URL=http://localhost:11434
MODEL_NAME=llama3.2
```

### 4. Start Ollama

Make sure Ollama is installed and running locally, then pull your configured model:

```bash
ollama run llama3.2
```

### 5. Run the application

Run the application from the root directory of the project:

```bash
python -m app.main
```

Then open your browser at `http://localhost:7860`.

### 6. Run automated tests

```bash
pytest
```

## Evaluation

Describe your evaluation methodology and summarize key results. Starter test cases can be found in [`evaluation/test_cases.json`](evaluation/test_cases.json).

Refer to [`evaluation/README.md`](evaluation/README.md) for guidelines on defining success, edge cases, and failure scenarios.


We actually forgot to do official evaluation during the project. However we did do testing and eval continuously during the developement.

## Known limitations

- Small model understands only english. When other languages are used, results vary wildly
- Macro counting is not the most trustworthy. It could be improved, by feeding high quality nutritional data, but this time it was not implemented
- Some websites cannot be used. AI bots might be blocked, or there is a language barrier

## Future improvements

- Planned, but not implemented:
  - Automatic user preferences via like and dislike buttons
  - Better implementation on tags, like cookbook search function using tags
- Better memory cabability for more varied recipe suggestions
- Plan meals for the whole week
- Generate shopping list from selected recipes
## Link to the Video
https://drive.google.com/file/d/1HwLeEgE76GbjR4vl1Y4FsS7ZcmJ-s1R4/view?usp=drive_link