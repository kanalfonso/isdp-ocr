import streamlit as st
import time

from pages.no_records_page import no_records_page 


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
    
    if st.session_state.submissions_df.empty:
        no_records_page()
        
        # Need to end with `return` so won't load the empty table
        return
    
    container = st.container()

    container.info(
        "ℹ️ Click the Predict button to perform batch prediction on all entries."
        "\n\nPrediction time depends on how many entries you have."
    )


    st.dataframe(st.session_state.submissions_df, hide_index=True)


    st.button(
        'Predict',
        on_click=predict_entries,
        args=[container, st.session_state.submissions_df]
    )
    

if __name__ == '__main__':
    predict_page()