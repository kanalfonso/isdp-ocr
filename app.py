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

    if 'create_text_results' not in st.session_state:
        st.session_state['create_text_results'] = {}


    if "file_id_to_metadata" not in st.session_state:
        st.session_state.file_id_to_metadata = {}

    if "create_text_results" not in st.session_state:
        st.session_state.create_text_results = {}


    st.set_page_config(layout="wide", page_title='ISDP OCR Tool', page_icon='💼')
    
    logout_page = st.Page('pages/logout_page.py', title='Log out', icon=":material/logout:")
    login_page = st.Page('pages/login_page.py', title='Login')
    user_access_page = st.Page('pages/user_access_page.py', title='User Access', icon='👨🏻‍💻')
    crud_page = st.Page('pages/crud_navigation.py', title='Submissions (Create, Read, Update, Delete)', icon='💾')
    predict_page = st.Page('pages/predict_page.py', title='Generate Spam Tag', icon='🤖')
    upload_to_sf_page = st.Page('pages/upload_to_sf_page.py', title='Upload to Snowflake', icon='❄️')
    # connection_page = st.Page('pages/connection_page.py', title='Connect to Snowflake', icon='❄️')
    
    with open('config.yaml', "r") as f:
        config = yaml.safe_load(f)



    ## LOGIN LOGIC ###
    # email whitelist logic
    if "credentials" in st.session_state and st.session_state['email'] in config.get('email_whitelist', []):

        pages = {
            "Records": [
                crud_page, 
                predict_page,
                upload_to_sf_page
            ],
            
            "Account": [
                user_access_page, 
                logout_page
            ]
        }

        pg = st.navigation(pages)
    
    else:
        pg = st.navigation([login_page])
    
    ## LOGIN LOGIC ###




    # pg = st.navigation(
    #     [
    #         # connection_page, 
    #         # login_page,
    #         crud_page, 
    #         predict_page, 
    #         upload_to_sf_page,
    #         logout_page
    #     ]
    # )

    if pg != crud_page:
        st.session_state.create_text_results = {}
        st.session_state.file_id_to_metadata = {}
    
    
    pg.run()
    
    st.write(st.session_state)

if __name__ == "__main__":
    main()