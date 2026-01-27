# for parse images -> TODO: refine helper func (AI must auto detect the fields declared) 
# for process submission -> # TODO: to reduce clutter, make this a helper func instead -> DONE
# TODO: add option in side bar to parse selected doc only (parse mode: batch vs solo) 
# TODO: use hashlib instead of relying on index as an identifier for the doc (this WILL BE USED FOR validating each button)


# use filehash to distinguish between files


import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image
import pandas as pd
import uuid

# helper function
from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes
from utils.streamlit_utils import persist_create_text_fields, convert_create_text_results_to_df, convert_bytes_to_hash, storing_doc_metadata


# backend func
def clear_content(container, current_doc_index):
    """
    Set st.session_state._text_submission to None
    """
    
    # Clear both perm and temp keys
    st.session_state.create_text_results[f'sender_{current_doc_index}'] = None
    st.session_state[f'_sender_{current_doc_index}'] = None
    
    # Clear both perm and temp keys
    st.session_state.create_text_results[f'text_submission_{current_doc_index}'] = None
    st.session_state[f'_text_submission_{current_doc_index}'] = None
    
    # st.session_state._is_clear_content = True

    container.success('✅ Text fields for the current document has been cleared!')


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
    

    # for idx, uuid, file in enumerate(zip(st.session_state.doc_id_to_metadata.keys(), uploaded_files), start=0):


    
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

        ## TODO: replace this with uuid instead of idx
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





## work on this
def validate_entry(
        container, 
        current_doc_index,
        doc_index_to_name
    ):
    """
    Form validation for the selected doc, shows error if blank entries
    """

    # Valid sender entry
    if (st.session_state[f'_sender_{current_doc_index}'] is None) or (st.session_state[f'_sender_{current_doc_index}'].strip() == ""):
        container.error('⚠️ Please ensure that the **Sender** text field is not **BLANK**!')   
        return


    if (st.session_state[f'_text_submission_{current_doc_index}'] is None) or (st.session_state[f'_text_submission_{current_doc_index}'].strip() == ""):
        container.error('⚠️ Please ensure that the **Parsed Message** text field is not **BLANK**!')   
        return


    container.success(
        f"✅ Document {current_doc_index + 1} - {doc_index_to_name[current_doc_index]} entry is valid.\n\n"
        "Fields have been locked. To unlock, click **Unvalidate entry**"
    )


    # use hashlib?

    # # Validation
    # st.session_state[f'is_validated_doc_{current_doc_index}'] = True



def process_submission():
    """
    Collate into a dataframe then submit entries
    """

    # Helper func that transforms dict to a dataframe
    latest_submission = convert_create_text_results_to_df(st.session_state.create_text_results)

    if st.session_state.submissions_df.empty:
        start_id = 1
    else:
        start_id = st.session_state.submissions_df['id'].max() + 1

    latest_submission.insert(0, 'id', range(start_id, start_id + len(latest_submission)))


    # # List of new IDs added
    # new_ids = latest_submission['id'].tolist()

    # # get min and max IDs
    # st.session_state.latest_min_id, st.session_state.latest_max_id  = min(new_ids), max(new_ids)


    # Save to submissions df
    st.session_state.submissions_df = pd.concat([st.session_state.submissions_df, latest_submission], ignore_index=True)


    # submission success
    st.session_state.is_successful_create_submission = True


    






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
                'Parse All Documents',
                key='_parse_image',
            )


            st.divider()

            st.button(
                'Submit All',
                key='_submit_all',
                on_click=process_submission
            )







