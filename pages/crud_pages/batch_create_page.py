import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image
import pandas as pd

# helper function
from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes
from utils.streamlit_utils import persist_create_text_fields



# backend func
def parse_images(
        container: st.delta_generator.DeltaGenerator, 
        uploaded_files: list
        
    ) -> str:
    """
    Parse image by passing image as bytes

    Notifies image has been successfully parsed 
    Stores results to `_text_submission` in session state
    """
    status = container.empty()

    total_files = len(uploaded_files)

    progress_bar = status.progress(0, text="Starting processing...")
    
    for idx, file in enumerate(uploaded_files, start=0):
        
        time.sleep(1)

        # convert to Image object
        img_file = Image.open(file)
        
        # convert to bytes
        img_bytes = pil_image_to_bytes(img_file)

        # Image-to-text func using Gemini (comment for now to save on credits)
        # TODO: refine helper func (AI must auto detect the fields declared)
        # parsed_text = detect_text_from_bytes(img_bytes)

        # store permanently in create_text_results
        st.session_state.create_text_results[f'sender_{idx}'] = f'sender for doc {idx}'
        st.session_state.create_text_results[f'text_submission_{idx}'] = f'parsed text for doc {idx}'
        # st.session_state.create_text_results[f'text_submission_{idx}'] = parsed_text


        # start at 1
        progress = (idx + 1) / total_files
        
        progress_bar.progress(
            progress,
            text=f'Processing file {idx + 1} out of {total_files}'
        )


    if (idx+1) == total_files:
        time.sleep(1)  # allow UI to render final state
    

    status.success("✅ All files processed successfully!")





def sidebar_ui():
    """
    Wrapper on sidebar UI for the OCR Page
    """

    with st.sidebar:

        # file uploader widget
        st.file_uploader(
            key="_uploaded_files",
            label="Choose images",
            accept_multiple_files=True, 
            type=["jpg", "png"]
        )


        if st.session_state.get('_uploaded_files'):
            # Parse Image button
            st.button(
                'Parse Image',
                key='_parse_image',
            )





def batch_create_page():

    sidebar_ui()

    ##### Main Page #####

    # maximum allowable files to upload
    MAX_FILES = 2

    st.title('Batch Upload')

    # Container for notif
    container = st.container()

    total_files_uploaded = len(st.session_state.get('_uploaded_files'))

    # if files uploaded exceed maximum
    if total_files_uploaded > MAX_FILES:
        container.error(
            f"⚠️ You’ve uploaded {total_files_uploaded} files, "
            f"but only {MAX_FILES} are allowed per batch. "
            f"\n\nPlease remove {total_files_uploaded - MAX_FILES} file/s to continue."
        )

        return


    # Submit an uploaded file
    if st.session_state.get('_uploaded_files'):
        total_files_uploaded = len(st.session_state.get('_uploaded_files'))


        # If the `Parse Image` button is clicked
        if st.session_state.get('_parse_image'):
            # Stores parsed text to st.session_state._text_submission
            parse_images(container, st.session_state.get('_uploaded_files'))


        # uploaded files stored in a LIST
        uploaded_files = st.session_state.get('_uploaded_files')
        

        # Transform uploaded_files into this dict => {doc_idx: doc_name}
        doc_index_to_name = {
            idx: uploaded_files[idx].name 
            for idx in range(len(uploaded_files))
        }
        
        doc_index_options = [idx for idx in doc_index_to_name.keys()]
        

        # Dropdown to switch between uploaded files to display
        current_doc_index = st.selectbox(
            "Select document",
            options=doc_index_options,
            index=0, # as default, will show first option
            format_func=lambda idx: f"Document {idx+1} - {doc_index_to_name[idx]}"
        )


        # re-fill text widgets (keys with `_` prefix) to the parse results of the associated document
        # the if-statements allow it to persist even when switching pages
        if st.session_state.create_text_results.get(f'sender_{current_doc_index}'):
            st.session_state[f'_sender_{current_doc_index}'] = st.session_state.create_text_results[f'sender_{current_doc_index}']


        if st.session_state.create_text_results.get(f'text_submission_{current_doc_index}'):
            st.session_state[f'_text_submission_{current_doc_index}'] = st.session_state.create_text_results[f'text_submission_{current_doc_index}']





        current_file = uploaded_files[current_doc_index]


        # Transform uploaded file to Image object
        img = Image.open(current_file)



        # Display image file - only one at a time
        st.image(img)




        ##### FIELDS TO PARSE ##### 

        st.text_input(
            key=f'_sender_{current_doc_index}',

            # to persist value even when switching pages
            # with this, manual edits get stored to persistent key as well
            on_change=persist_create_text_fields,  
            args=[f'sender_{current_doc_index}'],
            label='Sender',
        )

        st.text_area(
            key=f'_text_submission_{current_doc_index}',

            # to persist value even when switching pages, 
            # with this, manual edits get stored to persistent key as well
            on_change=persist_create_text_fields,  
            args=[f'text_submission_{current_doc_index}'],
            label="Parsed Message",
            height=300,
            placeholder='Results will load here after `Parse Image` button is clicked.',
        )


        ##### FIELDS TO PARSE #####

    else:  
        container.info('ℹ️ Please upload an image file to proceed.')
    

    return container




if __name__ == '__main__':
    batch_create_page()

    