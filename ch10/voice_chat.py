import streamlit as st
import mlx_whisper
import ollama
import tempfile
import os
 
WHISPER_MODEL = "mlx-community/whisper-medium-mlx"
OLLAMA_MODEL = "gemma3:4b"
 
st.title("🎤 Voice AI Chat")

# initialize the  sesssion state messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# display the messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

 
audio_value = st.audio_input("Click the microphone to record your message")
 
if audio_value is not None:
    # Transcribe
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_value.read())
        tmp_path = f.name
 
    with st.spinner("Transcribing..."):
        result = mlx_whisper.transcribe(tmp_path, path_or_hf_repo=WHISPER_MODEL)
        user_text = result["text"].strip()
 
    os.unlink(tmp_path)
    
    if not user_text:
        st.warning("No speech was detected. Please try again.")
    else:
        # Show user messages
        st.session_state.messages.append({"role": "user", "content": user_text})
        with st.chat_message("user"):
            st.markdown(user_text)

        # Generate AI Reposone
        with st.chat_message("assistant"):
            response_text = "" 
            placeholder = st.empty()
            stream = ollama.chat(model= OLLAMA_MODEL,
                messages=st.session_state.messages, stream = True)
            for chunk in stream:
                response_text += chunk["message"]["content"]
                placeholder.markdown(response_text + "▌")
            placeholder.markdown(response_text)
        
        # Add AI message to the session state
        st.session_state.messages.append({"role": "assistant", "content": response_text})