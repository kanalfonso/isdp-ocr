import streamlit as st
from pages.no_records_page import no_records_page 
# helper funcs
from utils.streamlit.general_helpers import persist_key, load_config

def read_page(COLUMN_CONFIG: dict):
    """
    UI when user chooses `Read` as the selected CRUD operation
    """
    
    st.title('Read Records')

    if st.session_state.submissions_df.empty:
        no_records_page()
        
        # Need to end with `return` so won't load the empty table
        return
    
    st.info(
        "ℹ️ This table is read-only. Choose a CRUD operation from the sidebar to create, update, delete, or predict records."
    )

    # display dataframe if it has records
    st.dataframe(st.session_state.submissions_df, hide_index=True, column_config=COLUMN_CONFIG)



if __name__ == '__main__':
    config = load_config()
    COLUMN_CONFIG = config.get('column_config')
    read_page(COLUMN_CONFIG)