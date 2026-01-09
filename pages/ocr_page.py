import streamlit as st
import time
from streamlit_cropper import st_cropper
from PIL import Image

from utils.image_processing import pil_image_to_bytes, detect_text_from_bytes

def parse_image(container, file_bytes):
    with st.spinner("Parsing image...", show_time=True):
        time.sleep(1)
        parsed_text = detect_text_from_bytes(file_bytes)
    
    # Show success inside the top container
    container.success("Image successfully parsed!")
    st.session_state['parsed_text'] = parsed_text


def clear_contents():
    st.session_state.pop("parsed_text", None)


def main():
    """
    Page navigation for OCR page
    """


    with st.sidebar:
        uploaded_file = st.file_uploader(label="Choose an image",
                                        accept_multiple_files=False, 
                                        type=["jpg", "png"]
        )

        if uploaded_file:
            parse_image_btn = st.button('Parse image')   
            st.button('Clear contents', on_click=clear_contents)  

            ## Cropper settings
            crop_box_color = st.color_picker(label="Crop Box Color", value='#0000FF')
            


    # Container for notifications
    container = st.container()

    col1, col2 = st.columns(2)



    if uploaded_file:

        
        with col1:       


            img = Image.open(uploaded_file)

            # PIL image
            st.write('Set crop box')
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
        height=400
    )



if __name__ == '__main__':
    main()