import cx_Oracle
import mimetypes
from datetime import datetime,date
from azure.ai.formrecognizer import FormRecognizerClient , DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
import numpy as np
import re
import streamlit as st


# Access secrets
endpoint = st.secrets["api_credentials"]["endpoint"]
api_key = st.secrets["api_credentials"]["api_key"]

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

# Function to guess MIME type based on file extension
def get_mime_type(file_name):
    mime_type, _ = mimetypes.guess_type(file_name)
    return mime_type or "application/octet-stream"  # Default MIME type if unknown

def extract_birthday(id_number):

    # # Validate ID number length
    # if len(id_number) < 14:
    #     return "Invalid ID number: Too short"

    try:
        # Extract year with precise century determination
        year_digits = id_number[1:3]
        month_digits = id_number[3:5]
        day_digits = id_number[5:7]

        # Validate month and day
        month = min(max(int(month_digits), 1), 12)
        day = min(max(int(day_digits), 1), 31)

        # Century logic
        current_year = datetime.now().year
        year = int(year_digits)

        # Determine full year with more precise logic
        if year > 40:  # Assume 1900-1950 range
            full_year = 1900 + year
        else:  # Assume 2000-2050 range
            full_year = 2000 + year

        # Construct date with error handling
        birthday = datetime(full_year, month, day)

        return birthday.strftime("%Y-%m-%d")

    except ValueError:
        return "2000-01-01"


# ----------------- Api use


# Path to your file (can be a PDF, JPG, PNG, etc.)
file_path = r"C:\Users\dell\Downloads\test06.jpg"

# enable = st.checkbox("Open Camera")
# picture = st.camera_input("Take a picture", disabled=not enable)
# flag_camera= False
st.title('Egyptian ID Card Data Extractor')
st.write('Upload an Egyptian ID card image to extract information')
file_upload = st.file_uploader("Upload the Picture" , type=["jpg", "jpeg", "png", "gif"])
flag_upload = False

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



type = ["list", "OTM-PROJECT"]

# Display the list in a select box
selected_item = st.selectbox("Choose type:", type)
if selected_item:
    # Display the selected item
    print(f"You selected: {selected_item}")
else:st.write("Please Select type")
# Initialize edit_mode in session state if not already exists
if 'edit_mode' not in st.session_state:
    st.session_state.edit_mode = False

if file_upload:
    img = file_upload
    st.image(file_upload)
    mime_type = get_mime_type(file_upload.name)
    # Get the current date and time for last update
    last_update_date = datetime.now()
    # Read the uploaded file in binary mode
    img_bytes =file_upload.getvalue()
    print("mime_type",mime_type,"\nlast_update_date",last_update_date)
    # Reset session state when a new image is uploaded
    st.session_state.extracted_info = {
        'id': None,
        'factory_num': None,
        'first_name': None,
        'second_name': None,
        'address': None,
        'address2': None
    }

    # Analyze the document
    poller = document_analysis_client.begin_analyze_document("prebuilt-layout", img)
    layout_result = poller.result()

    # Process OCR lines
    process_ocr_lines(layout_result)

    # Always show extracted data initially
    st.subheader("Extracted Information")
    for key, value in st.session_state.extracted_info.items():
        st.write(f"{key.replace('_', ' ').title()}: {value}")

    # Edit button
    if st.button("Edit"):
        st.session_state.edit_mode = True

    # Edit mode
    if st.session_state.edit_mode:
        st.subheader("Edit Extracted Details")

        # Edit inputs persist and update session state directly
        for key in st.session_state.extracted_info.keys():
            st.session_state.extracted_info[key] = st.text_input(
                f"Edit {key.replace('_', ' ').title()}",
                value=st.session_state.extracted_info[key] or ""
            )

        # Save button
        if st.button("Save Changes"):
            st.success("Information updated successfully!")
            for key, value in st.session_state.extracted_info.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
        # Cancel button
        if st.button("Cancel"):
            st.session_state.edit_mode = False
    name=(st.session_state.extracted_info['first_name']+" "+st.session_state.extracted_info['second_name'])
    address=(st.session_state.extracted_info['address']+" "+st.session_state.extracted_info['address2'])
    # Get current date
    current_date = date.today()
    # Get current time
    current_time = datetime.now().time()
    print("Current Time:", current_time)
    print("Current Date:", current_date)

    birthday=extract_birthday(st.session_state.extracted_info['id'])

else:st.write("Please upload an image file")
# -------------------database

dsn = cx_Oracle.makedsn(
    host=st.secrets["api_credentials"]['host'],
    port=st.secrets["api_credentials"]['port'],
    service_name=st.secrets["api_credentials"]['sn']  # Replace with your service name
)


if st.button("Submit") and file_upload:
    try:
        # Establish the connection
        connection = cx_Oracle.connect(
            user=st.secrets["api_credentials"]['user'],
            password=st.secrets["api_credentials"]['pass'],
            dsn=dsn
        )

        print("Connected successfully!")

        # Create a cursor object
        cursor = connection.cursor()

        # SQL query to create the table
        create_table_query = """
        CREATE TABLE Extracted_ID (
            id NUMBER PRIMARY KEY,
            name VARCHAR2(100),
            address VARCHAR2(200),
            date_column DATE,
            stamp TIMESTAMP,
            img BLOB,
            mime_type VARCHAR2(100),        -- MIME type of the image (e.g., "image/jpeg")
            last_update_img DATE,           -- Last update date of the record
            created_by VARCHAR2(50),
            type VARCHAR2(50)
        )
        """
        sql_stat_old="""ALTER TABLE Extracted_ID
        ADD P_id number"""


        # SQL statement to insert data
        sql_stat = """
        INSERT INTO Extracted_ID (
            id,P_id,name, address, date_column, stamp, img, mime_type, last_update_img, created_by, type
        )
        VALUES (
            extracted_id_seq.NEXTVAL,:1, :2, :3, :4, :5, :6, :7, :8, :9, :10
        )
        """
        # # SQL statement to create a sequence
        # create_sequence_query = """
        # CREATE SEQUENCE extracted_id_seq
        #   START WITH 1
        #   INCREMENT BY 1
        #   NOCACHE
        # """
        #
        # # Execute the query
        # cursor.execute(create_sequence_query)

        # Print out all variables before insertion
        st.write(f"Inserting data: {id}, {name}, {address}, {birthday}, {current_time}, {mime_type}, {current_date}")

        # Explicitly handle potential None values
        data = (
            st.session_state.extracted_info['id'] or '',  # Provide default if None
            name or '',
            address or '',
            datetime.strptime(birthday, "%Y-%m-%d"),
            current_time,
            img_bytes,
            mime_type,
            current_date,
            " ",
            selected_item
        )
        # Execute the query
        cursor.execute(sql_stat, data)
        # Execute the query
        # cursor.execute(sql_stat)

        # Commit the transaction
        connection.commit()


    except cx_Oracle.DatabaseError as e:
        print(f"Database error: {e}")

    finally:
        # Close the cursor and connection
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
