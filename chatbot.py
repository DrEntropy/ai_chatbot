"""chatbot.py -- Voice-enabled AI chat application.

Speak into your microphone to have a conversation with a local LLM.
A text input is also available as a fallback.
 
"""

import json
import os
import tempfile
from pathlib import Path

import mlx_whisper
import ollama
import streamlit as st

# -- Model configuration -------------------------------------------------------

CONFIG_PATH = Path(__file__).with_name("model_config.json")

WHISPER_MODELS = {
    "Small  -- fast, 244 MB  (recommended for 8 GB RAM)":
        "mlx-community/whisper-small-mlx",
    "Medium -- balanced, 1.4 GB":
        "mlx-community/whisper-medium-mlx",
    "Large v3 -- best quality, 2.9 GB (recommended for 16 GB+ RAM)":
        "mlx-community/whisper-large-v3-mlx",
}

# built in default for when model_config.json is not found or is invalid
DEFAULT_OLLAMA_CONFIG = {
    "default_model": "gemma3:4b",
    "models": [
        {
            "name": "gemma3:4b",
            "label": "Gemma 3 4B",
            "notes": "Lightweight default model.",
        },
    ],
}


def normalize_ollama_models(raw_models: list) -> list[dict]:
    """Normalize config entries into selectable Ollama model definitions."""
    models = []
    for item in raw_models:
        if isinstance(item, str):
            models.append({"name": item, "label": item, "notes": ""})
        elif isinstance(item, dict) and item.get("name"):
            name = str(item["name"])
            models.append({
                "name": name,
                "label": str(item.get("label") or name),
                "notes": str(item.get("notes") or ""),
            })
    return models


