# note callback executes before script re-run when clicking on widget
import streamlit as st
import pandas as pd

# crud pages
from pages.crud_pages.batch_create_page import batch_create_page
from pages.crud_pages.read_page import read_page
from pages.crud_pages.update_page import update_page
from pages.crud_pages.delete_page import delete_page

# helper funcs
from utils.streamlit.general_helpers import persist_key, load_config



### Pop-up message when `Delete All` has been clicked ### 
@st.dialog('Confirm Deletion')
def delete_all():
    st.write(
        f"Are you sure you want to delete ALL entries?"
        "\n\nThis action **cannot be undone**."
    )


    if st.button('Submit'):
        # Reset to a blank dataframe
        st.session_state.submissions_df = pd.DataFrame()
        st.session_state.is_successful_delete_all = True
        st.rerun()



## Sidebar
def sidebar_ui():
    """
    Wrapper on sidebar UI for the Submission Page
    """
    ### CONFIGS for the page ###
    CRUD_MAPPING = {
        'Create': 0,
        'Read': 1,
        'Update': 2,
        'Delete': 3
    }

    CRUD_OPTIONS = [option for option in CRUD_MAPPING.keys()]


    ## Sidebar
    with st.sidebar:

        st.selectbox(
            label='Choose Operation',
            options=CRUD_OPTIONS,
            key='_selected_crud_operation',
            on_change=persist_key,
            args=['selected_crud_operation'],


            # By default set option to 0 (Read) on first script run
            # Succeeding runs will refer to value of `selected_crud_operation`
            index=CRUD_MAPPING[st.session_state.selected_crud_operation] if 'selected_crud_operation' in st.session_state else 0
        )

        if st.session_state.get('selected_crud_operation') == 'Delete':
            st.divider()

            if st.button('Delete All', disabled=True if st.session_state.submissions_df.empty else False):
                delete_all()



def main(MAX_FILES: int, ACCEPTED_IMAGE_FILE_TYPES: list, COLUMN_CONFIG: dict):

    ###### Sidebar ######
    sidebar_ui()
    ###### Sidebar ######
    
    

    ###### Main Page ######
    
    # if len(st.session_state.submissions_df) > 0:
    if st.session_state._selected_crud_operation == 'Create':
        batch_create_page(MAX_FILES, ACCEPTED_IMAGE_FILE_TYPES)

    elif st.session_state._selected_crud_operation == 'Read':
        read_page(COLUMN_CONFIG)

    elif st.session_state._selected_crud_operation == 'Update':
        update_page()
    
    elif st.session_state._selected_crud_operation == 'Delete':
        delete_page(COLUMN_CONFIG)


    # TODO: if page not in batch_create set file_id_to_metadata and create_text_results to {}
    if st.session_state._selected_crud_operation != 'Create':
        st.session_state.create_text_results = {}
        st.session_state.file_id_to_metadata = {}


if __name__ == '__main__':
    config = load_config()

    MAX_FILES = config.get('max_files')
    ACCEPTED_IMAGE_FILE_TYPES = config.get('accepted_image_file_types')
    COLUMN_CONFIG = config.get('column_config')
    main(MAX_FILES, ACCEPTED_IMAGE_FILE_TYPES, COLUMN_CONFIG)