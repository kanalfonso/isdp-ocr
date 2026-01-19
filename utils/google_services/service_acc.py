# Google Libraries
from google.oauth2 import service_account
from google.oauth2.service_account import Credentials

# Streamlit Libraries
import streamlit as st


def get_service_account_credentials(service_account_credentials: dict) -> Credentials:    
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    
        credentials = service_account.Credentials.from_service_account_info(service_account_credentials, scopes=scopes)

        return credentials
    
    except Exception as e:
        return(f"An error occurred: {e}")

def main():
    credentials = get_service_account_credentials(st.secrets['service_account_credentials'])

    # print(credentials)
    # print(type(credentials))

if __name__ == '__main__':
    main()