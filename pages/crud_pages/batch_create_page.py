 # for process submission -> # TODO: to reduce clutter, make this a helper func instead -> DONE
# TODO: add option in side bar to parse selected doc only (parse mode: batch vs solo) -> DONE
# TODO: let field identifiers be suffixed by file_id (this WILL BE USED FOR validating each button) -> DONE
# TODO: fix validation buttons -> DONE
# TODO: Add mechanic where each doc needs to be validated before proceeding with submission -> DONE
# TODO: refine helper func (AI must auto detect the fields declared) 
# TODO: Read and display pdf files as well

import streamlit as st
from PIL import Image
from streamlit_pdf_viewer import pdf_viewer

# helpers for this page
from utils.streamlit.create_page_helpers import (
    persist_create_text_fields, 
    
    # On-click `Parse All Documents` or On-click `Parse Current Document`
    parse_documents,

    # Checks if all docs validated to unlock submit btn
    all_docs_validated, 
    
    # On-click `Unlock Entry` btn 
    unlock_entry, 

    # On-click `Validate & Lock Entry` btw
    validate_entry,


    # On-click `Clear content` btn 
    clear_content,

    # On-click `Submit All` btn
    process_submission
)




def sidebar_ui(total_files_uploaded):
    """
    Wrapper on sidebar UI for the OCR Page
    """

    with st.sidebar:

        # file uploader widget
        st.file_uploader(
            key="_uploaded_files",
            label="Choose images",
            accept_multiple_files=True, 
            type=["jpg", "png", "jpeg", "pdf"]
        )


        if st.session_state.get('_uploaded_files'):
            
            batch_processing_mode = st.toggle("Batch Processing", value=True)
            
            if batch_processing_mode:
                # Batch processing of image-to-text extraction
                st.button(
                    'Parse All Documents',
                    key='_batch_parsing',
                )

            else:
                st.button(
                    'Parse Current Document',
                    key='_solo_parsing',
                )

            st.divider()

            all_validated = all_docs_validated(st.session_state.file_id_to_metadata)

            st.write(
                f"Documents validated: "
                f"{sum(st.session_state.get(f'is_validated_doc_{file_id}', False) for file_id in st.session_state.file_id_to_metadata)}"
                f" / {total_files_uploaded}"
            )


            st.button(
                'Submit All',
                key='_submit_all',
                on_click=process_submission,
                disabled=not all_validated
            )