def load_ollama_config() -> tuple[list[dict], str, str | None]:
    """Load Ollama model options from model_config.json."""
    error = None
    try:
        with CONFIG_PATH.open(encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {"ollama": DEFAULT_OLLAMA_CONFIG}
        error = f"{CONFIG_PATH.name} was not found. Using built-in defaults."
    except json.JSONDecodeError as exc:
        config = {"ollama": DEFAULT_OLLAMA_CONFIG}
        error = f"{CONFIG_PATH.name} is invalid JSON: {exc}. Using built-in defaults."

    if not isinstance(config, dict):
        config = {"ollama": DEFAULT_OLLAMA_CONFIG}
        error = f"{CONFIG_PATH.name} must contain a JSON object. Using built-in defaults."

    ollama_config = config.get("ollama", {})
    if not isinstance(ollama_config, dict):
        ollama_config = DEFAULT_OLLAMA_CONFIG
        error = f"{CONFIG_PATH.name} has an invalid Ollama section. Using built-in defaults."

    raw_models = ollama_config.get("models", [])
    if not isinstance(raw_models, list):
        raw_models = []

    models = normalize_ollama_models(raw_models)
    if not models:
        models = normalize_ollama_models(DEFAULT_OLLAMA_CONFIG["models"])
        error = f"{CONFIG_PATH.name} has no usable Ollama models. Using built-in defaults."

    default_model = str(
        ollama_config.get("default_model") or DEFAULT_OLLAMA_CONFIG["default_model"]
    )
    model_names = {model["name"] for model in models}
    if default_model not in model_names:
        default_model = models[0]["name"]
    return models, default_model, error

def ensure_model_loaded(model: str) -> None:
    ollama.generate(model=model, keep_alive="5m") 

def update_context_length() -> None:
    ensure_model_loaded(llm_model)
    ps = ollama.ps()
    model = next(
        (model for model in ps.models if model.model == llm_model),
        None,
    )
    if model is None:
        raise RuntimeError(f"{llm_model} is not currently loaded")
    st.session_state.context_length = model.context_length

def summarize_chat() -> str:
    summary_prompt = "Summarize the following conversation in a concise manner, but make clear what the user asked and what the assistant provided."
    summary_prompt += "\n\n" + "\n".join([f"{message['role']}: {message['content']}" for message in st.session_state.messages[1:]])
     
    summary = ollama.chat(
        model=llm_model,
        messages=[{"role":"system", "content": "You are a concise sumarizer."}, {"role":"user", "content": summary_prompt}],
        options={"temperature": temperature},
    )
    print(summary) # for debugging
    return summary["message"]["content"]

# -- Page configuration --------------------------------------------------------

st.set_page_config(page_title="Voice AI Chat", page_icon="🎤", layout="wide")
st.title("🎤 Voice AI Chat")
st.caption(
    "Speak into your microphone -- your voice is transcribed locally by MLX Whisper, "
    "then answered by a local LLM via Ollama. Nothing leaves your Mac."
)

ollama_models, default_ollama_model, config_error = load_ollama_config()
if config_error:
    st.warning(config_error)

# -- Sidebar -------------------------------------------------------------------

with st.sidebar:
    st.subheader("Model Settings")

    model_names = [model["name"] for model in ollama_models]
    model_labels = {model["name"]: model["label"] for model in ollama_models}
    selected_model_index = model_names.index(default_ollama_model)
    llm_model = st.selectbox(
        "LLM Model (Ollama)",
        model_names,
        index=selected_model_index,
        format_func=lambda name: model_labels.get(name, name),
        on_change=update_context_length,
    )
    selected_model = next(
        (model for model in ollama_models if model["name"] == llm_model),
        None,
    )
    if selected_model and selected_model.get("notes"):
        st.caption(selected_model["notes"])
    if "context_length" not in st.session_state:
        with st.spinner("Loading model..."):
         update_context_length()

    whisper_label = st.selectbox("Whisper Model", list(WHISPER_MODELS.keys()))
    whisper_model = WHISPER_MODELS[whisper_label]

    temperature = st.slider("Temperature", min_value=0.0, max_value=2.0,
                            value=0.7, step=0.1)

    st.divider()
    system_prompt = st.text_area("System Prompt", value="You are a helpful assistant. Keep responses concise.", height=100)
    st.divider()
    st.subheader("Chat management")
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0

    st.caption(f"**Token Count**: {st.session_state.token_count}")
    remaining_tokens = st.session_state.context_length-st.session_state.token_count
    st.caption(f"**Context Remaining**: {remaining_tokens} tokens")
    percentage_remaining = remaining_tokens / st.session_state.context_length
    st.caption(f"Percentage remaining: {percentage_remaining*100:.2f}%")

    # warning if remaining tokens is less then 20% to leave room for summarization.
    if remaining_tokens < st.session_state.context_length*0.2:
        st.warning("You are running low on context. Please clear the chat or compact.")

    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False
    if not st.session_state.confirm_clear:
        if st.button("Clear chat"):
            st.session_state.confirm_clear = True
            st.rerun()
    else:
        st.warning("This will delete all chat history, are you sure?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes", use_container_width=True):
                st.session_state.messages = [{"role": "system", "content": system_prompt}]
                st.session_state.token_count = 0
                st.session_state.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("No", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()
    if st.button("Compact chat"):
        summary = summarize_chat()
        system_prompt_with_summary = system_prompt + "\n\n Compact summary of the conversation: " + summary
        st.session_state.messages = [{"role": "system", "content": system_prompt_with_summary}]
        st.session_state.token_count = 0
        st.rerun()
    st.divider()
    st.caption(
        f"**LLM**: {llm_model}\n\n"
        f"**Whisper**: {whisper_model.split('/')[-1]}\n\n"
        f"**Temp**: {temperature}"
    )

# -- Session state -------------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

if "processed_audio_id" not in st.session_state:
    st.session_state.processed_audio_id = None



# -- Helper functions ----------------------------------------------------------


def transcribe_audio(audio_file) -> str:
    """Transcribe a Streamlit audio_input value to text.

    Writes a temporary WAV file, calls MLX Whisper, deletes the temp file,
    and returns the transcript string (empty string if no speech detected).
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_file.read())
        tmp_path = f.name
    try:
        result = mlx_whisper.transcribe(tmp_path, path_or_hf_repo=whisper_model)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)


def stream_response(messages: list) -> str:
    """Send the message history to Ollama and stream the response into the UI.

    Returns the complete response text after streaming finishes.
    """
    with st.chat_message("assistant"):
        placeholder = st.empty()
        response_text = ""
        stream = ollama.chat(
            model=llm_model,
            messages=messages,
            stream=True,
            options={"temperature": temperature},
        )
        for chunk in stream:
            response_text += chunk["message"]["content"]
            placeholder.markdown(response_text + "▌")
            if chunk.done:
                final_chunk = chunk
        if final_chunk is None:
            raise RuntimeError("Ollama stream ended without a final chunk")

        update_token_count(final_chunk)
        placeholder.markdown(response_text)
    return response_text


def update_token_count(chunk: dict) -> None:
    st.session_state.token_count = chunk.eval_count + chunk.prompt_eval_count

def handle_user_message(user_text: str) -> None:
    """Add a user message to session state, display it, and get the AI response."""
    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)
    response = stream_response(st.session_state.messages)
    st.session_state.messages.append({"role": "assistant", "content": response})

# -- Chat history display ------------------------------------------------------

# display chat history, but not the system prompt
for message in st.session_state.messages[1:]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -- Voice input ---------------------------------------------------------------

audio_value = st.audio_input("Click to record, wait a second, then speak")

if audio_value is not None and audio_value.file_id != st.session_state.processed_audio_id:
    st.session_state.processed_audio_id = audio_value.file_id

    with st.spinner("Transcribing your voice with MLX Whisper..."):
        user_text = transcribe_audio(audio_value)

    if not user_text:
        st.warning("No speech detected. Please speak clearly and try again.")
    else:
        st.info(f"You said: **{user_text}**")
        handle_user_message(user_text)
        st.rerun()

# -- Text fallback input -------------------------------------------------------

if prompt := st.chat_input("Or type your message here..."):
    handle_user_message(prompt)
    st.rerun()