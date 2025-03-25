import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
from openai import OpenAI
import requests

def get_local_storage_js(get_key, default_value):
    """ Returns JavaScript to get a value from LocalStorage and inject into Streamlit. """
    return f"""
    <script>
        (function() {{
            const valueInStorage = localStorage.getItem('{get_key}');
            if (valueInStorage === null) {{
                localStorage.setItem('{get_key}', '{default_value}');
            }}

            // Retrieve the effective value from LocalStorage or default
            const effectiveValue = localStorage.getItem('{get_key}') || '{default_value}';
            const inputField = window.parent.document.createElement("input");
            inputField.type = "text";
            inputField.id = "return-{get_key}";
            inputField.value = effectiveValue;
            inputField.style.display = "none";
            window.parent.document.body.appendChild(inputField);
        }})();
    </script>
    """

def set_local_storage_js(set_key, value_to_set):
    """ Returns JavaScript for setting a value in LocalStorage. """
    return f"""
    <script>
        localStorage.setItem('{set_key}', '{value_to_set}');
    </script>
    """

def get_stored_value(key, default_value, type_cast=int):
    """ Helper function to get a stored value or a default. """
    value = st.session_state.get(key, default_value)
    try:
        # Convert value to the specified type
        return type_cast(value)
    except (ValueError, TypeError):
        # Return default if conversion fails
        return default_value

components.html(get_local_storage_js('temperature', "0.3"), height=0)
components.html(get_local_storage_js('max_tokens', "50"), height=0)

st.sidebar.title("AI API Playground")

temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0,
                                value=float(st_javascript("localStorage.getItem('temperature') || '0.3'")), step=0.1)
st.sidebar.markdown("""
"Temperature" is a parameter that controls the randomness of the model’s responses.
* A low value (e.g., 0.1) makes the output more focused and deterministic.
* A high value (e.g., 1.0) makes it more creative and diverse, but less predictable.
The value ranges from 0.0 to 2.0, with 0.7 being a common balanced setting.
""")

max_tokens = st.sidebar.slider("Max Tokens", min_value=10, max_value=1000,
                               value=int(st_javascript("localStorage.getItem('max_tokens') || '50'")), step=10)
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
        st.sidebar.write(f"Temperature: {temperature}")
        st.sidebar.write(f"Max Tokens: {max_tokens}")
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
