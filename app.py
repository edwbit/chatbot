import streamlit as st
from typing import Generator
from groq import Groq

# Set up the page configuration
st.set_page_config(page_icon="💬", layout="centered", page_title="Groq Chat")

# Add Sidebar Menu
st.sidebar.title("Super Chat App")  # App name

# Sidebar input for API key
api_key = st.sidebar.text_input("Enter your API key", type="password", value=st.secrets.get("GROQ_API_KEY", ""))

# Sidebar button to start a new chat
if st.sidebar.button("New Chat"):
    st.session_state.messages = []  # Clear the chat history

# Initialize the Groq client with the provided API key
client = Groq(
    api_key=api_key
)

st.subheader("Super Chat", divider="rainbow", anchor="false")

# Initialize chat history and selected model
if "messages" not in st.session_state:
    st.session_state.messages = []

if "selected_model" not in st.session_state:
    st.session_state.selected_model = None

# Define model details
models = {
    "llama-3.2-90b-text-preview": {"name": "llama-3.2-90b-text-preview", "tokens": 8192},
    "llama-3.1-70b-versatile": {"name": "llama-3.1-70b-versatile", "tokens": 8192},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768},
}

# Layout for model selection and max token slider
model_option = st.selectbox(
    "Choose a model:",
    options=list(models.keys()),
    format_func=lambda x: models[x]["name"],
    index=0
)

# Detect model change and clear chat history if the model has changed
if st.session_state.selected_model != model_option:
    st.session_state.messages = []
    st.session_state.selected_model = model_option

max_tokens_range = models[model_option]["tokens"]

# Adjust max_tokens slider dynamically based on the selected model
max_tokens = st.slider(
    "Max Tokens:",
    min_value=1024,
    max_value=max_tokens_range,
    step=1024,
    help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}"
)

# Custom CSS for the scrollable chat history
if st.session_state.messages:
    # Custom CSS for the scrollable chat history
    st.markdown("""
        <style>
            .chat-container {
                max-height: 400px;
                overflow-y: scroll;
                border: 1px solid #ccc;
                padding: 10px;
            }
        </style>
        """, unsafe_allow_html=True)

    # Display chat messages from history in a scrollable container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        avatar = '✨' if message["role"] == "assistant" else '🤠'
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])
    st.markdown('</div>', unsafe_allow_html=True)

else:
    # Placeholder when there are no messages
    st.write("No chat history yet. Start a conversation by typing a message.")

# Function to generate chat responses
def generate_chat_responses(chat_completion) -> Generator[str, None, None]:
    for chunk in chat_completion:
        if chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content

# Handle new chat input
if prompt := st.chat_input("What do you want to ask?"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar='🤠'):
        st.markdown(prompt)

    try:
        chat_completion = client.chat.completions.create(
            model=model_option,
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            max_tokens=max_tokens,
            stream=True
        )
        # Use the generator function with st.write stream
        with st.chat_message("assistant", avatar="✨"):
            chat_responses_generator = generate_chat_responses(chat_completion)
            full_response = st.write_stream(chat_responses_generator)
    except Exception as e:
        st.error(e, icon="🚨")
    
    # Append the full response to session_state.messages
    if isinstance(full_response, str):
        st.session_state.messages.append({"role": "assistant", "content": full_response})
    else:
        combined_response = "\n".join(str(item) for item in full_response)
        st.session_state.messages.append({"role": "assistant", "content": combined_response})
