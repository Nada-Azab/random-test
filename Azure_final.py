from azure.ai.formrecognizer import FormRecognizerClient , DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import cv2
import numpy as np
import streamlit as st


# Replace with your Form Recognizer endpoint and API key
endpoint = "https://textextraction01.cognitiveservices.azure.com/"
api_key = "9xK9bARgn3Ox6OYYwSVLkwOFRxNUrHBPeoox0YR9PBOQ57NMfhWxJQQJ99BAACrIdLPXJ3w3AAALACOGpDfI"

# pass images with :
# flash : snaa
# rotated : smsm
# bad quilty : moh basuniy
# not clip :
document_analysis_client = DocumentAnalysisClient(endpoint=endpoint, credential=AzureKeyCredential(api_key))

# helpers

def has_arabic_with_diacritics(text):
    """
    Check if text contains Arabic letters with diacritical marks (تشكيل).
    Args:
        text (str): The text to check
    Returns:
        bool: True if text contains Arabic letters with diacritics, False otherwise
    """
    # Arabic diacritical marks (تشكيل)
    arabic_diacritics = [
        '\u064B',  # Fathatan
        '\u064C',  # Dammatan
        '\u064D',  # Kasratan
        '\u064E',  # Fatha
        '\u064F',  # Damma
        '\u0650',  # Kasra
        '\u0651',  # Shadda
        '\u0652',  # Sukun
    ]

    # Arabic letter range
    arabic_letter_start = '\u0621'  # ء
    arabic_letter_end = '\u064A'  # ي

    has_arabic = False
    has_diacritics = False

    for char in text:
        # Check if character is an Arabic letter
        if arabic_letter_start <= char <= arabic_letter_end:
            has_arabic = True
        # Check if character is a diacritical mark
        if char in arabic_diacritics:
            has_diacritics = True

        # If we found both Arabic letters and diacritics, we can return True
        if has_arabic and has_diacritics:
            return True

    return False

# Example usage
# test_cases = [
#     "مرحبا",  # Arabic without diacritics
#     "مَرْحَبًا",  # Arabic with diacritics
#     "Hello world",  # English only
#     "مرحبا world",  # Mixed without diacritics
#     "مَرْحَبًا world",  # Mixed with diacritics
# ]

# for text in test_cases:
#     result = has_arabic_with_diacritics(text)
#     print(f"Text: {text}")
#     print(f"Has Arabic with diacritics: {result}\n")
import re


def check_text_type_with_len(text):
    """
    Check the type of text based on Arabic/English characters and numbers, and return the length of the text.

    Args:
        text (str): The input string to check.

    Returns:
        tuple: A tuple containing the type of text ("ara", "ara_num", "eng_num", "eng_mix", "ara_mix", or "unknown")
               and the length of the text.
    """
    # Define regex patterns
    arabic_char_pattern = re.compile(r'[\u0600-\u06FF\u0750-\u077F]+')  # Arabic characters
    arabic_num_pattern = re.compile(r'[\u0660-\u0669]+')  # Arabic numbers (٠-٩)
    english_num_pattern = re.compile(r'[0-9]+')  # English numbers (0-9)
    english_char_pattern = re.compile(r'[A-Za-z]+')  # English letters

    # Remove spaces from the text for classification
    text = text.replace(" ", "")

    # Check for Arabic characters
    has_arabic_chars = bool(arabic_char_pattern.search(text))
    # Check for Arabic numbers
    has_arabic_nums = bool(arabic_num_pattern.search(text))
    # Check for English numbers
    has_english_nums = bool(english_num_pattern.search(text))
    # Check for English characters
    has_english_chars = bool(english_char_pattern.search(text))

    # Determine the type of text
    if has_arabic_chars and has_arabic_nums:
        text_type = "ara_mix"  # Mixed Arabic characters and numbers
    elif has_arabic_chars:
        text_type = "ara"  # Arabic characters only
    elif has_arabic_nums:
        text_type = "ara_num"  # Arabic numbers only
    elif has_english_nums and has_english_chars:
        text_type = "eng_mix"  # Mixed English characters and numbers
    elif has_english_nums:
        text_type = "eng_num"  # English numbers only
    elif has_english_chars:
        text_type = "eng"  # English characters only
    else:
        text_type = "unknown"  # Unknown or other characters

    # Return the text type and the length of the text
    return text_type, len(text)


