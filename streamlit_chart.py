import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.title("Streamlit Chart")
st.header("Section Header")
st.subheader("Subsection")
st.write("General purpose text")
st.markdown("**Bold** and *italic* $e^{i\pi} + 1 = 0$")
st.code("print('hello')", language="python")
st.sidebar.title("Settings")
points = st.sidebar.slider("Select the number of points", 10, 100, 100)
frequency = st.sidebar.slider("Select the frequency", 0.1, 10.0, 1.0)

col1, col2 = st.columns(2)
with col1:
    st.write("This is a simple chart using Streamlit and Matplotlib")

    x = np.linspace(0, 10, points)
    y = np.sin(x * frequency)

    plt.plot(x, y)
    st.pyplot(plt)
 
with col2:
    if st.button("Push me"):
        st.write("You pushed me!")
        # Do something here