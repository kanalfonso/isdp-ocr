import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image
import pandas as pd

from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes


# backend func
def parse_image(
        container: st.delta_generator.DeltaGenerator, 
        file_bytes: bytes
    ):
    """
    Parse image by passing image as bytes

    Returns parsed text stored in session state and 
    container modified with success notification
    """
    status = container.empty()

    with status:
        with st.spinner("Parsing image...", show_time=True):
            time.sleep(1)
            # parsed_text = detect_text_from_bytes(file_bytes)
        
        # Show success inside the top container
        container.success("Image successfully parsed!")
        st.session_state['parsed_text'] = 'Parsed text'



def ocr_navigation(
        uploaded_file,
        ui: dict
    ):
    """
    Initiate UI change depending on whether user decides to use crop box or not
    """

    # set as variable the components passed to the dict
    container = ui['container']
    col1, col2 = ui['cols']
    parse_image_btn = ui['parse_image_btn']
    crop_image_tick = ui['crop_image_tick']
    crop_box_color = ui['crop_box_color']


    #### TODO: after each submit, add the submission to the session state dataframe
    if 'submissions_df' not in st.session_state:
        st.session_state['submissions_df'] = pd.DataFrame()


    if uploaded_file:

        # returns an Image object
        img = Image.open(uploaded_file)

        
      
        if crop_image_tick:

            with col1:      
                # PIL image
                # st.write('Set crop box')
                
                with st.container(border=True, width=1000):
                    
                    # interactive pic with cropbox
                    cropped_img = st_cropper(
                        img, 
                        realtime_update=True, 
                        box_color=crop_box_color
                    )

                


                if parse_image_btn:
                    # Convert image to bytes
                    cropped_img_bytes = pil_image_to_bytes(cropped_img)
                    
                    # Parse image
                    parse_image(container, cropped_img_bytes)

                
            with col2:

                cropped_container = st.container(width=1000, border=True)


                # result of the st cropper
                with cropped_container:
                    st.write("Cropped Image")
                    st.image(cropped_img)


            txt_submission = st.text_area(
                label="Parsed Message",
                value=st.session_state['parsed_text'] if 'parsed_text' in st.session_state else None,
                height=400,
            )


        else:
            with col1:
                with st.container(border=True, width=1000):
                    st.image(img)

                if parse_image_btn:
                    img_bytes = pil_image_to_bytes(img)

                    # Parse image
                    parse_image(container, img_bytes)

                

            with col2:

                txt_submission = st.text_area(
                    label="Parsed Message",
                    value=st.session_state['parsed_text'] if 'parsed_text' in st.session_state else None,
                    height=400
                )

 


        #### LOGIC FOR SUBMITTING RECORDS ####
        
        if st.button('Submit'):
      

            if (txt_submission is not None) and (txt_submission.strip() != ""):
                row = {
                    'content': txt_submission, 
                    'spam_tag': None
                }

                st.session_state['txt_submission'] = row
                st.session_state['submission_done'] = True
                

            else:
                st.session_state['txt_submission'] = None
                st.session_state['submission_done'] = False
                

            # Show success if submission is done
            if st.session_state.submission_done:
                container.success('Submission recorded! To view, edit, or delete entry proceed to the **Submissions** Page')
                latest_submission = pd.DataFrame([row])

                st.session_state.submissions_df = pd.concat([st.session_state.submissions_df, latest_submission], ignore_index=True)


            else:
                container.warning('Please ensure that the text field is not blank!')   


    # check session state variables
    st.write(st.session_state) 



# UI func
def main():
    """
    Page navigation for OCR page
    """

    # Initially set components to `None`
    crop_image_tick = None
    crop_box_color = None
    parse_image_btn = None

    with st.sidebar:
        uploaded_file = st.file_uploader(
            label="Choose an image",
            accept_multiple_files=False, 
            type=["jpg", "png"]
        )

        if uploaded_file:
            parse_image_btn = st.button('Parse image')   

            crop_image_tick = st.checkbox('Crop Image')
            


            if crop_image_tick:
                ## Cropper settings
                crop_box_color = st.color_picker(label="Crop Box Color", value='#0000FF')
            
    # Title of Page
    st.title('Text-to-Image Extraction')

    # Container for notification  
    container = st.container()

    # Columns
    col1, col2 = st.columns(2)
    
    # collate components in a dict
    ui = {
        "container": container,
        "cols": (col1, col2),
        "parse_image_btn": parse_image_btn,
        "crop_image_tick": crop_image_tick,
        "crop_box_color": crop_box_color
    }

    # navigation for ocr -- pass components here
    ocr_navigation(
        uploaded_file,
        ui
    )




if __name__ == '__main__':
    main()