# pip install snowflake-snowpark-python
from snowflake.snowpark import Session
import pandas as pd

def create_sf_session(
    user: str = 'alfonso.kan@globe.com.ph',
    role: str = 'ROLE_AKAN',        
    warehouse: str = 'CSSG_CDA_WH_GENERAL'
):
    """
    Creates a Snowflake Session based on the connection parameters passed
    """

    connection_parameters = {
        'account': 'globe-cssg.privatelink',
        'authenticator': 'externalbrowser',
        'user': user, 
        'role': role,
        'warehouse': warehouse,
        'query_tag': f'Enterprise - ISDP OCR Tool Dev'
    }

    return Session.builder.configs(connection_parameters).create()




def upload_data_to_sf(
    session: Session, 
    df: pd.DataFrame, 
    table_name="ISDP_OCR_SUBMISSIONS",
    database="DB_SBX",
    schema="SP_AKAN"
):
    """
    Upload dataframe to Snowflake    
    """

    session.write_pandas(
        df,
        table_name=table_name,
        database=database,
        schema=schema
    )






def main():
    print('Creating session...')
    session = create_sf_session('alfonso.kan@globe.com.ph',
                                'ROLE_AKAN',
                                'CSSG_CDA_WH_GENERAL')
    print('Session created!')


if __name__ == '__main__':
    main()