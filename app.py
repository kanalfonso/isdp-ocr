import streamlit as st
import yaml

def main():
    """
    Main function to control the Streamlit app workflow.

    If credentials are not found, it directs the user to 
    the authentication page (`auth_page`). Otherwise, it proceeds to the 
    newsblast page. (`newsblast`).

    """


    st.set_page_config(layout="wide", page_title='ISDP OCR Tool', page_icon='💼')
    
    logout_page = st.Page('pages/logout_page.py', title='Log out', icon=":material/logout:")
    login_page = st.Page('pages/login_page.py', title='Login')
    ocr_page = st.Page('pages/ocr_page.py', title='OCR (Create)', icon='📑')
    ocr_page_2 = st.Page('pages/ocr_page_v2.py', title='OCR (Create) 2', icon='📑')
    submissions_page = st.Page('pages/submissions_page.py', title='Submissions (Read, Predict, Update, Delete)', icon='💾')
    connection_page = st.Page('pages/connection_page.py', title='Connect to Snowflake', icon='❄️')
    
    # with open('config.yaml', "r") as f:
    #     config = yaml.safe_load(f)

    # if "credentials" in st.session_state and st.session_state['email'] in config.get('email_whitelist', []):
    #     pg = st.navigation([ocr_page, logout_page])
    
    # else:
    #     pg = st.navigation([login_page])
    
    pg = st.navigation([connection_page, ocr_page, ocr_page_2, submissions_page, logout_page])
    pg.run()
    

if __name__ == "__main__":
    main()