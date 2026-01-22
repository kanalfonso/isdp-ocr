import streamlit as st

def no_records_page():
    
    container = st.container()
    container.warning(
        "⛔ No records detected." 
        "\n\nCreate a new submission by going to the **Submissions** page and selecting the **Create** Operation."
    )


if __name__ == '__main__':
    no_records_page()