def batch_create_page():

    sidebar_ui()

    ##### Main Page #####

    # maximum allowable files to upload
    MAX_FILES = 5

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

    if st.session_state.get('is_successful_create_submission'):
        # container.success(
        #     f"✅ Entries {st.session_state.latest_min_id}-{st.session_state.latest_max_id} have been saved.  You can use the other CRUD options to modify it."
        # )
        container.success("Successful submission")
        # turn back to false to close notif when rerun
        st.session_state.is_successful_create_submission = False

    
    # # When you press on the `Clear Current Text Fields` button
    # if st.session_state.get('_is_clear_content'):
    #     # container.info('ℹ️ Text fields for the current document has been cleared!')
    #     st.session_state['_is_clear_content'] = False




    # Submit an uploaded file
    if st.session_state.get('_uploaded_files'):
        total_files_uploaded = len(st.session_state.get('_uploaded_files'))


        # If the `Parse Image` button is clicked
        if st.session_state.get('_parse_image'):
            # Stores parsed text to st.session_state._text_submission
            parse_images(container, st.session_state.get('_uploaded_files'))


        # uploaded files stored in a LIST
        uploaded_files = st.session_state.get('_uploaded_files')
        

        doc_id_to_metadata = {}

        for idx, file in enumerate(uploaded_files, start=0):
            
            # Converting UploadedFile -> Bytes -> Hash Digest
            file_hash = convert_bytes_to_hash(file)

            # Update values for st.session_state.doc_id_to_metadata
            storing_doc_metadata(idx, file, file_hash, doc_id_to_metadata)

        
        # overwrite session state value
        st.session_state.doc_id_to_metadata = doc_id_to_metadata


        # doc_index_options = [metadata['idx'] for metadata in doc_id_to_metadata.values()]

        # Dropdown to switch between uploaded files to display
        current_doc_id = st.selectbox(
            "Select document",
            options=[id for id in doc_id_to_metadata.keys()],   # uuid
            index=0, # as default, will show first option
            format_func=lambda id: f"Document {doc_id_to_metadata[id]['idx']} - {doc_id_to_metadata[id]['file_name']}"
            # format_func=lambda idx: f"Document {idx+1} - {doc_index_to_name[idx]}"
        )


        # re-fill text widgets (keys with `_` prefix) to the parse results of the associated document
        # the if-statements allow it to persist even when switching pages
        if st.session_state.create_text_results.get(f'sender_{current_doc_id}'):
            st.session_state[f'_sender_{current_doc_id}'] = st.session_state.create_text_results[f'sender_{current_doc_id}']


        if st.session_state.create_text_results.get(f'text_submission_{current_doc_id}'):
            st.session_state[f'_text_submission_{current_doc_id}'] = st.session_state.create_text_results[f'text_submission_{current_doc_index}']





        current_file = uploaded_files[doc_id_to_metadata[current_doc_id]['idx']]


        # Transform uploaded file to Image object
        img = Image.open(current_file)



        # Display image file - only one at a time
        st.image(img)




        ##### FIELDS TO PARSE ##### 

        is_validated = st.session_state.get(
            f'is_validated_doc_{current_doc_id}',
            False
        )
        

        st.text_input(
            key=f'_sender_{current_doc_id}',

            # to persist value even when switching pages
            # with this, manual edits get stored to persistent key as well
            on_change=persist_create_text_fields,  
            args=[f'sender_{current_doc_id}'],
            disabled=is_validated,
            label='Sender',
        )

        st.text_area(
            key=f'_text_submission_{current_doc_id}',

            # to persist value even when switching pages, 
            # with this, manual edits get stored to persistent key as well
            on_change=persist_create_text_fields,  
            args=[f'text_submission_{current_doc_id}'],
            label="Parsed Message",
            disabled=is_validated,
            height=300,
            placeholder='Results will load here after `Parse Image` button is clicked.',
        )


        st.button(
            'Clear Current Text Fields',
            key=f'_clear_contents_{current_doc_id}',
            on_click=clear_content,
            args=[container, current_doc_id]
        )

        # st.button(
        #     "Validate & Lock Entry",
        #     on_click=validate_entry,
        #     args=[container, current_doc_index, doc_index_to_name]
        # )


        ##### FIELDS TO PARSE #####


        # data = list(zip(doc_id_to_metadata.items(), uploaded_files))
        # print(data)
    else:  
        container.info('ℹ️ Please upload an image file to proceed.')
    

    return container




if __name__ == '__main__':
    batch_create_page()

    