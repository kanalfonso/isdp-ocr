import streamlit as st

def read_page():
    """
    UI when user chooses `Read` as the selected CRUD operation
    """
    st.title('Read Records')


    st.info(
        "ℹ️ This table is read-only. Choose a CRUD operation from the sidebar to create, update, delete, or predict records."
    )

    st.dataframe(st.session_state.submissions_df, hide_index=True)


if __name__ == '__main__':
    read_page()