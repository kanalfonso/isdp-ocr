import streamlit as st

def update_page():
    """
    UI when user chooses `Update` as the selected CRUD operation
    """
    st.title('Update a Record')

    container = st.container()

    # Enter ID
    st.number_input(
        "Input ID", 
        value=None, 
        placeholder="Type a number..."
    )

    st.dataframe(st.session_state.submissions_df, hide_index=True)



if __name__ == '__main__':
    update_page()