import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="💬", layout="centered", page_title="Groq Chat")

st.subheader("Super Chat", divider="rainbow", anchor="false")

#get the apik key 
client=Groq(
    api_key = st.secrets["GROQ_API_KEY"]
)

#initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

#Define model details
models = {
    "llama-3.2-90b-text-preview" : {"name" : "llama-3.2-90b-text-preview", "tokens": 8192},
    "llama-3.1-70b-versatile" : {"name": "llama-3.1-70b-versatile", "tokens": 8192},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768},
}

#layout for model selection and max token slider
model_option = st.selectbox(
    "Choose a model: " ,
    options=list(models.keys()),
    format_func = lambda x: models[x] ["name"],
    index=0
)

#detect model change and clear chat history if model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages=[]
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

#adjst max_tokens slideer dynamically based on the selected model
max_tokens = st.slider(
    "Max Tokens:",
    min_value=512,
    max_value = max_tokens_range,
    step =512,
    help=f"Adjust he maximum number of tokens(words) for the model's response. Max for selected model: {max_tokens_range}"
)

#display chat messages from history
for message in st.session_state.messages:
    avatar= '🤖' if message["role"] == "assistant" else '👨‍💻'
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chung.choices[0].delta.content:
            yield chunk.choices[0].delta.content

if prompt := st.chat_input("What do you want to ask?"):
    st.session_state.messages.append({"role":"user", "content": prompt})

    with st.chat_messages("user", avatat='👨‍💻'):
        st.markdown(prompt)

    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {
                "role":m["role"],
                "content": m["content"],
                }
                for m in st.session_state.message
            ],
            max_tokens = max_tokens,
            stream = True
        )
        #use the generator function with st.write stream
        with st.chat_mesage("assistant", avatar="🤖"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_response_generator)
    except Exception as e:
        st.error(e, icon="🚨")
    
    #append the full response to session_state_messages
    if isinstance(full_response, str):
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append(
            {"role":"assistant", "content": combine_response}
        )



