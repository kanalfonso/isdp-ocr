# pip install snowflake-snowpark-python
from snowflake.snowpark import Session
from cryptography.hazmat.primitives import serialization
from snowflake.snowpark import Session
import streamlit as st
import pandas as pd


def load_sf_private_key():
    """Loads private key of snowflake service account"""

    # Retrieve from streamlit secrets file
    PASSPHRASE = st.secrets['snowflake_service_account']['private_key_passphrase']
    PRIVATE_KEY_PATH = st.secrets['snowflake_service_account']['private_key_path']
    
    # Open private key file
    with open(PRIVATE_KEY_PATH, "rb") as key_file:
        p_key = serialization.load_pem_private_key(
            key_file.read(),
            password=PASSPHRASE.encode(),
        )
    
    # Convert private bytes to bytes
    pkb = p_key.private_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption())
    
    return pkb


def create_session_using_sa():
    """Creates session using service account thru pkb"""
    
    pkb = load_sf_private_key()

    connection_parameters = {
        'account': 'globe-cssg.privatelink',
        'user': 'SF_DB_PRD_APP_OCR',
        'role': 'SA_FR_SF_DB_PRD_APP_OCR',
        'authenticator': 'SNOWFLAKE_JWT',
        'private_key': pkb,
        'warehouse': 'PRD_VWH_EDS_CDA_ENT_XS',
        'database': 'GRP_SBX_ISDP',
        'schema': 'OCR',
        'query_tag': f"Enterprise - ISDP OCR Tool Dev - {st.session_state['email']}"
    }

    session = Session.builder.configs(connection_parameters).create()

    return session


def query_results(session, query):
    results = session.sql(query).to_pandas()
    session.close()

    return results 


def upload_data_to_sf(
    session: Session, 
    df: pd.DataFrame, 
    table_name="STOPSPAM_SUBMISSIONS",
    database="GRP_SBX_ISDP",
    schema="OCR"
):
    """
    Upload dataframe to Snowflake    
    """

    # Upload dataframe to SF table
    session.write_pandas(
        df,
        table_name=table_name,
        database=database,
        schema=schema
    )

    # Closing session
    session.close()



def main():
    pass
    # print("1) Creating session...\n")
    # session = create_session_using_sa()

    # print("2) Querying results...\n")
    # query = """
    # SELECT *
    # FROM GRP_SBX_ISDP.OCR.STOPSPAM_SUBMISSIONS
    # ORDER BY submission_time
    # LIMIT 2
    # """
    
    # print(query_results(session, query))


if __name__ == '__main__':
    main()