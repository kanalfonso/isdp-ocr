# note callback executes before script re-run when clicking on widget
import streamlit as st
import pandas as pd

# crud pages
from pages.crud_pages.create_page import create_page
from pages.crud_pages.read_page import read_page
from pages.crud_pages.update_page import update_page
from pages.crud_pages.delete_page import delete_page
# helper funcs
from utils.streamlit_utils import persist_key



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

            if st.button('Delete All'):
                delete_all()



def main():

    ###### Sidebar ######
    sidebar_ui()
    ###### Sidebar ######
    
    

    ###### Main Page ######
    
    if len(st.session_state.submissions_df) > 0:
        if st.session_state._selected_crud_operation == 'Create':
            create_page()

        elif st.session_state._selected_crud_operation == 'Read':
            read_page()

        elif st.session_state._selected_crud_operation == 'Update':
            update_page()
        
        elif st.session_state._selected_crud_operation == 'Delete':
            delete_page()




    # When there are no records in the session state df, show warning message
    else:

        if st.session_state._selected_crud_operation == 'Create':
            create_page()

        # Going to view any other crud operation: R, U or D
        else: 
            # container for notifications
            container = st.container()

            # When you delete all records uing `Delete All`
            if st.session_state.get('is_successful_delete_all'):
                st.session_state.is_successful_delete_all = False
                container.warning(
                    "All records have been deleted."
                    "\n\nPlease add new records by selecting the **Create** Operation."
                )

            # When you delete the last record using multiselect
            elif st.session_state.get('is_successful_delete'):
                st.session_state.is_successful_delete = False
                container.warning(
                    f"Successfully deleted the record(s) with ID(s): {st.session_state._ids_to_delete}."
                    "\n\nNo records remain. Please add new records by selecting the **Create** Operation."
                )

            
            else:
                container.warning(
                    "No records found." 
                    "\n\nPlease add new records by selecting the **Create** Operation."
                )



if __name__ == '__main__':
    main()