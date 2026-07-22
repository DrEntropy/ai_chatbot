"""chatbot.py -- Voice-enabled AI chat application.

Speak into your microphone to have a conversation with a local LLM.
A text input is also available as a fallback.
 
"""

import os
import tempfile

import mlx_whisper
import ollama
import streamlit as st

# -- Model configuration -------------------------------------------------------

PREFERRED_OLLAMA_MODEL = "gemma3:4b"

WHISPER_MODELS = {
    "Small  -- fast, 244 MB  (recommended for 8 GB RAM)":
        "mlx-community/whisper-small-mlx",
    "Medium -- balanced, 1.4 GB":
        "mlx-community/whisper-medium-mlx",
    "Large v3 -- best quality, 2.9 GB (recommended for 16 GB+ RAM)":
        "mlx-community/whisper-large-v3-mlx",
}


def _model_notes(details) -> str:
    """Build a short caption from Ollama model details."""
    if details is None:
        return ""
    parts = [
        part
        for part in (
            getattr(details, "family", None) or "",
            getattr(details, "parameter_size", None) or "",
            getattr(details, "quantization_level", None) or "",
        )
        if part
    ]
    return " · ".join(parts)


def list_ollama_models() -> tuple[list[dict], str, str | None]:
    """Fetch installed Ollama models via ollama.list()."""
    try:
        response = ollama.list()
    except Exception as exc:
        return [], "", f"Could not reach Ollama: {exc}"

    models = []
    for item in response.models or []:
        name = getattr(item, "model", None)
        if not name:
            continue
        models.append({
            "name": name,
            "label": name,
            "notes": _model_notes(getattr(item, "details", None)),
        })
    models.sort(key=lambda model: model["name"].lower())

    if not models:
        return [], "", "No Ollama models found. Pull a model with `ollama pull`, then refresh."

    model_names = {model["name"] for model in models}
    default_model = (
        PREFERRED_OLLAMA_MODEL
        if PREFERRED_OLLAMA_MODEL in model_names
        else models[0]["name"]
    )
    return models, default_model, None

def ensure_model_loaded(model: str) -> None:
    ollama.generate(model=model, keep_alive="5m")


def context_length_from_show(model_name: str) -> int:
    """Read max context length from ollama.show (works for local and cloud models)."""
    info = ollama.show(model_name)
    modelinfo = getattr(info, "modelinfo", None) or {}
    for key, value in modelinfo.items():
        if str(key).endswith("context_length"):
            return int(value)
    raise RuntimeError(f"Could not determine context length for {model_name}")


def update_context_length() -> None:
    model_name = st.session_state.llm_model
    ensure_model_loaded(model_name)
    ps = ollama.ps()
    loaded = next(
        (model for model in ps.models if model.model == model_name),
        None,
    )
    if loaded is not None and loaded.context_length:
        st.session_state.context_length = loaded.context_length
        return
    # Cloud models are served remotely and typically never appear in ollama.ps().
    st.session_state.context_length = context_length_from_show(model_name)

def summarize_chat() -> str:
    summary_prompt = (
        "Summarize the following conversation in a concise manner, "
        "but make clear what the user asked and what the assistant provided."
    )
    summary_prompt += "\n\n" + "\n".join(
        f"{message['role']}: {message['content']}"
        for message in st.session_state.model_messages[1:]
    )

    summary = ollama.chat(
        model=llm_model,
        messages=[
            {"role": "system", "content": "You are a concise sumarizer."},
            {"role": "user", "content": summary_prompt},
        ],
        options={"temperature": temperature},
    )
    #print(summary)  # for debugging
    return summary["message"]["content"]


def reset_model_messages(system_content: str) -> None:
    st.session_state.model_messages = [{"role": "system", "content": system_content}]


def clear_chat(system_content: str) -> None:
    reset_model_messages(system_content)
    st.session_state.display_messages = []
    st.session_state.token_count = 0

# -- Page configuration --------------------------------------------------------

st.set_page_config(page_title="Voice AI Chat", page_icon="🎤", layout="wide")
st.title("🎤 Voice AI Chat")
st.caption(
    "Speak into your microphone -- your voice is transcribed locally by MLX Whisper, "
    "then answered by a local LLM via Ollama. Nothing leaves your Mac."
)

