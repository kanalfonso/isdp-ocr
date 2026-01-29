import streamlit as st
from pages.no_records_page import no_records_page
import time
import yaml

from utils.snowflake_utils import create_sf_session, upload_data_to_sf

# helper funcs
from utils.streamlit.general_helpers import load_config

@st.dialog("Confirming Upload")
def submit_popup():
    st.write(
        "Are you sure you want to upload this table to Snowflake?"
        "\n\nThis action **cannot be undone**."
    )

    if st.button("Confirm"):
        st.session_state.confirm_sf_upload = True
        st.rerun()



def upload_to_sf_page(COLUMN_CONFIG):
    st.title('Upload to Snowflake')

    # Last action wasn't delete and table is empty
    if st.session_state.submissions_df.empty:
        no_records_page()
        
        # Need to end with `return` so won't load the empty table
        return

    # at least one spam tag value is `None`
    if st.session_state.submissions_df['spam_tag'].isna().any():
        st.warning(
            "⛔ Your submissions contain AT LEAST one spam tag value that is blank"
            "\n\nPlease populate these in the **Generate Spam Tag** page before proceeding with upload"
        )

        st.dataframe(
            st.session_state.submissions_df,
            column_config=COLUMN_CONFIG,
            hide_index=True
        )


    else:
        container = st.container()

        container.info(
            "ℹ️ Clicking **Submit** uploads your records to a dedicated Snowflake table."
            "\n\nThis action cannot be undone. Updates or deletions must be done directly in Snowflake."
        )
        
        spinner_placeholder = st.empty()
        
        if st.session_state.get('confirm_sf_upload'):
            with spinner_placeholder.spinner("Creating Snowflake session..."):
    
                # Create session
                session = create_sf_session()
                time.sleep(2)

            with spinner_placeholder.spinner("Uploading data to Snowflake..."):
                
                # Upload data to snowflake and closes session afterwards
                df_to_upload = st.session_state.submissions_df[['sender', 'CONTENT', 'spam_tag']].copy()

                df_to_upload['USER_EMAIL'] = None
                df_to_upload['USER_TRANSACTION_DATE'] = None


                df_to_upload.columns = df_to_upload.columns.str.upper()
                upload_data_to_sf(session, df_to_upload)
                time.sleep(2)

            with spinner_placeholder.spinner("Closing session..."):
                # Close session
                session.close()
                time.sleep(2)


            st.session_state.confirm_sf_upload = False
            container.success("✅ Submission uploaded to Snowflake!")


        # display dataframe
        st.dataframe(
            st.session_state.submissions_df,
            column_config=COLUMN_CONFIG,
            hide_index=True
        )


        st.button(
            "Submit",
            on_click=submit_popup
        )
                

if __name__ == '__main__':
    config = load_config()

    COLUMN_CONFIG = config.get('column_config')

    upload_to_sf_page(COLUMN_CONFIG)

