import streamlit as st
import sys, os

st.set_page_config(page_title="Nutri-Bot | SnapDiet", layout="wide")

try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
except Exception:
    pass

from utils.sidebar import render_sidebar
from utils.ui_theme import render_hero
from utils.db import add_chat_message, clear_chat_history
from utils.ai_engine import nutribot_chat

render_sidebar()

if st.session_state.get('user_profile') is None:
    st.switch_page("app.py")

render_hero("Nutri-Bot 🤖", "Your personal 24/7 AI Nutritionist. Ask anything about Indian diets, recipes, or your health.")

# Clear chat history every time the user logs in or refreshes the page
if 'chat_history' not in st.session_state:
    clear_chat_history()
    st.session_state.chat_history = []

col_c1, col_c2 = st.columns([6, 1])
with col_c2:
    if st.button("🗑️ Clear Chat", use_container_width=True):
        clear_chat_history()
        st.session_state.chat_history = []
        st.rerun()

# Display chat history
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about Indian diets or recipes..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Save to DB and state
    add_chat_message("user", prompt)
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # Stream the response instantly token-by-token
            response = st.write_stream(nutribot_chat(st.session_state.chat_history[:-1], prompt))
    
    # Save to DB and state
    add_chat_message("assistant", response)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    st.rerun()
