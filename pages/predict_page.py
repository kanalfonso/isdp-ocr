import streamlit as st
import time


# backend
def predict_entries(container, df):
    status = container.empty()

    with status:
        with st.spinner("Predicting entries...", show_time=True):
            time.sleep(1)
            df['spam_tag'] = '?'
    
    # Show success inside the top container
    container.success("✅ Predictions successfully generated!")




def predict_page():
    """
    UI when user chooses `Predict` as the selected CRUD operation
    """
    st.title('Predict Spam Type of Records')

    container = st.container()

    if len(st.session_state.submissions_df) > 0:
        st.dataframe(st.session_state.submissions_df, hide_index=True)


        st.button(
            'Predict',
            on_click=predict_entries,
            args=(container, st.session_state.submissions_df)
        )
    
    # No records
    else: 
        container.warning(
            "No records detected." 
            "\n\nCreate a new submission by going to the **Submissions** page and selecting selecting the **Create** Operation."
        )


if __name__ == '__main__':
    predict_page()