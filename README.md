## AI Chatbot Project 

This is for my read through of Building Your OwnApplicatoins with Local AI Models on a Mac
- Currently up through chapter 8

I will record differences here:

- Using vscode installed via official installer and also cursor 
- Ollama already installed via curl rather then brew (manages its own updates)

- Using gemma4:12b-mlx instead of gemma3:4b. (But i have both pulled and plan to do comparisons).
- Also compare qwen3.6:35b-mlx and others . 
    - Use uv run (or use activate, doesnt matter)
    - use uv add instead of pip, so much of chapter 6 doesnt apply


## Usage

- Install uv. 
- Install Ollama, make sure it is running (see below)
- `uv sync` (not really needed, but nice to get all that out of the way)
- use `uv run` for everything.

## Tips

To run streamlit apps:
`uv run streamlit run app.py`
Yeah its clunky.

## Set Up Ollama

Pull the models you wish to use. The app discovers them automatically via `ollama.list`
(preferred default: `gemma3:4b` when installed).

For example:

```bash
ollama pull gemma3:4b
```

Confirm installed models:

```bash
ollama list
```

## File structure

- ch10 :  files created for chapter 10. not sure why we put this in a sub folder
- experiments ; various small scripts to experiment with ollama , streamlit etc.

## Main app

The main app is 'chatbot.py'

```bash
uv run streamlit run chatbot.py
```