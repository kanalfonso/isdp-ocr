import streamlit as st
import yaml

# Backend
def persist_key(key):
    """
    Persists key across different pages
    """
    st.session_state[key] = st.session_state['_' + key] 


@st.cache_resource
def load_config():
    with open('config.yaml', "r") as f:
        return yaml.safe_load(f)

