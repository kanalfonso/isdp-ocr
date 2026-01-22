import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import gspread
import time

# helper
from utils.google_services.service_acc import get_service_account_credentials

@st.cache_data(show_spinner="Fetching whitelist records via API request...")
def load_dataframe():
    """
    Loads GSheets from secrets.toml
    """
    conn = st.connection("gsheets", type=GSheetsConnection)

    # read() method returns a dataframe
    df = conn.read()

    time.sleep(2)


    return df.reset_index(drop=True)



# backend logic for refreshing data
def clear_cache():
    """
    Trigger data refresh to get up-to-date info
    """

    st.cache_data.clear()
    st.rerun()


# backend logic for rewriting table in gsheets
def save_to_gsheets(df: pd.DataFrame):
    """
    Overwrite data to Gsheets 
    """
    # credentials = get_service_account_credentials(st.secrets['service_account_credentials'])
    # gc = gspread.authorize(credentials)
    # sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Z4a8thj-ls1nR6f-IPeVsynhyjraKHqK-C586hDLEGo/edit?gid=0#gid=0")
    # worksheet = sh.get_worksheet(0)

    # # clear all content
    # worksheet.clear()

    # # update with values from streamlit
    # worksheet.update(
    #     values=[df.columns.values.tolist()] + df.values.tolist(),
    #     range_name="A1"
    # )


@st.dialog('Confirm Changes')
def submit_popup(df):
    st.write(
        f"Are you sure you want to update the whitelist"
        "\n\nThis action **cannot be undone**."
    )

    if st.button('Submit'):
        save_to_gsheets(df)
        st.session_state.is_successful_whitelist_update = True
        st.rerun()



def user_access_page():
    """
    UI for user access page
    """

    # init state
    if "show_whitelist" not in st.session_state:
        st.session_state.show_whitelist = False


    # ---- BEFORE CLICK ----
    if not st.session_state.show_whitelist:
        st.info(
            "**NOTE**: Clicking this button will run an API request to display Email Whitelist"
            "\n\nCheck file [here](https://docs.google.com/spreadsheets/d/1Z4a8thj-ls1nR6f-IPeVsynhyjraKHqK-C586hDLEGo/edit?gid=0#gid=0) before opening"
        )

        if st.button("Open Whitelist?"):
            st.session_state.show_whitelist = True
            st.rerun()




    # ---- AFTER CLICK ----
    else:

        with st.sidebar:
            if st.button("Refresh Data"):
                clear_cache()

        st.title('Email Whitelist')
        st.info('ℹ️ Freely add or remove emails from the whitelist. Once done click **Submit Changes** to push update.')

        container = st.container()



        if st.session_state.get('is_successful_whitelist_update'):
            container.success("✅ Successfully updated the whitelist!")
            st.session_state.is_successful_whitelist_update = False


            # refresh to clear cache
            clear_cache()


        # API request to load latest dataframe after update
        whitelist_df = load_dataframe()

        
        updated_whitelist_df = st.data_editor(
            data=whitelist_df,
            hide_index=True,
            num_rows='dynamic'
        )

        if st.button('Submit Changes'):
            submit_popup(updated_whitelist_df)
        




if __name__ == "__main__":
    user_access_page()