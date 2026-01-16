import streamlit as st
import yaml
import pandas as pd

def main():
    """
    Main function to control the Streamlit app workflow.

    If credentials are not found, it directs the user to 
    the authentication page (`auth_page`). Otherwise, it proceeds to the 
    newsblast page. (`newsblast`).

    """

    ### Session state variables to instantiate
    # For first run when submissions_df doesn't exist yet
    if 'submissions_df' not in st.session_state:
        st.session_state['submissions_df'] = pd.DataFrame()


    st.set_page_config(layout="wide", page_title='ISDP OCR Tool', page_icon='💼')
    
    logout_page = st.Page('pages/logout_page.py', title='Log out', icon=":material/logout:")
    login_page = st.Page('pages/login_page.py', title='Login')
    submissions_page = st.Page('pages/submissions_navigation.py', title='Submissions (Create, Read, Update, Delete)', icon='💾')
    predict_page = st.Page('pages/predict_page.py', title='Generate Spam Tag', icon='🤖')
    connection_page = st.Page('pages/connection_page.py', title='Connect to Snowflake', icon='❄️')
    
    # with open('config.yaml', "r") as f:
    #     config = yaml.safe_load(f)

    # if "credentials" in st.session_state and st.session_state['email'] in config.get('email_whitelist', []):
    #     pg = st.navigation([ocr_page, logout_page])
    
    # else:
    #     pg = st.navigation([login_page])
    
    
    pg = st.navigation([connection_page, submissions_page, predict_page, logout_page])
    pg.run()
    
    st.write(st.session_state)

if __name__ == "__main__":
    main()