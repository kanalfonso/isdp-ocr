import streamlit as st
import pandas as pd
import time
from PIL import Image
from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes


def persist_create_text_fields(key):
    st.session_state.create_text_results[key] = st.session_state['_' + key] 




def convert_create_text_results_to_df(create_text_results: dict):
    """
    Pass `create_text_results` dict to return an equivalent dataframe 
    """
    rows = {}

    for key, value in create_text_results.items():
        field, file_id = key.rsplit("_", 1)   # sender_0 → sender, 0        

        rows.setdefault(file_id, {})[field] = value

    latest_submission = (
        pd.DataFrame
        .from_dict(rows, orient="index")
        .reset_index(drop=True)
    )


    return latest_submission


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



def unlock_entry(
        container, 
        current_file_id
    ):
    """
    Unlocks text fields for the selected entry
    """

    container.info(
        'ℹ️ Fields have been unlocked. Please lock to process submission.'
    )

    st.session_state[f'is_validated_doc_{current_file_id}'] = False




def validate_entry(
        container, 
        current_file_id
    ):
    """
    Form validation for the selected doc
    
    Shows error if blank entries. If successful entry, triggers disabled fields 
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
    
    st.session_state[f'is_validated_doc_{current_file_id}'] = False

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



# def convert_bytes_to_hash(file: UploadedFile) -> str:
#     """
#     This func takes an `UploadedFile`, converts it into a bytes object 
    
#     Returns a hash digest of type str
#     """

#     # read file as bytes
#     file_bytes = file.getvalue()

#     # instantiate hash object
#     sha = hashlib.sha256()

#     # create hash digest from bytes
#     sha.update(file_bytes)


#     return sha.hexdigest()




# def storing_doc_metadata(
#         file: UploadedFile, 
#         doc_id_to_metadata: dict,
#     ):

#     """
#     Updates values for st.session_state.doc_id_to_metadata when a file is passed, regardless if existing or old
#     """
    
#     doc_id_to_metadata[file.file_id] = {
#         'file_name': file.name,
#         'UploadedFile': file
#     }


