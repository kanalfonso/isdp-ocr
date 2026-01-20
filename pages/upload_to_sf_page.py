import streamlit as st
from pages.no_records_page import no_records_page
import time

def upload_to_sf_page():
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
            hide_index=True
        )


    else:
        container = st.container()

        container.info(
            "ℹ️ Clicking **Submit** uploads your records to a dedicated Snowflake table."
            "\n\nThis action cannot be undone. Updates or deletions must be done directly in Snowflake."
        )

        spinner_placeholder = st.empty()

        # display dataframe
        st.dataframe(
            st.session_state.submissions_df,
            hide_index=True
        )


        if st.button("Submit"):
            with spinner_placeholder.spinner("Uploading data to Snowflake...."):
                time.sleep(2)
                container.success("Submission uploaded to Snowflake!")

if __name__ == '__main__':
    upload_to_sf_page()