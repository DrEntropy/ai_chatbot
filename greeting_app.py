import streamlit as st
 
# Page configuration
st.set_page_config(page_title="Smart Greeter", page_icon="Hi")
 
st.title("Smart Greeting Generator")
st.write("This app generates a personalized greeting based on your inputs.")
 
# Sidebar settings
with st.sidebar:
    st.header("Settings")
    language = st.selectbox(
        "Greeting Language:",
        ["English", "Italian", "French"]
    )
    formality = st.radio(
        "Formality Level:",
        ["Casual", "Formal"]
    )
 
# Main content
name = st.text_input("Enter your name:")
 
if name:
    # Generate greeting based on settings
    greetings = {
        "English": {
            "Casual": f"Hey {name}! What's up?",
            "Formal": f"Good day, {name}. It is a pleasure to meet you."
        },
        "Italian": {
            "Casual": f"Ciao, {name}! How are you?",
            "Formal": f"Good day, {name}. It is a pleasure to meet you."
        },
        "French": {
            "Casual": f"Bonjour, {name}! How are you?",
            "Formal": f"Good day, {name}. It is a pleasure to meet you."
        }
    }
 
    greeting = greetings[language][formality]
 
    st.divider()
    st.subheader("Your Greeting:")
    st.success(greeting)
 
    # Show what settings were used
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Language", language)
    with col2:
        st.metric("Style", formality)
else:
    st.info("Please enter your name above to generate a greeting.")