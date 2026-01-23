import streamlit as st
import time

from pages.no_records_page import no_records_page 
from utils.generate_taggings import step_1, step_2, step_3, step_4, step_5, step_6, step_7, step_8


# backend
def predict_entries(progress_placeholder, container, df):
    # status = container.empty()

    # with status:
    #     with st.spinner("Predicting entries...", show_time=True):

    # start time of prediction
    start_time = time.perf_counter()

    progress_bar = progress_placeholder.progress(0.1, text="Step 0: Loading dataframe...")
    spamshield_df = df.copy()
    time.sleep(1)

    progress_bar.progress(0.2, text="Step 1: Removing no record rows / no record indeces....")
    complete_records_spamshield_df, spamshield_df, no_record_indeces = step_1(spamshield_df)


    progress_bar.progress(0.3, text="Step 2: Generating spam code features....")
    spamcode_df = step_2(complete_records_spamshield_df)


    progress_bar.progress(0.4, text="Step 3: Calling spam code model....")
    spam_code_modeling_df, X = step_3(spamcode_df)


    progress_bar.progress(0.5, text="Step 4: Determining spam code prediction....")
    sms_no_spamcodes_df, spamcode_indeces = step_4(spam_code_modeling_df, X)


    progress_bar.progress(0.6, text="Step 5: Generating spam type features....")
    sms_no_spamcodes_no_url_no_imsi_df, imsi_indeces, url_indeces = step_5(sms_no_spamcodes_df)


    progress_bar.progress(0.7, text="Step 6: Generating embeddings....")
    modeling_df = step_6(sms_no_spamcodes_no_url_no_imsi_df)


    progress_bar.progress(0.8, text="Step 7: Predicting spam type....")
    predicted_spam_type_indeces, label_mapping_df = step_7(modeling_df)


    progress_bar.progress(1.0, text="Step 8: Assigning labels....")
    output_table = step_8(
        spamshield_df,
        spamcode_indeces,
        url_indeces,
        imsi_indeces,
        no_record_indeces,
        predicted_spam_type_indeces,
        label_mapping_df

    )

    # update the submissions df
    st.session_state.submissions_df = output_table

    # end time of prediction
    end_time = time.perf_counter()

    # calculate total run time
    total_runtime = end_time - start_time

    # Show success inside the top container
    container.success(f"✅ Predictions successfully generated! Total runtime: {total_runtime:.2f} seconds")




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

    # progress bar
    progress_placeholder = st.empty()

    st.dataframe(st.session_state.submissions_df, hide_index=True)


    st.button(
        'Predict',
        on_click=predict_entries,
        args=[progress_placeholder, container, st.session_state.submissions_df],
        key='_predict_btn'
    )
    

if __name__ == '__main__':
    predict_page()