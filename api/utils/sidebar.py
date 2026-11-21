import streamlit as st
import os
from utils.ui_theme import inject_theme
from utils.db import clear_chat_history

def render_sidebar():
    # Inject the premium global theme
    inject_theme()
    
    with st.sidebar:
        # A sleek, modern sidebar header
        st.markdown("""
        <div style='text-align: center; margin-bottom: 20px;'>
            <h1 style='background: linear-gradient(90deg, #34d399, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; font-size: 2.5rem; font-weight: 800;'>SnapDiet 🍏</h1>
            <p style='color: #94a3b8; margin: 0; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase;'>National Nutrition Week 2026</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
        
        # --- LOGOUT ---
        if 'user_profile' in st.session_state and st.session_state.user_profile is not None:
            if st.button("🚪 Logout", use_container_width=True, type="primary"):
                st.session_state.user_profile = None
                clear_chat_history()
                st.session_state.chat_history = []
                st.switch_page("app.py")
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
        
        # --- GLOBAL CHATBOT ---
        st.page_link("pages/6_chatbot.py", label="💬 Ask Nutri-Bot", icon="🤖")
                
        st.markdown("<hr style='border-color: rgba(255,255,255,0.1); margin: 20px 0 20px 0;'>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='font-size: 1.1rem; color: #e2e8f0; margin-bottom: 15px;'>🤖 AI Engine</h3>", unsafe_allow_html=True)
        
        if "gemini_api_key" not in st.session_state or not st.session_state.gemini_api_key:
            st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
            if not st.session_state.gemini_api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                st.session_state.gemini_api_key = st.secrets["GEMINI_API_KEY"]
                os.environ["GEMINI_API_KEY"] = st.session_state.gemini_api_key
            
        if st.session_state.gemini_api_key:
            st.markdown("""
            <div style='background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); padding: 12px; border-radius: 12px; margin-bottom: 15px;'>
                <div style='color: #34d399; font-weight: 600; display: flex; align-items: center; gap: 8px;'>
                    <span>✅</span> AI Engine Active
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Reset / Change API Key", use_container_width=True):
                st.session_state.gemini_api_key = ""
                if "GEMINI_API_KEY" in os.environ:
                    del os.environ["GEMINI_API_KEY"]
                st.rerun()
        else:
            api_key = st.text_input(
                "Gemini API Key", 
                type="password", 
                placeholder="Paste API Key here...",
                help="Required to unlock AI nutrition analysis. Without it, mock data will be used."
            )
            
            if api_key:
                st.session_state.gemini_api_key = api_key
                os.environ["GEMINI_API_KEY"] = api_key
                st.rerun()
            else:
                st.markdown("""
                <div style='background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 12px; border-radius: 12px; margin-bottom: 15px;'>
                    <div style='color: #fbbf24; font-size: 0.9rem;'>
                        ⚠️ AI Offline. Using mock data.
                    </div>
                </div>
                """, unsafe_allow_html=True)
