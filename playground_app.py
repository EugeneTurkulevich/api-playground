import streamlit as st
import streamlit.components.v1 as components
from openai import OpenAI
import requests

def get_local_storage_js(key, default):
    """ Return JavaScript for retrieving values from LocalStorage. """
    return f"""
    <script>
        (function() {{
            // Initialize with default value if not set
            const storedValue = localStorage.getItem("{key}") || '{default}';
            const returnValue = storedValue === 'null' ? '{default}' : storedValue;
            const streamlitDoc = window.parent.document;

            // Send value to Streamlit
            const input = streamlitDoc.createElement('input');
            input.value = returnValue;
            input.id = '{key}';
            input.setAttribute('style', 'display:none;');
            streamlitDoc.body.appendChild(input);
        }})();
    </script>
    """

def set_local_storage_js(key, value):
    """ Return JavaScript for setting values in LocalStorage. """
    return f"""
    <script>
        localStorage.setItem("{key}", "{value}");
    </script>
    """

def get_stored_value(key, default, type_fn=int):
    value = st.session_state.get(key, default)
    try:
        return type_fn(value)
    except ValueError:
        return default

html = get_local_storage_js("temperature", 0.3)
components.html(html, height=0)
html = get_local_storage_js("max_tokens", 50)
components.html(html, height=0)

st.sidebar.title("AI API Playground")

temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0,
                                value=get_stored_value('temperature', 0.3, float), step=0.1)
st.sidebar.markdown("""
"Temperature" is a parameter that controls the randomness of the model’s responses.
* A low value (e.g., 0.1) makes the output more focused and deterministic.
* A high value (e.g., 1.0) makes it more creative and diverse, but less predictable.
The value ranges from 0.0 to 2.0, with 0.7 being a common balanced setting.
""")

max_tokens = st.sidebar.slider("Max Tokens", min_value=1, max_value=1000,
                               value=get_stored_value('max_tokens', 50, int), step=10)
components.html(local_storage_js("max_tokens_slider", 50), height=0)
st.sidebar.markdown("""
"Max Tokens" is a parameter that controls the maximum number of tokens the model can generate in its response.
* A low value (e.g., 10) makes the output shorter and more concise.
* A high value (e.g., 100) makes it longer and more detailed.
The value ranges from 1 to 4096, with 50 being a common balanced setting.
""")

tab1, tab2 = st.tabs(["OpenAI", "Grok"])
tab1.write("OpenAI API Playground")
tab2.write("Grok API Playground")

with tab1:

    col1, col2 = st.columns(2)
    with col1:
        openai_api_key = st.text_input("Enter your OpenAI API Key", type="password")
    with col2:
        openai_model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        openai_selected_model = st.selectbox("Select Model", openai_model_options)

    openai_system_prompt = st.text_area("OpenAI System Prompt", height=150)
    openai_user_prompt = st.text_area("OpenAI User Prompt", height=150)

    if st.button("Send to OpenAI"):
        st.session_state['temperature'] = temperature
        st.session_state['max_tokens'] = max_tokens
        components.html(set_local_storage_js("temperature", temperature), height=0)
        components.html(set_local_storage_js("max_tokens", max_tokens), height=0)
        if not openai_api_key:
            st.error("Please provide a valid API key.")
        else:
            try:
                client = OpenAI(api_key=openai_api_key)
                openai_response = client.chat.completions.create(
                    model=openai_selected_model,
                    messages=[
                        {"role": "system", "content": openai_system_prompt},
                        {"role": "user", "content": openai_user_prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                container = st.container(border=True)
                container.write(openai_response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

with tab2:

    grok_api_key = st.text_input("Enter your Grok API Key", type="password")
    grok_system_prompt = st.text_area("Grok System Prompt", height=150)
    grok_user_prompt = st.text_area("Grok User Prompt", height=150)

    if st.button("Send to Grok"):
        st.session_state['temperature'] = temperature
        st.session_state['max_tokens'] = max_tokens
        components.html(set_local_storage_js("temperature", temperature), height=0)
        components.html(set_local_storage_js("max_tokens", max_tokens), height=0)
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
                    "temperature": temperature,
                }
                grok_response = requests.post(
                    "https://api.x.ai/v1/chat/completions", headers=headers, json=data
                )
                grok_response.raise_for_status()
                grok_result = grok_response.json()
                grok_response_text = grok_result["choices"][0]["message"]["content"]
                container = st.container(border=True)
                container.write(grok_response_text)
            except Exception as e:
                st.error(f"Error: {e}")