def batch_create_page():

    # uploaded files stored in a LIST
    uploaded_files = st.session_state.get('_uploaded_files') or []

    file_id_to_metadata = {
        file.file_id: {
            'idx': idx,
            'file_name': file.name,
            'UploadedFile': file
        }

        for idx, file in enumerate(uploaded_files, start=1)
    }

    st.session_state.file_id_to_metadata = file_id_to_metadata


    total_files_uploaded = len(st.session_state.get('_uploaded_files', []))

    sidebar_ui(total_files_uploaded)


    ##### Main Page #####

    # maximum allowable files to upload
    MAX_FILES = 5
    IMAGE_FILE_TYPES = ['image/png', 'image/jpeg', 'image/jpg']
    

    st.title('Batch Upload')

    # Container for notif
    container = st.container()



    # if files uploaded exceed maximum
    if total_files_uploaded > MAX_FILES:
        container.error(
            f"⚠️ You’ve uploaded {total_files_uploaded} files, "
            f"but only {MAX_FILES} are allowed per batch. "
            f"\n\nPlease remove {total_files_uploaded - MAX_FILES} file/s to continue."
        )

        return

    if st.session_state.get('is_successful_create_submission'):
        
        if st.session_state.latest_min_id == st.session_state.latest_max_id:
            container.success(
                f"✅ Entry {st.session_state.latest_min_id} has been saved.  You can use the other CRUD options to modify submissions."
            )

        else:
            container.success(
                f"✅ Entries {st.session_state.latest_min_id}-{st.session_state.latest_max_id} have been saved.  You can use the other CRUD options to modify submissions."
            )

        # turn back to false to close notif when rerun
        st.session_state.is_successful_create_submission = False
    

    # conduct check to see if file id is create text results is still part of uploaded file, if not pop
    if st.session_state.get('create_text_results'):
        for key in list(st.session_state.create_text_results.keys()):
            _, file_id = key.rsplit("_", 1)

            if file_id not in st.session_state.file_id_to_metadata:
                st.session_state.create_text_results.pop(key)



    # Submit an uploaded file
    if st.session_state.get('_uploaded_files'):
        total_files_uploaded = len(st.session_state.get('_uploaded_files'))


        

        select_options = [file.file_id for file in uploaded_files]

        # Dropdown to switch between uploaded files to display
        current_file_id = st.selectbox(
            "Select document",
            options=select_options,   # uuid
            format_func=lambda file_id: f"Document {st.session_state.file_id_to_metadata[file_id]['idx']} - {st.session_state.file_id_to_metadata[file_id]['file_name']}"
        )


        # If the `Parse All Documents` button is clicked (batch processing mode)
        if st.session_state.get('_batch_parsing'):

            file_ids = list(st.session_state.file_id_to_metadata.keys())

            # Stores parsed text to st.session_state._text_submission
            parse_documents(container, file_ids)



        # If the `Parse Current Document` button is clicked (solo processing mode)
        if st.session_state.get('_solo_parsing'):
            # Stores parsed text to st.session_state._text_submission
            parse_documents(container, [current_file_id])



        # re-fill text widgets (keys with `_` prefix) to the parse results of the associated document
        # the if-statements allow it to persist even when switching pages
        if st.session_state.create_text_results.get(f'sender_{current_file_id}'):
            st.session_state[f'_sender_{current_file_id}'] = st.session_state.create_text_results[f'sender_{current_file_id}']


        if st.session_state.create_text_results.get(f'text_submission_{current_file_id}'):
            st.session_state[f'_text_submission_{current_file_id}'] = st.session_state.create_text_results[f'text_submission_{current_file_id}']





        current_file = st.session_state.file_id_to_metadata[current_file_id]['UploadedFile']

        




        col1, col2 = st.columns([1, 1])



        # Display image file - only one at a time
        with col1:
            st.subheader("Image")
            
            # Transform uploaded file to Image object
            if current_file.type in IMAGE_FILE_TYPES:
                img = Image.open(current_file)
                st.image(img)
            
            if current_file.type == 'application/pdf':
                pdf = current_file.getvalue()
                pdf_viewer(pdf)



        ##### FIELDS TO PARSE ##### 

        is_validated = st.session_state.get(
            f'is_validated_doc_{current_file_id}',
            False
        )
        
        with col2:
            st.subheader('Fields')
            st.text_input(
                key=f'_sender_{current_file_id}',

                # to persist value even when switching pages
                # with this, manual edits get stored to persistent key as well
                on_change=persist_create_text_fields,  
                args=[f'sender_{current_file_id}'],
                disabled=is_validated,
                label='Sender',
            )

            st.text_area(
                key=f'_text_submission_{current_file_id}',

                # to persist value even when switching pages, 
                # with this, manual edits get stored to persistent key as well
                on_change=persist_create_text_fields,  
                args=[f'text_submission_{current_file_id}'],
                label="Parsed Message",
                disabled=is_validated,
                height=300,
                placeholder='Results will load here after `Parse Image` button is clicked.',
            )


            st.button(
                'Clear Current Text Fields',
                key=f'_clear_contents_{current_file_id}',
                on_click=clear_content,
                args=[container, current_file_id]
            )

            if is_validated:
                st.button(
                    "Unlock Entry",
                    on_click=unlock_entry,
                    args=[container, current_file_id]
                )


            else:
                st.button(
                    "Validate & Lock Entry",
                    on_click=validate_entry,
                    args=[container, current_file_id]
                )


        ##### FIELDS TO PARSE #####

    else:  
        container.info('ℹ️ Please upload images to proceed.')
        
        # reset to blank
        st.session_state.create_text_results = {}
        st.session_state.file_id_to_metadata = {}
    

if __name__ == '__main__':
    batch_create_page()