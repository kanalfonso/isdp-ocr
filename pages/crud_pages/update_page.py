import streamlit as st
from pages.no_records_page import no_records_page


@st.dialog("Confirm Update")
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




def update_page():

    st.title('Update Records')

    # Last action wasn't delete and table is empty
    if st.session_state.submissions_df.empty:
        no_records_page()
        
        # Need to end with `return` so won't load the empty table
        return
    
    container = st.container()

    container.info(
        "ℹ️ Double-click a cell to edit (ID fields are read-only). "
        "\n\nPress **Enter** or click outside the cell to register changes. "
        "\n\nThe **Submit Changes** button is only enabled when changes are detected."
    )


    if st.session_state.get('is_successful_update'):
        container.success('✅ Changes saved successfully')
        st.session_state.is_successful_update = False

    data_df = st.session_state.submissions_df 

    COLUMN_CONFIG ={
        "id": st.column_config.TextColumn(
                    label="ID", # display column name
                    disabled=True
        ),

        "sender": st.column_config.TextColumn(
            label="Sender", # display column name
            disabled=False
        ),

        "sms_content": st.column_config.TextColumn(
            label="SMS Content", # display column name
            disabled=False
        ),

        "spam_tag": st.column_config.SelectboxColumn(
            label="Spam Tag", # display column name
            disabled=False,
            options=[
                "LOAN/SCAM/SPAM",
                "P2P",
                "COMMERCIAL",
            ],
        )
    }

    edited_df = st.data_editor(
        data_df,
        column_config=COLUMN_CONFIG,
        hide_index=True,
    )


    # # True if edited_df != submission_df
    # has_changes = not edited_df.equals(st.session_state.submissions_df)

    
    if st.button("Submit Changes"):
        if edited_df.equals(st.session_state.submissions_df):
            container.error("⚠️ No changes detected. Please modify the data before submitting.")
        else:
            update_popup(edited_df)


if __name__ == '__main__':
    update_page()