# note callback executes before script re-run when clicking on widget

import streamlit as st
import pandas as pd


def main():

    ### Session state variables
    if 'submissions_df' not in st.session_state:
        st.session_state['submissions_df'] = pd.DataFrame()



    ### CONFIGS for the page ###
    CRUD_MAPPING = {
        'Read': 0,
        'Predict': 1,
        'Update': 2,
        'Delete': 3
    }

    CRUD_OPTIONS = [option for option in CRUD_MAPPING.keys()]





    def keep_perma_key(key):
        """
        Callback function that stores widget key permanently to session state
        Keeps latest widget selection even when widget is not rendered 
        """
        st.session_state[key] = st.session_state['_' + key] 





    ## Sidebar
    with st.sidebar:

        selected_crud_operation = st.selectbox(
            label='Choose Operation',
            options=CRUD_OPTIONS,
            key='_selected_crud_operation',
            on_change=keep_perma_key,
            args=['selected_crud_operation'],

            # By default set option to 0 (Read) on first script run
            # Succeeding runs will refer to value of `selected_crud_operation`
            index=CRUD_MAPPING[st.session_state.selected_crud_operation] if 'selected_crud_operation' in st.session_state else 0
        )




    ###### Main Page ######
    st.title('Submissions')
    
    # container for notifications
    container = st.container()




    if len(st.session_state.submissions_df) > 0:
        
        if selected_crud_operation == 'Read':
            st.dataframe(st.session_state.submissions_df)
        elif selected_crud_operation == 'Update':
            st.write('Update')
        elif selected_crud_operation == 'Predict':
            st.write('Predict')
        elif selected_crud_operation == 'Delete':
            st.write('Delete')




    # When there are no records in the session state df, show warning message
    else:
        container.warning('No records found. Please add record in the **OCR (Create)** Page')


    st.write(st.session_state)
if __name__ == '__main__':
    main()