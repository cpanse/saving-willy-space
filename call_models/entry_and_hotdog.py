import streamlit as st
from PIL import Image
import datetime
import re
import os
import json

import hashlib

from transformers import pipeline
from transformers import AutoModelForImageClassification

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

allowed_image_types = ['webp']
#allowed_image_types = ['jpg', 'jpeg', 'png', 'webp']

#create cache object for the data dict
#@st.cache(allow_output_mutation=True)
#def FullInfo():
#    return {}

# initialize the data dict
if "full_data" not in st.session_state:
    st.session_state.full_data = {}






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

#full_data = FullInfo()

# Streamlit app
st.sidebar.title("Input Form")

# 1. Image Selector
uploaded_filename = st.sidebar.file_uploader("Upload an image", type=allowed_image_types)
image_datetime = None  # For storing date-time from image

if uploaded_filename is not None:
    # Display the uploaded image
    image = Image.open(uploaded_filename)
    st.sidebar.image(image, caption='Uploaded Image.', use_column_width=True)

    # Extract and display image date-time
    image_datetime = get_image_datetime(uploaded_filename)
    print(f"[D] image date extracted as {image_datetime}")

metadata = {
    "latitude": 23.5,
    "longitude": 44,
    "author_email": "super@whale.org",
    "date": None,
    "time": None,
}

# 2. Latitude Entry Box
latitude = st.sidebar.text_input("Latitude", metadata.get('latitude', ""))
# 3. Longitude Entry Box
longitude = st.sidebar.text_input("Longitude", metadata.get('longitude', ""))
# 4. Author Box with Email Address Validator
author_email = st.sidebar.text_input("Author Email", metadata.get('author_email', ""))

if author_email and not is_valid_email(author_email):   
    st.sidebar.error("Please enter a valid email address.")




# 5. date/time
## first from image metadata
if image_datetime is not None:
    time_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').time()
    date_value = datetime.datetime.strptime(image_datetime, '%Y:%m:%d %H:%M:%S').date()
else:
    time_value = datetime.datetime.now().time()  # Default to current time
    date_value = datetime.datetime.now().date()

## if not, give user the option to enter manually
date_option = st.sidebar.date_input("Date", value=date_value)
time_option = st.sidebar.time_input("Time", time_value)


# Display submitted data
if st.sidebar.button("Upload"):
    # create a dictionary with the submitted data
    submitted_data = {
        "latitude": latitude,
        "longitude": longitude,
        "author_email": author_email,
        "date": str(date_option),
        "time": str(time_option),
        "predicted_class": None,
        "image_filename": uploaded_filename.name if uploaded_filename else None,
        "image_md5": hashlib.md5(uploaded_filename.read()).hexdigest() if uploaded_filename else None,
        
    }
    #full_data.update(**submitted_data)
    for k, v in submitted_data.items():
        st.session_state.full_data[k] = v
        
    
    st.write("Submitted Data:")
    st.write(f"Latitude: {submitted_data['latitude']}")
    st.write(f"Longitude: {submitted_data['longitude']}")
    st.write(f"Author Email: {submitted_data['author_email']}")
    st.write(f"Date: {submitted_data['date']}")
    st.write(f"Time: {submitted_data['time']}")
    
    st.write(f"full dict of data: {json.dumps(submitted_data)}")
    
print(f"[D] full data: {st.session_state.full_data}")
    
if st.button("Get c`etacean- prediction")    :
    #pipe = pipeline("image-classification", model="Saving-Willy/cetacean-classifier", trust_remote_code=True)
    cetacean_classifier = AutoModelForImageClassification.from_pretrained("Saving-Willy/cetacean-classifier", trust_remote_code=True)
    st.title("Cetacean? Or Not?")
    if uploaded_filename is not None:
        col1, col2 = st.columns(2)

        # I think I'm repeating this, for now just let it slide. Fix after prototype 1 done
        image = Image.open(uploaded_filename)
        col1.image(image, use_column_width=True)
        out = cetacean_classifier(image) # get top 3
        
        
        print(out)        
        st.write(f"model outputs: {out} |{len(out)}")
  
    pass

if st.button("Get Hotdog Prediction"):   
    
    pipeline = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")
    st.title("Hot Dog? Or Not?")

    #file_name = st.file_uploader("Upload a hot dog candidate image")

    if uploaded_filename is not None:
        col1, col2 = st.columns(2)

        # I think I'm repeating this, for now just let it slide. Fix after prototype 1 done
        image = Image.open(uploaded_filename)
        col1.image(image, use_column_width=True)
        predictions = pipeline(image)

        col2.header("Probabilities")
        first = True
        for p in predictions:
            col2.subheader(f"{ p['label'] }: { round(p['score'] * 100, 1)}%")
            if first:
                st.session_state.full_data['predicted_class'] = p['label']
                st.session_state.full_data['predicted_score'] = round(p['score'] * 100, 1)
                first = False
        
        st.write(f"Submitted Data: {json.dumps(st.session_state.full_data)}")
        
print(f"[D] full data after inference: {st.session_state.full_data}")
        
        
