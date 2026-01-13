# pip install snowflake-snowpark-python
from snowflake.snowpark import Session

def create_sf_session(
    user: str,
    role: str,        
    warehouse: str
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
        'query_tag': 'ISDP OCR Tool'
    }

    return Session.builder.configs(connection_parameters).create()


def main():
    print('Creating session...')
    session = create_sf_session('alfonso.kan@globe.com.ph',
                                'ROLE_AKAN',
                                'CSSG_CDA_WH_GENERAL')
    print('Session created!')


if __name__ == '__main__':
    main()