import streamlit as st
import time


st.title('Connect to Snowflake')

# Container for success and spinner status
status_container = st.container()

with st.form('sf_conn_form'):

    email_input = st.text_input('Email Address')
    role_input = st.text_input('Role')
    warehouse_input = st.text_input('Warehouse')

    # Submit button
    submit = st.form_submit_button('Establish connection')



with status_container:
    if submit:
        with st.spinner("Creating session...", show_time=True):
            time.sleep(1.5)

        st.success('Connection secured!')

