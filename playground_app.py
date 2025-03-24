import streamlit as st
from openai import OpenAI
import requests

st.title("AI API Playground")

tab1, tab2 = st.tabs(["OpenAI", "Grok"])
tab1.write("OpenAI API Playground")
tab2.write("Grok API Playground")

with tab1:

    openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    openai_system_prompt = st.text_area("OpenAI System Prompt", height=150)
    openai_user_prompt = st.text_area("OpenAI User Prompt", height=150)
    openai_model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
    openai_selected_model = st.selectbox("Select Model", openai_model_options)

    if st.button("Send to OpenAI"):
        if not openai_api_key:
            st.error("Please provide a valid API key.")
        else:
            try:
                client = OpenAI(api_key=openai_api_key)
                openai_response = client.chat.completions.create(
                    model=openai_selected_model,
                    instructions=openai_system_prompt,
                    input=openai_user_prompt,
                )
                st.subheader("Response:")
                st.write(openai_response.output_text)
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:

    grok_api_key = st.text_input("Enter your Grok API Key", type="password")
    grok_system_prompt = st.text_area("Grok System Prompt", height=150)
    grok_user_prompt = st.text_area("Grok User Prompt", height=150)

    if st.button("Send to Grok"):
        if not grok_api_key:
            st.error("Please provide a valid API key.")
        else:
            try:
                api_url = "https://api.xai.com/grok"
                headers = {
                    "Authorization": f"Bearer {grok_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": "grok-2-latest",
                    "messages": [
                        {
                            "role": "system",
                            "content": grok_system_prompt,
                        },
                        {
                            "role": "user",
                            "content": grok_user_prompt,
                        },
                    ],
                    "stream": False,
                    "temperature": 0,
                }
                grok_response = requests.post(
                    "https://api.x.ai/v1/chat/completions", headers=headers, json=data
                )
                grok_response.raise_for_status()
                grok_result = grok_response.json()
                grok_response_text = grok_result["choices"][0]["message"]["content"]
                st.subheader("Response:")
                st.write(grok_response_text)
            except Exception as e:
                st.error(f"Error: {e}")

st.sidebar.markdown("""
### HOW TO USE:
1. Choose AI
2. Enter your API KEY
3. Enter System Prompt
4. Enter User Prompt
5. Choose AI model (if any)
6. Press Send
""")
