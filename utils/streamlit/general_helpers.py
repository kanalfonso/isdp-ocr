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
    CONFIG_PATH = st.secrets['config']['config_file_path']
    with open(CONFIG_PATH, "r") as f:
        return yaml.safe_load(f)

@st.cache_resource
def load_whitelist():
    return st.secrets['whitelisted_users']['email_whitelist']