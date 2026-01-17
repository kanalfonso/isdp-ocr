import streamlit as st

### Pop-up message when `Delete entry` has been clicked ### 
@st.dialog('Confirm Deletion')
def delete_ids_popup(_ids_to_delete):
    st.write(
        f"Are you sure you want to delete the following entries, IDs: {st.session_state._ids_to_delete}? "
        "\n\nThis action **cannot be undone**."
    )


    if st.button('Submit'):

        # Remove the passed id from the dataframe
        st.session_state.submissions_df = (
            st.session_state.submissions_df[
                ~st.session_state.submissions_df["id"].isin(_ids_to_delete)
            ]
        )

        st.session_state.is_successful_delete = True
        st.rerun()



def delete_page():
    """
    UI when user chooses `Delete` as the selected CRUD operation
    """
    st.title('Delete Records')


    container = st.container()

    if st.session_state.get('is_successful_delete') and st.session_state.get('_ids_to_delete'):
        container.success(f'✅ Successfully deleted record(s) with ID(s): {st.session_state._ids_to_delete}')

        # set back to False immediately so the notifcation goes away
        st.session_state.is_successful_delete = False


    # Enter ID
    st.multiselect(
        "Input IDs", 
        key='_ids_to_delete',
        options=st.session_state.submissions_df["id"].tolist(),
        placeholder="Select one or more IDs to delete"
    )


    st.dataframe(st.session_state.submissions_df, hide_index=True)

    
    if st.button('Delete'):

        if len(st.session_state._ids_to_delete) == 0:
            container.error("⚠️ No IDs selected. Please choose **at least one ID** to delete.")

        else:
            # Redirects to pop-up message above
            delete_ids_popup(st.session_state._ids_to_delete)


if __name__ == '__main__':
    delete_page()
