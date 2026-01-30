import streamlit as st
from pages.no_records_page import no_records_page

# helper funcs
from utils.streamlit.general_helpers import load_config

### Pop-up message when `Delete entry` has been clicked ### 
@st.dialog('Confirm Deletion')
def delete_ids_popup():

    st.session_state._ids_to_delete = st.session_state._edited_df.loc[
        st.session_state._edited_df["to_delete"] == True,
        "id"
    ].tolist()


    st.write(
        f"Are you sure you want to delete the following entries, IDs: {st.session_state._ids_to_delete}? "
        "\n\nThis action **cannot be undone**."
    )


    if st.button('Submit'):

        # Remove the passed id from the dataframe
        st.session_state.submissions_df = (
            st.session_state.submissions_df[
                ~st.session_state.submissions_df["id"].isin(st.session_state._ids_to_delete)
            ]
        )

        st.session_state.is_successful_delete = True
        st.rerun()



def delete_page(COLUMN_CONFIG):
    """
    UI when user chooses `Delete` as the selected CRUD operation
    """
    st.title('Delete Records')

    container = st.container()


    # Last action wasn't delete and table is empty
    if not st.session_state.get('is_successful_delete') and st.session_state.submissions_df.empty:
        no_records_page()
        
        # Need to end with `return` so won't load the empty table
        return

    else:
        container.info(
            "ℹ️ Select records to delete using the checkboxes, or clear everything with **Delete All**."
            "\n\nDeleted records cannot be recovered."
        )


    # After delete and no records remain show this notification
    if st.session_state.get('is_successful_delete') and st.session_state.submissions_df.empty:
        st.session_state.is_successful_delete = False
        container.success(
            f"✅ Successfully deleted the record(s) with ID(s): {st.session_state._ids_to_delete}."
            "\n\nNo records remain. Please add new records by selecting the **Create** Operation."
        )

        # Need to end with `return` so won't load the empty table
        return



    # When you delete all records uing `Delete All`
    if st.session_state.get('is_successful_delete_all'):
        st.session_state.is_successful_delete_all = False
        container.success(
            "✅ All records have been deleted."
            "\n\nPlease add new records by selecting the **Create** Operation."
        )

        # Need to end with `return` so won't load the empty table
        return
    


    # After delete and there are still records remaining
    if st.session_state.get('is_successful_delete') and not st.session_state.submissions_df.empty:
        container.success(f'✅ Successfully deleted record(s) with ID(s): {st.session_state._ids_to_delete}')

        # set back to False immediately so the notifcation goes away
        st.session_state.is_successful_delete = False



    submissions_df = st.session_state.submissions_df.copy()

    # coluumn for tickbox widget
    submissions_df['to_delete'] = False

    edited_df = st.data_editor(
        submissions_df,
        column_config=COLUMN_CONFIG,
        hide_index=True
    )

    st.session_state._edited_df = edited_df




    if st.button('Delete'):

        if st.session_state._edited_df['to_delete'].any():

            # triggers `st.session_state.is_successful_delete`
            delete_ids_popup()

        # if no row selected to delete
        else:
            container.error("⚠️ No IDs selected. Please choose **at least one ID** to delete.")


if __name__ == '__main__':
    config = load_config()

    COLUMN_CONFIG = config.get('column_config')

    delete_page(COLUMN_CONFIG)
