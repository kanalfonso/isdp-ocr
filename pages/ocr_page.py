import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image

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
        # st.session_state['parsed_text'] = parsed_text

# backend func
def clear_contents():
    """
    Clears session state for parsed_text
    """
    st.session_state.pop("parsed_text", None)


def ocr_navigation(
        uploaded_file,
        crop_image_tick,
        col1,
        col2,
        crop_box_color,
        parse_image_btn,
        container
    ):
    """
    Initiate UI change depending on whether user decides to use crop box or not
    """

    if uploaded_file:

        # returns an Image object
        img = Image.open(uploaded_file)
        
        if crop_image_tick:

            with col1:      
                # PIL image
                # st.write('Set crop box')
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

                cropped_container = st.container(width=800, height=800)

                with cropped_container:
                    st.write("Cropped Image")
                    st.image(cropped_img)


            st.text_area(
                label="Parsed Message",
                value=st.session_state['parsed_text'] if 'parsed_text' in st.session_state else None,
                height=400,
            )


        else:
            with col1:
                st.image(img)

                if parse_image_btn:
                    img_bytes = pil_image_to_bytes(img)

                    # Parse image
                    parse_image(container, img_bytes)

                

            with col2:
                st.text_area(
                    label="Parsed Message",
                    value=st.session_state['parsed_text'] if 'parsed_text' in st.session_state else None,
                    height=400
                )


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
            st.button('Clear contents', on_click=clear_contents)  


            crop_image_tick = st.checkbox('Crop Image')
            
            if crop_image_tick:
                ## Cropper settings
                crop_box_color = st.color_picker(label="Crop Box Color", value='#0000FF')
            


    # Container for notification  
    container = st.container()

    # Columns
    col1, col2 = st.columns(2)
    


    # navigation for ocr
    ocr_navigation(
        uploaded_file,
        crop_image_tick,
        col1,
        col2,
        crop_box_color,
        parse_image_btn,
        container
    )




if __name__ == '__main__':
    main()