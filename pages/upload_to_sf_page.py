import streamlit as st
from pages.no_records_page import no_records_page
import time

from datetime import datetime


# Snowflake functions
from utils.snowflake_utils import create_session_using_sa, upload_data_to_sf

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
            "ℹ️ Clicking **Submit** uploads your records to a Snowflake table."
            "\n\nThis action cannot be undone. Updates or deletions must be done directly in Snowflake if needed."
        )
        
        spinner_placeholder = st.empty()
        
        if st.session_state.get('confirm_sf_upload'):
            with spinner_placeholder.spinner("Creating Snowflake session..."):
    
                # Create session
                session = create_session_using_sa()
                time.sleep(2)

            with spinner_placeholder.spinner("Uploading data to Snowflake..."):
                
                # Upload data to snowflake and closes session afterwards
                df_to_upload = st.session_state.submissions_df.copy()
                
                # Add col for email
                df_to_upload['email'] = st.session_state.email

                # Add col for date submitted
                dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df_to_upload['submission_time'] = dt_str


                # standardize upper case for all cols
                df_to_upload.columns = df_to_upload.columns.str.upper()
                
                # reorder column before submission
                COL_ORDER = ['EMAIL', 'SUBMISSION_TIME', 'SENDER', 'SMS_CONTENT', 'SPAM_TAG']
                df_to_upload = df_to_upload[COL_ORDER]
    
                upload_data_to_sf(session, df_to_upload)
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

