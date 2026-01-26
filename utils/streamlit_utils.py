import streamlit as st

# Backend
def persist_key(key):
    """
    Persists key across different pages
    """
    st.session_state[key] = st.session_state['_' + key] 

def persist_create_text_fields(key):
    st.session_state.create_text_results[key] = st.session_state['_' + key] 