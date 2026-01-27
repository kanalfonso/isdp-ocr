# for parse images -> TODO: refine helper func (AI must auto detect the fields declared) 
# for process submission -> # TODO: to reduce clutter, make this a helper func instead -> DONE
# TODO: add option in side bar to parse selected doc only (parse mode: batch vs solo) 
# TODO: let field identifiers be suffixed by file_id (this WILL BE USED FOR validating each button) -> DONE
# TODO: fix validation buttons -> DONE
# TODO: Add mechanic where each doc needs to be validated before proceeding with submission -> DONE


# use filehash to distinguish between files


import streamlit as st
import time
from PIL import Image
import pandas as pd

# helper function
from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes
from utils.streamlit_utils import persist_create_text_fields, convert_create_text_results_to_df


# backend func
def clear_content(container, current_file_id):
    """
    Set st.session_state._text_submission to None
    """
    
    # Clear both perm and temp keys
    st.session_state.create_text_results[f'sender_{current_file_id}'] = None
    st.session_state[f'_sender_{current_file_id}'] = None
    
    # Clear both perm and temp keys
    st.session_state.create_text_results[f'text_submission_{current_file_id}'] = None
    st.session_state[f'_text_submission_{current_file_id}'] = None
    
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



    for file_id in st.session_state.file_id_to_metadata.keys():

        idx, file = st.session_state.file_id_to_metadata[file_id]['idx'], st.session_state.file_id_to_metadata[file_id]['UploadedFile']

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
        st.session_state.create_text_results[f'sender_{file_id}'] = f'sender for doc {file_id}'
        st.session_state.create_text_results[f'text_submission_{file_id}'] = f'parsed text for doc {file_id}'
        # st.session_state.create_text_results[f'text_submission_{idx}'] = parsed_text


        # start at 1
        progress = (idx) / total_files
        
        progress_bar.progress(
            progress,
            text=f'Processing file {idx} out of {total_files}'
        )


    if (idx) == total_files:
        time.sleep(1)  # allow UI to render final state
    

    status.success("✅ All files processed successfully!")





## work on this
def validate_entry(
        container, 
        current_file_id
    ):
    """
    Form validation for the selected doc, shows error if blank entries
    """

    # Valid sender entry
    if (st.session_state[f'_sender_{current_file_id}'] is None) or (st.session_state[f'_sender_{current_file_id}'].strip() == ""):
        container.error('⚠️ Please ensure that the **Sender** text field is not **BLANK**!')   
        return


    if (st.session_state[f'_text_submission_{current_file_id}'] is None) or (st.session_state[f'_text_submission_{current_file_id}'].strip() == ""):
        container.error('⚠️ Please ensure that the **Parsed Message** text field is not **BLANK**!')   
        return


    container.success(
        f"✅ Document {st.session_state.file_id_to_metadata[current_file_id]['idx']} - {st.session_state.file_id_to_metadata[current_file_id]['file_name']} entry is valid.\n\n"
        "Fields have been locked. To unlock, click **Unvalidate entry**"
    )

    st.session_state[f'is_validated_doc_{current_file_id}'] = True


def unlock_entry(
        container, 
        current_file_id
    ):
    """
    Unlock fields
    """

    container.info(
        'ℹ️ Fields have been unlocked. Please lock to process submission.'
    )

    st.session_state[f'is_validated_doc_{current_file_id}'] = False


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


    # List of new IDs added
    new_ids = latest_submission['id'].tolist()

    # get min and max IDs
    st.session_state.latest_min_id, st.session_state.latest_max_id  = min(new_ids), max(new_ids)


    # Save to submissions df
    st.session_state.submissions_df = pd.concat([st.session_state.submissions_df, latest_submission], ignore_index=True)


    # submission success
    st.session_state.is_successful_create_submission = True


    


def all_docs_validated(file_id_to_metadata: dict) -> bool:
    """
    Returns True if ALL uploaded docs are validated
    """

    # # No documents meaning NOT validated
    # if not file_id_to_metadata:
    #     return False
    

    for file_id in file_id_to_metadata.keys():
        if not st.session_state.get(f'is_validated_doc_{file_id}', False):
            return False
    return True



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
            type=["jpg", "png"]
        )


        if st.session_state.get('_uploaded_files'):
            # Parse Image button
            st.button(
                'Parse All Documents',
                key='_parse_image',
            )


            st.divider()

            all_validated = all_docs_validated(st.session_state.file_id_to_metadata)

            st.write(
                f"Documents validated: "
                f"{sum(st.session_state.get(f'is_validated_doc_{fid}', False) for fid in st.session_state.file_id_to_metadata)}"
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


        # If the `Parse Image` button is clicked
        if st.session_state.get('_parse_image'):
            # Stores parsed text to st.session_state._text_submission
            parse_images(container, st.session_state.get('_uploaded_files'))

        

        select_options = [file.file_id for file in uploaded_files]

        # Dropdown to switch between uploaded files to display
        current_file_id = st.selectbox(
            "Select document",
            options=select_options,   # uuid
            format_func=lambda file_id: f"Document {st.session_state.file_id_to_metadata[file_id]['idx']} - {st.session_state.file_id_to_metadata[file_id]['file_name']}"
        )


        # re-fill text widgets (keys with `_` prefix) to the parse results of the associated document
        # the if-statements allow it to persist even when switching pages
        if st.session_state.create_text_results.get(f'sender_{current_file_id}'):
            st.session_state[f'_sender_{current_file_id}'] = st.session_state.create_text_results[f'sender_{current_file_id}']


        if st.session_state.create_text_results.get(f'text_submission_{current_file_id}'):
            st.session_state[f'_text_submission_{current_file_id}'] = st.session_state.create_text_results[f'text_submission_{current_file_id}']





        current_file = st.session_state.file_id_to_metadata[current_file_id]['UploadedFile']


        # Transform uploaded file to Image object
        img = Image.open(current_file)



        # Display image file - only one at a time
        st.image(img)




        ##### FIELDS TO PARSE ##### 

        is_validated = st.session_state.get(
            f'is_validated_doc_{current_file_id}',
            False
        )
        

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


        # data = list(zip(doc_id_to_metadata.items(), uploaded_files))
        # print(data)

    else:  
        container.info('ℹ️ Please upload an image file to proceed.')
        
        # reset to blank
        st.session_state.create_text_results = {}
        st.session_state.file_id_to_metadata = {}
    




if __name__ == '__main__':
    batch_create_page()

    