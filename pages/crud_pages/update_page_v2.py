import pandas as pd
import streamlit as st

@st.dialog("Edit Records")
def update_popup(edited_df):
    st.write(
        f"Are you sure you want to edit the submissions?"
        "\n\nThis action **cannot be undone**."
    )

    if st.button('Submit'):

        # Set as new dataframe
        st.session_state.submissions_df = edited_df.copy()

        st.session_state.is_successful_update = True
        st.rerun()


def update_page_v2():

    st.title('Update a Record')

    container = st.container()


    container.info(
            "ℹ️ Double-click any cell to make changes. ID fields are read-only."
    )


    if st.session_state.get('is_successful_update'):
        container.success('Successful edit')
        st.session_state.is_successful_update = False

    data_df = st.session_state.submissions_df 


    edited_df = st.data_editor(
        data_df,
        column_config={
            
            # keys are col names
            "id": st.column_config.TextColumn(
                label="ID", # display column name
                disabled=True
            ),

            "content": st.column_config.TextColumn(
                label="Content", 
            ),

            "spam_tag": st.column_config.SelectboxColumn(
                label="Spam Tag",
                # help="The category of the app",
                # width="medium",
                options=[
                    "LOAN/SCAM/SPAM",
                    "P2P",
                    "COMMERCIAL",
                ],
            ),




        },
        hide_index=True,
    )

    
    if st.button("Submit Changes"):

        # exactly the same
        if edited_df.equals(st.session_state.submissions_df):
            container.warning('Nothing changed. Your table is the same as before.')
        else:
            update_popup(edited_df)


if __name__ == '__main__':
    update_page_v2()