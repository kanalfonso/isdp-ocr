import streamlit as st

# Backend
def persist_key(key):
    """
    Persists key across different pages
    """
    st.session_state[key] = st.session_state['_' + key] 