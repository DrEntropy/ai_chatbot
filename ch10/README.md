# Voice AI Chat

Voice AI Chat is a Streamlit app that transcribes microphone input locally with
MLX Whisper and sends the text to a local Ollama model.


## Requirements

```bash
uv sync
```

Ollama must be installed before the app can answer with a local LLM.  You can either use the 
gui app or start `ollama serve` 

## Set Up Ollama

Pull the models you wish to use and list them in `model_config.json`
The default model was `gemma3:4b`

 
For example;  

```bash
ollama pull gemma3:4b
```

and then make sure it is listed in the config.

Then confirm it is available:

```bash
ollama list
```

## Switch Ollama Models

Ollama model options are configured in `model_config.json`.

To change the default model, edit `ollama.default_model`:

```json
{
  "ollama": {
    "default_model": "gemma3:1b"
  }
}
```

The default model must also exist in `ollama.models`.

To add another model to the app selector, add an entry like this:

```json
{
  "name": "gemma4:e2b",
  "label": "Gemma 4 E2B",
  "notes": "Newer effective 2B Gemma model."
}
```

Then pull the model locally:

```bash
ollama pull gemma4:e2b
```

Restart Streamlit so the app reloads `model_config.json`.

 
## Run

```bash
uv run streamlit run voice_chat.py
```