ollama_models, default_ollama_model, list_error = list_ollama_models()
if list_error:
    st.error(list_error)
    st.stop()

# -- Sidebar -------------------------------------------------------------------

with st.sidebar:
    st.subheader("Model Settings")

    model_names = [model["name"] for model in ollama_models]
    model_labels = {model["name"]: model["label"] for model in ollama_models}
    if st.session_state.get("llm_model") not in model_names:
        # Initial default, or drop a stale selection (model removed from Ollama).
        st.session_state.llm_model = default_ollama_model
    llm_model = st.selectbox(
        "LLM Model (Ollama)",
        model_names,
        format_func=lambda name: model_labels.get(name, name),
        on_change=update_context_length,
        key="llm_model",
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

    if "model_messages" not in st.session_state:
        reset_model_messages(system_prompt)
    if "display_messages" not in st.session_state:
        st.session_state.display_messages = []
    if "token_count" not in st.session_state:
        st.session_state.token_count = 0
    if "processed_audio_id" not in st.session_state:
        st.session_state.processed_audio_id = None

    st.divider()
    st.subheader("Chat management")

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
                clear_chat(system_prompt)
                st.session_state.confirm_clear = False
                st.rerun()
        with col2:
            if st.button("No", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()
    can_compact = len(st.session_state.model_messages) > 1
    if st.button("Compact chat", disabled=not can_compact):
        with st.spinner("Compacting conversation..."):
            summary = summarize_chat()
        system_prompt_with_summary = (
            system_prompt + "\n\nCompact summary of the conversation: " + summary
        )
        reset_model_messages(system_prompt_with_summary)
        st.session_state.display_messages.append({
            "role": "assistant",
            "content": summary,
            "kind": "compact",
        })
        st.session_state.token_count = 0
        st.rerun()
    st.divider()
    st.caption(
        f"**LLM**: {llm_model}\n\n"
        f"**Whisper**: {whisper_model.split('/')[-1]}\n\n"
        f"**Temp**: {temperature}"
    )

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


def stream_response(messages: list) -> tuple[str, str]:
    """Send the message history to Ollama and stream the response into the UI.

    Returns (content, thinking) after streaming finishes.
    """
    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        content_placeholder = st.empty()
        thinking_text = ""
        response_text = ""
        final_chunk = None
        stream = ollama.chat(
            model=llm_model,
            messages=messages,
            stream=True,
            options={"temperature": temperature},
        )
        for chunk in stream:
            message = chunk["message"]
            thinking_text += message.get("thinking") or ""
            response_text += message.get("content") or ""
            if thinking_text:
                with thinking_placeholder.container():
                    with st.expander("Thinking", expanded=not response_text):
                        st.markdown(thinking_text)
            if response_text:
                content_placeholder.markdown(response_text + "▌")
            if chunk.done:
                final_chunk = chunk
        if final_chunk is None:
            raise RuntimeError("Ollama stream ended without a final chunk")

        update_token_count(final_chunk)
        if thinking_text:
            with thinking_placeholder.container():
                with st.expander("Thinking", expanded=False):
                    st.markdown(thinking_text)
        content_placeholder.markdown(response_text)
    return response_text, thinking_text


def update_token_count(chunk: dict) -> None:
    st.session_state.token_count = chunk.eval_count + chunk.prompt_eval_count

def handle_user_message(user_text: str) -> None:
    """Add a user message to display + model context, then get the AI response."""
    user_message = {"role": "user", "content": user_text}
    st.session_state.display_messages.append(user_message)
    st.session_state.model_messages.append(user_message)
    with st.chat_message("user"):
        st.markdown(user_text)
    response, thinking = stream_response(st.session_state.model_messages)
    display_message = {"role": "assistant", "content": response}
    if thinking:
        display_message["thinking"] = thinking
    st.session_state.display_messages.append(display_message)
    # Model context only needs the final answer, not the thinking trace.
    st.session_state.model_messages.append({"role": "assistant", "content": response})

# -- Chat history display ------------------------------------------------------

for message in st.session_state.display_messages:
    with st.chat_message(message["role"]):
        if message.get("kind") == "compact":
            st.info("Conversation compacted for the model.")
            with st.expander("Summary sent to model"):
                st.markdown(message["content"])
        else:
            if message.get("thinking"):
                with st.expander("Thinking"):
                    st.markdown(message["thinking"])
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