# Standard Libraries
import time

# Streamlit Libraries
import streamlit as st

# Old Logout Design
# with st.spinner("Logging out..."):
#     # Clear session state
#     st.session_state.clear()
#     time.sleep(2)  # Simulate a slight delay for better UX
#     st.rerun()  # Refresh the app to take the user back to the login screen
    
# st.switch_page("pages/Login.py")  # Redirect to login if not authenticated


@st.dialog("Are you sure you want to log out?")
def logout_option():
    # Perform logout if "Yes" was clicked
    if st.button("Yes", type="primary"):
        with st.spinner("Logging out..."):
            st.session_state.clear()  # Clear all session state
            time.sleep(1.5)  # UX delay
            st.rerun()  # Refresh the app


if __name__ == '__main__':
    try:
        # Ensure redirection after reloading
        if "email" and "credentials" not in st.session_state:  # Or check authentication state
            st.switch_page("pages/login_page.py")  # Redirect to login
        else:
            logout_option()
    except Exception as e:
        st.error(f'**Unknown Error**: Please refresh browser or if issue persists, please reach out to the CDA - Enterprise Team.  \n\nError Message: {e}', icon='🚫')