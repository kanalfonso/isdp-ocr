import streamlit as st

def read_page():
    """
    UI when user chooses `Read` as the selected CRUD operation
    """
    st.title('View Records')

    st.dataframe(st.session_state.submissions_df, hide_index=True)


if __name__ == '__main__':
    read_page()