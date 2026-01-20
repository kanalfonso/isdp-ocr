import streamlit as st
from pages.no_records_page import no_records_page 


def read_page():
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
    st.dataframe(st.session_state.submissions_df, hide_index=True)



if __name__ == '__main__':
    read_page()