def sort_ocr_lines(lines):
    # Sort lines using their top coordinate
    def get_top_coordinate(line):
        try:
            # Try different potential attributes for getting position
            if hasattr(line, 'polygon'):
                return line.polygon[1].y  # If polygon is available
            elif hasattr(line, 'boundingBox'):
                return line.boundingBox[1]  # Alternative attribute name
            elif hasattr(line, 'bbox'):
                return line.bbox[1]  # Another possible attribute
            else:
                # If no position attribute is found, use index as fallback
                return lines.index(line)
        except Exception as e:
            print(f"Error sorting line: {e}")
            return lines.index(line)

    # Sort lines based on top coordinate
    return sorted(lines, key=get_top_coordinate)




# ----------------- Api use


# Path to your file (can be a PDF, JPG, PNG, etc.)
file_path = r"C:\Users\dell\Downloads\test06.jpg"

# enable = st.checkbox("Open Camera")
# picture = st.camera_input("Take a picture", disabled=not enable)
# flag_camera= False
st.title('Egyptian ID Card Data Extractor')
st.write('Upload an Egyptian ID card image to extract information')
file_upload = st.file_uploader("Upload the Picture")
flag_upload= False

extracted_info = {
    'id': None,
    'factory_num': None,
    'first_name': None,
    'second_name': None,
    'address': None,
    'address2': None
}


# Function to process OCR lines and extract information
def process_ocr_lines(layout_result):
    sorted_page_lines = sort_ocr_lines(layout_result.pages[0].lines)

    for line in sorted_page_lines:
        result = has_arabic_with_diacritics(line.content)
        text_type, len_text = check_text_type_with_len(line.content)

        # Skip unwanted lines
        if result or ('بطاقة' in line.content) or ('الشخصية' in line.content) or ('/' in line.content):
            continue

        # Extract information logic
        if not st.session_state.extracted_info['id'] and text_type == 'ara_mix' and len_text == 14:
            st.session_state.extracted_info['id'] = line.content

        elif not st.session_state.extracted_info['factory_num'] and text_type == 'eng_mix' and len_text > 5:
            st.session_state.extracted_info['factory_num'] = line.content

        elif not st.session_state.extracted_info['first_name'] and text_type == 'ara' and len_text < 10:
            st.session_state.extracted_info['first_name'] = line.content

        elif not st.session_state.extracted_info['second_name'] and text_type == 'ara' and len_text > 9:
            st.session_state.extracted_info['second_name'] = line.content

        elif not st.session_state.extracted_info['address'] and (
                text_type == 'ara_mix' or text_type == 'ara') and len_text >= 5:
            st.session_state.extracted_info['address'] = line.content

        elif not st.session_state.extracted_info['address2'] and (
                text_type == 'ara_mix' or text_type == 'ara') and len_text >= 5:
            st.session_state.extracted_info['address2'] = line.content

        # Break if all information is extracted
        if all(st.session_state.extracted_info.values()):
            break


# if picture :
#     # flag_camera=True
#     img=picture
#     st.image(picture)
if file_upload:
    img= file_upload
    st.image(file_upload)
    # Analyze the document using the layout model
    # with open(file_upload, "rb") as id_image_file:
    # Reset session state when new image is uploaded
    st.session_state.extracted_info = {
        'id': None,
        'factory_num': None,
        'first_name': None,
        'second_name': None,
        'address': None,
        'address2': None
    }

    # st.session_state.edit_mode = False
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", img)
    layout_result = poller.result()
    flag_save = False


    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False

    # # Process OCR lines if not already processed
    # if st.button("Extract Information"):

    process_ocr_lines(layout_result)
    edit_btn=st.button("Edit")
    # Edit mode toggle
    if edit_btn:
        st.session_state.edit_mode = True

    # Display or Edit mode
    if st.session_state.edit_mode:
        st.subheader("Edit Extracted Details")

        # Use session state for edited info to persist across reruns
        for key in st.session_state.extracted_info.keys():
            st.session_state.extracted_info[key] = st.text_input(
                f"Edit {key.replace('_', ' ').title()}",
                value=st.session_state.extracted_info[key] or ""
            )

        # Save and Cancel columns
        col1, col2 = st.columns([6, 1])

        with col1:
            save_btn=st.button("Save Changes")
            if save_btn:
                st.success("Information updated successfully!")
                st.session_state.edit_mode = False
                flag_save=True
        with col2:
            if st.button("Cancel"):
                st.session_state.edit_mode = False

    # Display information
    if st.session_state.edit_mode == False or flag_save :
        st.subheader("Final Information")
        for key, value in st.session_state.extracted_info.items():
            st.write(f"{key.replace('_', ' ').title()}: {value}")
            st.session_state.edit_mode = True
