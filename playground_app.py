import streamlit as st
import streamlit.components.v1 as components
from streamlit_javascript import st_javascript
from openai import OpenAI
from PIL import Image
from io import BytesIO
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

with st.sidebar:

    with st.expander("AI API Playground", expanded=False):
        components.html(get_local_storage_js('temperature', "0.3"), height=0)
        components.html(get_local_storage_js('max_tokens', "50"), height=0)
        temperature_value = float(st_javascript("localStorage.getItem('temperature') || '0.3'"))
        max_tokens_value = int(st_javascript("localStorage.getItem('max_tokens') || '50'"))

        components.html(get_local_storage_js('openai_api_key', ""), height=0)
        components.html(get_local_storage_js('openai_model', "gpt-3.5-turbo"), height=0)
        components.html(get_local_storage_js('openai_system_prompt', ""), height=0)
        components.html(get_local_storage_js('openai_user_prompt', ""), height=0)
        openai_api_key_value = st_javascript("localStorage.getItem('openai_api_key') || ''")
        openai_model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        openai_model_from_storage = st_javascript("localStorage.getItem('openai_model') || 'gpt-3.5-turbo'")
        try:
            openai_model_index_value = openai_model_options.index(openai_model_from_storage)
        except (ValueError, TypeError):
            openai_model_index_value = 0
        openai_system_prompt_value = st_javascript("localStorage.getItem('openai_system_prompt') || ''")
        openai_user_prompt_value = st_javascript("localStorage.getItem('openai_user_prompt') || ''")

        components.html(get_local_storage_js('grok_api_key', ""), height=0)
        components.html(get_local_storage_js('grok_system_prompt', ""), height=0)
        components.html(get_local_storage_js('grok_user_prompt', ""), height=0)
        grok_api_key_value = st_javascript("localStorage.getItem('grok_api_key') || ''")
        grok_system_prompt_value = st_javascript("localStorage.getItem('grok_system_prompt') || ''")
        grok_user_prompt_value = st_javascript("localStorage.getItem('grok_user_prompt') || ''")

        components.html(get_local_storage_js('dalle_api_key', ""), height=0)
        components.html(get_local_storage_js('dalle_model', "dall-e-3"), height=0)
        components.html(get_local_storage_js('dalle_prompt', ""), height=0)
        dalle_api_key_value = st_javascript("localStorage.getItem('dalle_api_key') || ''")
        dalle_model_options = ["dall-e-2", "dall-e-3"]
        dalle_model_from_storage = st_javascript("localStorage.getItem('dalle_model') || 'dall-e-3'")
        try:
            dalle_model_index_value = dalle_model_options.index(dalle_model_from_storage)
        except (ValueError, TypeError):
            dalle_model_index_value = 0
        dalle_style_options = ["vivid", "natural"]
        dalle_prompt_value = st_javascript("localStorage.getItem('dalle_prompt') || ''")

    temperature = st.slider("Temperature", min_value=0.0, max_value=1.0, value=temperature_value, step=0.1)
    with st.expander("Temperature"):
        st.markdown("""
        "Temperature" is a parameter that controls the randomness of the model’s responses.
        * A low value (e.g., 0.1) makes the output more focused and deterministic.
        * A high value (e.g., 1.0) makes it more creative and diverse, but less predictable.
        The value ranges from 0.0 to 2.0, with 0.7 being a common balanced setting.
        """)

    max_tokens = st.slider("Max Tokens", min_value=10, max_value=1000, value=max_tokens_value, step=10)
    with st.expander("Max Tokens"):
        st.markdown("""
        "Max Tokens" is a parameter that controls the maximum number of tokens the model can generate in its response.
        * A low value (e.g., 10) makes the output shorter and more concise.
        * A high value (e.g., 100) makes it longer and more detailed.
        The value ranges from 1 to 4096, with 50 being a common balanced setting.
        """)

tab1, tab2, tab3 = st.tabs(["OpenAI", "Grok", "Dall-e"])
tab1.write("OpenAI API Playground")
tab2.write("Grok API Playground")
tab3.write("Dall-e API Playground")

with tab1:

    col1, col2 = st.columns(2)
    with col1:
        openai_api_key = st.text_input("Enter your OpenAI API Key", type="password", value=openai_api_key_value)
    with col2:
        openai_selected_model = st.selectbox("OpenAI Model", openai_model_options, index=openai_model_index_value)

    openai_system_prompt = st.text_area("OpenAI System Prompt", height=150, value=openai_system_prompt_value)
    openai_user_prompt = st.text_area("OpenAI User Prompt", height=150, value=openai_user_prompt_value)

    if st.button("Send to OpenAI"):
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
        with st.expander("", expanded=False):
            components.html(set_local_storage_js("temperature", temperature), height=0)
            components.html(set_local_storage_js("max_tokens", max_tokens), height=0)
            components.html(set_local_storage_js("openai_api_key", openai_api_key), height=0)
            components.html(set_local_storage_js("openai_model", openai_selected_model), height=0)
            components.html(set_local_storage_js("openai_system_prompt", openai_system_prompt), height=0)
            components.html(set_local_storage_js("openai_user_prompt", openai_user_prompt), height=0)

