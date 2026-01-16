import streamlit as st



def edit_record(updated_data: dict, form_container):
    """
    Logic that handles form submission entry
    """

    # call our current submission df
    df = st.session_state.submissions_df

    # get the updates the user pushes
    record_id, updated_content, updated_spam_tag = updated_data['id'], updated_data['content'], updated_data['spam_tag']
    
    # cast as str
    updated_content = str(updated_content)

    # get the current entry of the record ID
    current_content, current_spam_tag = (
        df.loc[df['id'] == record_id, ['content', 'spam_tag']]
        .iloc[0]
    )

    # cast as str
    current_content = str(current_content)
    

    # if content field is left blank
    if updated_content.strip() == "":
        form_container.error('Please do not leave the **Content** field blank!')
    

    # if no changes have been made from the current and updated
    elif (current_content.strip() == updated_content.strip()) and (current_spam_tag == updated_spam_tag):
        form_container.warning('No changes have been made.')


    # successful entry
    else:
        # id masking
        id_mask = df['id'] == record_id

        df.loc[id_mask, 'content'] = updated_content
        df.loc[id_mask, 'spam_tag'] = updated_spam_tag

        # make this as the new dataframe
        st.session_state.submissions_df = df

        st.session_state.is_successful_edit = True
        st.rerun()



### Pop-up message when `Delete entry` has been clicked ### 
@st.dialog('Edit Selected Record')
def edit_popup():

    # for notifications
    form_container = st.container()


    SPAM_TAG_OPTIONS = ['LOAN/SCAM/SPAM', 'COMMERCIAL', 'P2P']

    SPAM_TAG_MAPPING = {
        'LOAN/SCAM/SPAM': 0,
        'COMMERCIAL': 1,
        'P2P': 2
    }


    # Current values
    df  = st.session_state.submissions_df
    selected_id = st.session_state._id_to_edit
    


    # string -> SMS content
    current_content = str(df.loc[df['id'] == selected_id, 'content'].iloc[0])

    # string -> LOAN/SCAM/SPAM, COMMERCIAL, P2P
    current_spam_tag = df.loc[df['id'] == selected_id, 'spam_tag'].iloc[0]



    # index
    if current_spam_tag is not None:
        current_spam_tag_index = SPAM_TAG_MAPPING[current_spam_tag]
    else:
        current_spam_tag_index = None

    

    

    with st.form('edit_form'):
        
        st.text_input(
            "ID", 
            placeholder='id', 
            value=st.session_state._id_to_edit, 
            disabled=True
        )


        updated_content = st.text_input(
            "Content", 
            value=current_content
        )
        

        updated_spam_tag = st.selectbox(
            "Spam Tag", 
            options=SPAM_TAG_OPTIONS,
            index=current_spam_tag_index
        )
            

        if st.form_submit_button('Submit'):
            
            updated_data = {
                'id': st.session_state._id_to_edit,
                'content': updated_content,
                'spam_tag': updated_spam_tag
            }

            # Logic that handles submitting a form entry
            edit_record(updated_data, form_container)
            






def update_page():
    """
    UI when user chooses `Update` as the selected CRUD operation
    """
    st.title('Update a Record')

    main_page_container = st.container()

    # Enter ID
    st.selectbox(
        "Input ID",
        options=st.session_state.submissions_df["id"].tolist(), 
        key='_id_to_edit',
        placeholder="Type a number..."
    )

    st.dataframe(st.session_state.submissions_df, hide_index=True)


    if st.button('Edit'):
        edit_popup()

    if st.session_state.get('is_successful_edit'):
        main_page_container.success(f'✅ Successfully edited the record with ID: {st.session_state._id_to_edit}')
        st.session_state.is_successful_edit = False



if __name__ == '__main__':
    update_page()