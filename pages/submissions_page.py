# note callback executes before script re-run when clicking on widget

import streamlit as st
import pandas as pd

# Backend
def persist_key(key):
    """
    Persists latest CRUD operation selection even when switching to different pages
    """
    st.session_state[key] = st.session_state['_' + key] 


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
        'Read': 0,
        'Predict': 1,
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




def read_page():
    """
    UI when user chooses `Read` as the selected CRUD operation
    """
    st.title('View Records')

    st.dataframe(st.session_state.submissions_df, hide_index=True)



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




def delete_page():
    """
    UI when user chooses `Delete` as the selected CRUD operation
    """
    st.title('Delete a Record')


    container = st.container()

    if st.session_state.get('is_successful_delete') and st.session_state.get('_ids_to_delete'):
        container.success(f'Successfully deleted record(s) with ID(s): {st.session_state._ids_to_delete}')

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





def predict_page():
    """
    UI when user chooses `Predict` as the selected CRUD operation
    """
    st.title('Predict Spam Type of Records')

    container = st.container()





def main():

    ### Session state variables
    if 'submissions_df' not in st.session_state:
        st.session_state['submissions_df'] = pd.DataFrame()

    ###### Sidebar ######
    sidebar_ui()
    
    
    ###### Main Page ######
    




    if len(st.session_state.submissions_df) > 0:
        if st.session_state._selected_crud_operation == 'Read':
            read_page()

        elif st.session_state._selected_crud_operation == 'Update':
            update_page()
        
        elif st.session_state._selected_crud_operation == 'Predict':
            predict_page()
        
        elif st.session_state._selected_crud_operation == 'Delete':
            delete_page()




    # When there are no records in the session state df, show warning message
    else:
        # container for notifications
        container = st.container()

        # Message to show after delete all has been executed
        if st.session_state.get('is_successful_delete_all'):
            st.session_state.is_successful_delete_all = False
            container.warning(
                "All records have been deleted."
                "\n\nPlease add record in the **OCR (Create)** Page"
            )


        elif st.session_state.get('is_successful_delete'):
            st.session_state.is_successful_delete = False
            container.warning(
                f"Successfully deleted the record(s) with ID(s): {st.session_state._ids_to_delete}."
                "\n\nNo records remain. Please add new records in the **OCR (Create)** page."
            )

        
        else:
            container.warning(
                "No records found." 
                "\n\nPlease add record in the **OCR (Create)** Page"
            )


    st.write(st.session_state)



if __name__ == '__main__':
    main()