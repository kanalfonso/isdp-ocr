import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image
import pandas as pd

from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes
from typing import Optional

# for type annotations in func
from streamlit.runtime.uploaded_file_manager import UploadedFile

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


# backend func
def process_uploaded_file(
        uploaded_file: UploadedFile,
        is_crop: bool,
        crop_box_color=None
    ):
    """
    Handles image uploaded depending on whether user wants to crop image or not
    
    Returns image in processed format
    """
    
    img = Image.open(uploaded_file)

    # if user ticks crop button
    if is_crop:
        cropped_img = st_cropper(
            img, 
            realtime_update=True, 
            box_color=crop_box_color
        )

        return cropped_img

    else:
        return img




def main():
    # Sidebar
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


    if uploaded_file:
    
        img = Image.open(uploaded_file)

        if crop_image_tick:
            with col1:
                with st.container():
                    # interactive pic with cropbox
                    cropped_img = st_cropper(
                        img, 
                        realtime_update=True, 
                        box_color=crop_box_color
                    )
        
        # If user doesn't select the crop option
        else:
            with col1:
                with st.container(border=True):
                    img = process_uploaded_file(uploaded_file, crop_image_tick)
                    st.image(img)

                # Only show when file is uploaded and 
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



if __name__ == '__main__':
    main()

    