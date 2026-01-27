import streamlit as st
from streamlit.runtime.uploaded_file_manager import UploadedFile
import pandas as pd
# import hashlib
# import uuid


# Backend
def persist_key(key):
    """
    Persists key across different pages
    """
    st.session_state[key] = st.session_state['_' + key] 

def persist_create_text_fields(key):
    st.session_state.create_text_results[key] = st.session_state['_' + key] 




# data structure: 

# "create_text_results":{
# "text_submission_0":"parsed text for doc 0"
# "sender_0":"sender for doc 0"
# "sender_1":"sender for doc 1"
# "text_submission_1":"parsed text for doc 1"
# "sender_2":"sender for doc 2"
# "text_submission_2":"parsed text for doc 2"
# }


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


