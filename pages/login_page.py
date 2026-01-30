# Standard Libraries
import yaml

# Google Libraries
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Streamlit Libraries
import streamlit as st
from streamlit_oauth import OAuth2Component

from utils.streamlit.general_helpers import load_whitelist

oauth_params = st.secrets['oauth_client_secret']


CLIENT_ID, CLIENT_SECRET = oauth_params["client_id"], oauth_params["client_secret"]
AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, REDIRECT_URI, REVOKE_ENDPOINT = oauth_params["auth_uri"], oauth_params["token_uri"], oauth_params["redirect_uris"][0], oauth_params['revoke_endpoint'] 

def get_user_email(credentials: Credentials) -> str:
    service = build('oauth2', 'v2', credentials=credentials)
    user_info = service.userinfo().get().execute()

    return user_info['email']


# OAuth authentication function
def oauth_authentication():
    try:
        EMAIL_WHITELIST = load_whitelist()

        oauth2 = OAuth2Component(CLIENT_ID, CLIENT_SECRET, AUTHORIZE_ENDPOINT, TOKEN_ENDPOINT, TOKEN_ENDPOINT, REVOKE_ENDPOINT)
        result = oauth2.authorize_button(
            name="Login with Google", 
            icon="https://www.google.com.tw/favicon.ico", 
            scope="openid email profile", 
            redirect_uri=REDIRECT_URI, 
            extras_params={"prompt": "consent", "access_type": "offline"},
            pkce='S256'
        )

        
        if result:
            credentials = Credentials(token=result['token']['access_token'],
                                      refresh_token=result['token']['refresh_token'],
                                      id_token=result['token']['id_token'],
                                      client_id=CLIENT_ID,
                                      client_secret=CLIENT_SECRET)
            
            st.session_state['credentials'] = credentials
            email = get_user_email(st.session_state.credentials)
            st.session_state['email'] = email

            # Check for email access
            if st.session_state['email'] in EMAIL_WHITELIST:
                st.rerun()
            else:
                st.warning(f"Access denied for {email}. You do not have the required privileges.", icon="🚫")


    except Exception as e:
        st.warning(f"{e}: An error occurred during authentication. Please try again.")

    # st.write(st.session_state)


if __name__ == "__main__":
    try:
        oauth_authentication()
    except Exception as e:
        st.error(f'**Unknown Error**: Please refresh browser or if issue persists, please reach out to the CDA - Enterprise Team.  \n\nError Message: {e}', icon='🚫')


