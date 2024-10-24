import streamlit as st
from PIL import Image
import datetime
import re
import os

allowed_image_types = ['webp']
#allowed_image_types = ['jpg', 'jpeg', 'png', 'webp']


# Function to validate email address
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Function to extract date and time from image metadata
def get_image_datetime(image_file):
    try:
        from PIL import ExifTags
        image = Image.open(image_file)
        exif_data = image._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                if ExifTags.TAGS.get(tag) == 'DateTimeOriginal':
                    return value
    except Exception as e:
        st.warning("Could not extract date from image metadata.")
    return None

# Streamlit app
st.sidebar.title("Input Form")

# 1. Image Selector
uploaded_file = st.sidebar.file_uploader("Upload an image", type=allowed_image_types)
image_datetime = None  # For storing date-time from image

if uploaded_file is not None:
    # Display the uploaded image
    image = Image.open(uploaded_file)
    st.sidebar.image(image, caption='Uploaded Image.', use_column_width=True)

    # Extract and display image date-time
    image_datetime = get_image_datetime(uploaded_file)
    print(f"[D] image date extracted as {image_datetime}")

# 2. Latitude Entry Box
latitude = st.sidebar.text_input("Latitude", "")
# 3. Longitude Entry Box
longitude = st.sidebar.text_input("Longitude", "")
# 4. Author Box with Email Address Validator
author_email = st.sidebar.text_input("Author Email")

if author_email and not is_valid_email(author_email):
    st.sidebar.error("Please enter a valid email address.")

if image_datetime is not None:
    time_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').time()
    date_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').date()
else:
    time_value = datetime.datetime.now().time()  # Default to current time
    date_value = datetime.datetime.now().date()

# 5. Date-Time Box

date_option = st.sidebar.date_input("Date", value=date_value)
time_option = st.sidebar.time_input("Time", time_value)



# Display submitted data
if st.sidebar.button("Upload"):
    st.write("Submitted Data:")
    st.write(f"Latitude: {latitude}")
    st.write(f"Longitude: {longitude}")
    st.write(f"Author Email: {author_email}")
    st.write(f"Date: {date_option}")
    st.write(f"Time: {time_option}")