with tab2:

    grok_api_key = st.text_input("Enter your Grok API Key", type="password", value=grok_api_key_value)
    grok_system_prompt = st.text_area("Grok System Prompt", height=150, value=grok_system_prompt_value)
    grok_user_prompt = st.text_area("Grok User Prompt", height=150, value=grok_user_prompt_value)

    if st.button("Send to Grok"):
        if not grok_api_key:
            st.error("Please provide a valid API key.")
        else:
            try:
                api_url = "https://api.x.ai/v1/chat/completions"
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
                    api_url, headers=headers, json=data
                )
                grok_response.raise_for_status()
                grok_result = grok_response.json()
                grok_response_text = grok_result["choices"][0]["message"]["content"]
                container = st.container(border=True)
                container.write(grok_response_text)
            except Exception as e:
                st.error(f"Error: {e}")
        with st.expander("", expanded=False):
            components.html(set_local_storage_js("temperature", temperature), height=0)
            components.html(set_local_storage_js("max_tokens", max_tokens), height=0)
            components.html(set_local_storage_js("grok_api_key", grok_api_key), height=0)
            components.html(set_local_storage_js("grok_system_prompt", grok_system_prompt), height=0)
            components.html(set_local_storage_js("grok_user_prompt", grok_user_prompt), height=0)

with tab3:

    col1, col2 = st.columns(2)
    with col1:
        dalle_api_key = st.text_input("Enter your Dall-e API Key", type="password", value=dalle_api_key_value)
    with col2:
        dalle_selected_model = st.selectbox("Dall-e Model", dalle_model_options, index=dalle_model_index_value)
        if dalle_selected_model == "dall-e-3":
            dalle_style = st.selectbox("Dall-e Style", dalle_style_options)
        else:
            dalle_style = None

    resize_factor_values = {
        "dall-e-2": 100,
        "dall-e-3": 50,
    }
    default_resize_value = resize_factor_values.get(dalle_selected_model, 70)
    dalle_prompt = st.text_area("Dall-e Prompt", height=150, value=dalle_prompt_value)
    resize_factor = st.slider("Resize Factor (%)", min_value=10, max_value=100, value=default_resize_value, step=10)

    if st.button("Send to Dall-e"):
        if not dalle_api_key:
            st.error("Please provide a valid API key.")
        else:
            with st.spinner("Generating image..."):
                api_url = "https://api.openai.com/v1/images/generations"
                if dalle_selected_model == "dall-e-2":
                    image_size = "512x512"
                elif dalle_selected_model == "dall-e-3":
                    image_size = "1024x1024"
                headers = {
                    "Authorization": f"Bearer {dalle_api_key}",
                    "Content-Type": "application/json"
                }
                data = {
                    "model": dalle_selected_model,
                    "prompt": dalle_prompt,
                    "n": 1,
                    "size": image_size
                }
                if dalle_style:
                    data["style"] = dalle_style
                try:
                    dalle_response = requests.post(
                        api_url, headers=headers, json=data
                    )
                    dalle_response.raise_for_status()
                    dalle_result = dalle_response.json()
                    image_url = dalle_result["data"][0]["url"]
                    # st.image(image_url)
                    response = requests.get(image_url)
                    img = Image.open(BytesIO(response.content))
                    width, height = img.size
                    new_width = int(width * resize_factor / 100)
                    new_height = int(height * resize_factor / 100)
                    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
                    st.image(resized_img, caption="Generated Image")
                    buf = BytesIO()
                    img.save(buf, format="PNG")
                    byte_im = buf.getvalue()
                    st.download_button(
                        label="Download Image",
                        data=byte_im,
                        file_name="dalle_generated_image.png",
                        mime="image/png"
                    )
                    st.success("Image generated successfully!")
                except Exception as e:
                    st.error(f"Error generating image: {e}")
        with st.expander("", expanded=False):
            components.html(set_local_storage_js("dalle_api_key", dalle_api_key), height=0)
            components.html(set_local_storage_js("dalle_model", dalle_selected_model), height=0)
            components.html(set_local_storage_js("dalle_prompt", dalle_prompt), height=0)
