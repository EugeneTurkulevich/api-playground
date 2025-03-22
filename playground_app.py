import streamlit as st
from openai import OpenAI

st.title("OpenAI API Playground")

# API key input
api_key = st.text_input("Enter your OpenAI API Key", type="password")

# Text areas for system and user prompts
system_prompt = st.text_area("System Prompt", height=150)
user_prompt = st.text_area("User Prompt", height=150)

# Model selector
model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
selected_model = st.selectbox("Select Model", model_options)

if st.button("Send"):
    if not api_key:
        st.error("Please provide a valid API key.")
    else:
        try:
            client = OpenAI(api_key=api_key)
            response = client.responses.create(
                model=selected_model,
                instructions=system_prompt,
                input=user_prompt,
            )
            st.subheader("Response:")
            st.write(response.output_text)
        except Exception as e:
            st.error(f"Error: {e}")
