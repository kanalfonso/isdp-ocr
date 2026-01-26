from google.cloud import vision
from google.oauth2.service_account import Credentials
import streamlit as st
from streamlit_cropper import st_cropper

import io
from PIL import Image

def pil_image_to_bytes(img: Image.Image, format="PNG") -> bytes:
    buffer = io.BytesIO()
    img.save(buffer, format=format)
    return buffer.getvalue()



def detect_text_from_path(path):
    """
    Detect text using Cloud Vision API by passing image path
    """
    
    # pass credentials
    credentials = Credentials.from_service_account_info(st.secrets['service_account_credentials'],
                                            scopes=['https://www.googleapis.com/auth/cloud-platform'])
    

    # instantiate client by passing credentials
    client = vision.ImageAnnotatorClient(credentials=credentials)
    
    
    with open(path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    
    if response.full_text_annotation:
        return response.full_text_annotation.text

    return "None"



def detect_text_from_bytes(bytes):
    """
    Detect text using Cloud Vision API by passing image path
    """
    
    # pass credentials
    credentials = Credentials.from_service_account_info(st.secrets['service_account_credentials'],
                                            scopes=['https://www.googleapis.com/auth/cloud-platform'])
    

    client = vision.ImageAnnotatorClient(credentials=credentials)

    image = vision.Image(content=bytes)
    response = client.text_detection(image=image)

    if response.full_text_annotation:
        return response.full_text_annotation.text

    return "None"






# # Replace 'PATH_TO_YOUR_IMAGE' with the path to the image file you want to analyze.
# detect_text_from_path('sms_screenshot/image_2.png')

def main():
    # 1. Open original image
    img = Image.open("sms_screenshot/image_1.png")

    # 2. Convert to bytes
    bytes = pil_image_to_bytes(img)


    # st cropper
    cropped_img, crop_box = st_cropper(img, return_type="both")

    print('hello')

if __name__ == '__main__':
    main()