import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image
import pandas as pd

# helper function
from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes




# backend func
def parse_image(
        container: st.delta_generator.DeltaGenerator, 
        image_file
        
    ) -> str:
    """
    Parse image by passing image as bytes

    Notifies image has been successfully parsed 
    Stores results to `_text_submission` in session state
    """
    status = container.empty()

    with status:
        with st.spinner("Parsing image...", show_time=True):
            time.sleep(1)
        
            img_bytes = pil_image_to_bytes(image_file)

            parsed_text = detect_text_from_bytes(img_bytes)
        
        # Show success inside the top container
        container.success(
            "✅ Image parsed successfully! Please verify the text and edit if needed."
        )

        # Store results in `_text_submission`
        st.session_state._text_submission = 'parsed_text'




def clear_content():
    """
    Set st.session_state._text_submission to None
    """
    
    st.session_state._text_submission = None
    st.session_state._is_clear_content = True



def process_submission(container):
    """
    Process text submission by storing it, along with other submission, in a pandas DataFrame
    """

    # Valid Submission
    if (st.session_state._text_submission is not None) and (st.session_state._text_submission.strip() != ""):
        
        # ID column for dataframe
        if st.session_state.submissions_df.empty:
            next_id = 1
        else:
            next_id = st.session_state.submissions_df['id'].max() + 1


        row = {
            'id': next_id, 
            'sender': st.session_state._sender,
            'content': st.session_state._text_submission, 
            'spam_tag': None
        }

        latest_submission = pd.DataFrame([row])



        st.session_state.submissions_df = pd.concat([st.session_state.submissions_df, latest_submission], ignore_index=True)

        container.success(
            "✅ Submission saved! Use other CRUD options to modify entries."
        )


    # Invalid Submission
    else:
        container.error('⚠️ Please ensure that the text field is not **BLANK**!')   


def sidebar_ui():
    """
    Wrapper on sidebar UI for the OCR Page
    """


    with st.sidebar:

        # file uploader widget
        st.file_uploader(
            key="_uploaded_file",
            label="Choose an image",
            accept_multiple_files=False, 
            type=["jpg", "png"]
        )


        # If file has been uploaded
        if st.session_state.get('_uploaded_file'):

            # Parse Image button
            st.button(
                'Parse Image',
                key='_parse_image'
            )

            # Crop Image tick
            st.checkbox(
                'Crop Image',
                key='_crop_image'
            )

            st.markdown(
                "<div style='margin-top: 32px'></div>", 
                unsafe_allow_html=True
            )

            st.button(
                'Clear Submission',
                key='_clear_contents',
                on_click=clear_content
            )


        # If crop image tick box is clicked
        if st.session_state.get('_crop_image'):
            ## Change crop box color
            st.color_picker(
                key="_crop_box_color",
                label="Crop Box Color", 
                value='#0000FF'
            )






def create_page():

    sidebar_ui()

    ##### Main Page #####



    # Submit an uploaded file
    if st.session_state.get('_uploaded_file'):
    
        # Title
        st.title('Create Records (Text-to-Image Extraction)')

        # Container for notification  
        container = st.container()

        if st.session_state.get('_is_clear_content'):
            container.info('ℹ️ Text field has been cleared')
            st.session_state['_is_clear_content'] = False


        # Columns
        col1, col2 = st.columns([0.5, 0.5])
        
        uploaded_file = st.session_state._uploaded_file
        
        # Transform uploaded file to Image object
        img = Image.open(uploaded_file)


        # User ticks Crop Image
        if st.session_state.get('_crop_image'):

            with col1: 
                st.write('Set Crop Box')
                with st.container(border=True):
                    # Interactive image cropper
                    cropped_img = st_cropper(
                        img, 
                        realtime_update=True, 
                        box_color=st.session_state._crop_box_color
                    )

            with col2:
                st.write('Crop Results')
                with st.container(border=True):
                    st.image(cropped_img)
        

        # User DOESN'T tick Crop Image
        else:
            st.image(img)


        # If the `Parse Image` button is clicked
        if st.session_state.get('_parse_image'):
            # Stores parsed text to st.session_state._text_submission
            parse_image(container, img)

        st.text_input(
            key='_sender',
            label='Sender',
            value=None
        )

        st.text_area(
            key='_text_submission',
            label="Parsed Message",
            value=None,
            height=300,
            placeholder='Results will load here after `Parse Image` button is clicked.'
        )

        st.button(
            'Submit',
            on_click=process_submission,
            args=[container]
        )

    else:  
        container = st.container()
        container.info('ℹ️ Please upload an image file to proceed.')


if __name__ == '__main__':
    create_page()

    