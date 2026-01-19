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
def get_new_data():
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
    credentials = get_service_account_credentials(st.secrets['service_account_credentials'])
    gc = gspread.authorize(credentials)
    sh = gc.open_by_url("https://docs.google.com/spreadsheets/d/1Z4a8thj-ls1nR6f-IPeVsynhyjraKHqK-C586hDLEGo/edit?gid=0#gid=0")
    worksheet = sh.get_worksheet(0)

    # clear all content
    worksheet.clear()

    # update with values from streamlit
    worksheet.update(
        values=[df.columns.values.tolist()] + df.values.tolist(),
        range_name="A1"
    )







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
                get_new_data()

        st.title('Email Whitelist')
        st.info('Freely add or remove emails from the whitelist. Once done click **Submit Changes** to push update.')

        # load df - after cache refresh
        
        whitelist_df = load_dataframe()

        
        updated_whitelist_df = st.data_editor(
            data=whitelist_df,
            hide_index=True,
            num_rows='dynamic'
        )

        st.button(
            'Submit Changes',
            on_click=save_to_gsheets,
            args=[updated_whitelist_df]
        )

        




if __name__ == "__main__":
    user_access_page()