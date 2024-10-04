import streamlit as st
from typing import Generator
from groq import Groq

st.set_page_config(page_icon="💬", layout="centered", page_title="Groq Chat")

st.subheader("Groq Chat Streamlit App", divider="rainbow", anchor="false")
