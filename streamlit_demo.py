import streamlit as st
 
# --- Page Configuration ---
st.set_page_config(
    page_title="Streamlit Components Demo",
    page_icon="Tools",
    layout="wide"
)
 
# --- Title and Text ---
st.title("Streamlit Components Demo")
st.header("This is a header")
st.subheader("This is a subheader")
st.write("The `st.write` function is the Swiss Army knife of Streamlit. "
         "It can display text, data, charts, and more.")
 
# --- Divider ---
st.divider()
 
# --- Text Input ---
st.subheader("Text Input")
user_input = st.text_input("Type something here:")
if user_input:
    st.write(f"You typed: {user_input}")
 
# --- Text Area ---
st.subheader("Text Area")
long_text = st.text_area("Write a longer message:", height=100)
if long_text:
    st.write(f"Your message has {len(long_text)} characters.")
 
# --- Selectbox ---
st.subheader("Selectbox")
color = st.selectbox(
    "What is your favorite color?",
    ["Red", "Blue", "Green", "Yellow", "Purple"]
)
st.write(f"You selected: {color}")
 
# --- Slider ---
st.subheader("Slider")
age = st.slider("Select your age:", 0, 100, 25)
st.write(f"Your age: {age}")
 
# --- Button ---
st.subheader("Button")
if st.button("Click me!"):
    st.write("You clicked the button!")
    st.balloons()
 
# --- Sidebar ---
with st.sidebar:
    st.header("Sidebar")
    st.write("This content appears in the sidebar.")
    sidebar_option = st.radio(
        "Choose a section:",
        ["Home", "About", "Contact"]
    )
    st.write(f"Selected: {sidebar_option}")
 
# --- Columns ---
st.subheader("Columns Layout")
col1, col2, col3 = st.columns(3)
 
with col1:
    st.write("Column 1")
    st.metric("Temperature", "72°F", "1.2°F")
 
with col2:
    st.write("Column 2")
    st.metric("Wind", "9 mph", "-8%")
 
with col3:
    st.write("Column 3")
    st.metric("Humidity", "86%", "4%")