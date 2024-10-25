from PIL import Image
import datetime
import re
import os
import json
import hashlib
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium, folium_static
import folium


from transformers import pipeline
from transformers import AutoModelForImageClassification

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

USE_BASIC_MAP = False
allowed_image_types = ['webp']
#allowed_image_types = ['jpg', 'jpeg', 'png', 'webp']

tile_sets = [
    'Open Street Map',
    #'Stamen Terrain',
    #'Stamen Toner',
    'Esri Ocean',
    'Esri Images',
    'Stamen Watercolor',
    'CartoDB Positron',
    #'CartoDB Dark_Matter'
]


# initialize the data dict
if "full_data" not in st.session_state:
    st.session_state.full_data = {}

# initialize a log list in session state
if "log" not in st.session_state:
    st.session_state.log = st.table([f"{datetime.datetime.now()}", "- App started."])

# an arbitrary set of defaults so testing is less painful...
# ideally we add in some randomization to the defaults
metadata = {
    "latitude": 23.5,
    "longitude": 44,
    "author_email": "super@whale.org",
    "date": None,
    "time": None,
}

_map_data = {'name': {
    0: 'matterhorn',
  1: 'zinalrothorn',
  2: 'alphubel',
  3: 'allalinhorn',
  4: 'weissmies',
  5: 'lagginhorn',
  6: 'lenzspitze',
  10: 'strahlhorn',
  11: 'parrotspitze'},
 'lat': {0: 45.9764263,
  1: 46.0648271,
  2: 46.0628767,
  3: 46.0460858,
  4: 46.127633,
  5: 46.1570635,
  6: 46.1045505,
  10: 46.0131498,
  11: 45.9197881},
 'lon': {0: 7.6586024,
  1: 7.6901238,
  2: 7.8638549,
  3: 7.8945842,
  4: 8.0120569,
  5: 8.0031044,
  6: 7.8686568,
  10: 7.9021703,
  11: 7.8710552},
 'height': {0: 4181.0,
  1: 3944.0,
  2: 4174.0,
  3: 3940.0,
  4: 3983.0,
  5: 3916.0,
  6: 4255.0,
  10: 4072.0,
  11: 4419.0},
 'color': {0: '#aa0000',
  1: '#aa0000',
  2: '#aa0000',
  3: '#aa0000',
  4: '#aa0000',
  5: '#aa0000',
  6: '#aa0000',
  10: '#00aa00',
  11: '#aa0000'},
 'size': {0: 30, 1: 30, 2: 30, 3: 30, 4: 30, 5: 30, 6: 30, 10: 500, 11: 30}
}



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


# Define a function to create a map with the selected tile
def create_map2(tile_name, location):
    # can't get the tile layer to work so nicely, fall back to explicit
    # itle provider method
    if 'Positr' in tile_name:
        tile_xyz = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
        tile_attr = '<a href="https://opentopomap.org/">Open Topo Map</a>'
    
    elif 'Watercolor' in tile_name:
        #https://tiles.stadiamaps.com/tiles/{variant}/{z}/{x}/{y}.{ext}
        tile_xyz = 'https://tiles.stadiamaps.com/tiles/watercolor/{z}/{x}/{y}.jpg'
        tile_attr = '<a href="https://stadiamaps.com/">Stadia Maps</a>'
        
    elif 'Esri' in tile_name:
        tile_xyz = 'https://server.arcgisonline.com/ArcGIS/rest/services/{variant}/MapServer/tile/{z}/{y}/{x}'
        tile_attr = 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    
    else:
        tile_xyz = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
        tile_attr = '<a href="https://openstreetmap.org">Open Street Map</a>'
        
        
    m = folium.Map(location=visp_loc, zoom_start=9, 
                   tiles=tile_xyz, attr=tile_attr)
    return m

    


def create_map(tile_name, location):
    # https://xyzservices.readthedocs.io/en/stable/gallery.html 
    # get teh attribtuions from here once we pick the 2-3-4 options 
    m = folium.Map(location=location, zoom_start=7)

    attr = ""
    if tile_name == 'Open Street Map':
        #folium.TileLayer('openstreetmap').add_to(m)
        pass

    #Esri.OceanBasemap
    elif tile_name == 'Esri Ocean':
        attr = "Esri"
        folium.TileLayer('Esri.OceanBasemap', attr=attr).add_to(m)

    elif tile_name == 'Esri Images':
        attr = "Esri &mdash; Source: Esri, i-cubed, USDA"
        #folium.TileLayer('stamenterrain', attr=attr).add_to(m)
        folium.TileLayer('Esri.WorldImagery', attr=attr).add_to(m)
    elif tile_name == 'Stamen Toner':
        attr = "Stamen"
        folium.TileLayer('stamentoner', attr=attr).add_to(m)
    elif tile_name == 'Stamen Watercolor':
        attr = "Stamen"
        folium.TileLayer('Stadia.StamenWatercolor', attr=attr).add_to(m)
    elif tile_name == 'CartoDB Positron':
        folium.TileLayer('cartodb positron').add_to(m)
    elif tile_name == 'CartoDB Dark_Matter':
        folium.TileLayer('cartodb dark_matter').add_to(m)

    #folium.LayerControl().add_to(m)
    return m




# Streamlit app
tab_inference, tab_map, tab_data, tab_log = st.tabs(["Inference", "Map", "Data", "Log"])

#stat = st.info("Hello whale gang")
#st.session_state.log.add_rows([f"{datetime.datetime.now()}", "Hello whale gang."])
#with tab_log:


st.sidebar.title("Input image and data")

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

# 2. Latitude Entry Box
latitude = st.sidebar.text_input("Latitude", metadata.get('latitude', ""))
# 3. Longitude Entry Box
longitude = st.sidebar.text_input("Longitude", metadata.get('longitude', ""))
# 4. Author Box with Email Address Validator
author_email = st.sidebar.text_input("Author Email", metadata.get('author_email', ""))

if author_email and not is_valid_email(author_email):   
    st.sidebar.error("Please enter a valid email address.")


with tab_map:
    _df = pd.DataFrame(_map_data)
    st.markdown("# :whale: :whale: Cetaceans :red[& friends] :balloon:")
    show_points = st.toggle("Show Points", True)
    basic_map = st.toggle("Use Basic Map", False)
    
    visp_loc = 46.295833, 7.883333
    # do a default render (should just be once but streamlit passes many times?)
    #map_ = create_map('Esri Ocean', visp_loc)
    ## and render it
    #st_data = st_folium(map_, width=725)

    if basic_map:
        st.map(_df, latitude='lat', longitude='lon', color='color', size='size', zoom=7)
    else:
        # setup a dropdown to pick tiles
        # and render with folium instead
        selected_tile = st.selectbox("Choose a tile set", tile_sets)
        #st.info(f"Selected tile: {selected_tile}") 
        # don't get why the default selection doesn't get renderd.
        # generate a layer
        map_ = create_map(selected_tile, visp_loc)
        # and render it
        #tile_xyz = 'https://tile.opentopomap.org/{z}/{x}/{y}.png'
        #tile_attr = '<a href="https://opentopomap.org/">Open Topo Map</a>'

        if show_points:
            folium.Marker(
                location=visp_loc,
                popup="Visp",
                tooltip="Visp",
                icon=folium.Icon(color='blue', icon='info-sign')
            ).add_to(map_)
            
            for i, row in _df.iterrows():
                c = 'red'
                if row['name'] == 'strahlhorn':
                    c = 'green'
                kw = {"prefix": "fa", "color": c, "icon": "mountain-sun"}
                folium.Marker(
                    location=[row['lat'], row['lon']],
                    popup=f"{row['name']} ({row['height']} m)",
                    tooltip=row['name'],
                    icon=folium.Icon(**kw)
                ).add_to(map_)
                #st.info(f"Added marker for {row['name']} {row['lat']} {row['lon']}")

        
        #folium_static(map_)
        st_data = st_folium(map_, width=725)
                
                

with tab_log:
    #st.table(st.session_state.log)
    st.markdown("Coming soon! :construction:")
    
with tab_data:
    st.markdown("Coming later hope! :construction:")


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
        
    
    if 0: # ugly... 
        st.write("Submitted Data:")
        st.write(f"Latitude: {submitted_data['latitude']}")
        st.write(f"Longitude: {submitted_data['longitude']}")
        st.write(f"Author Email: {submitted_data['author_email']}")
        st.write(f"Date: {submitted_data['date']}")
        st.write(f"Time: {submitted_data['time']}")
        
    #st.write(f"full dict of data: {json.dumps(submitted_data)}")
    tab_inference.info(f"{st.session_state.full_data}")

    df = pd.DataFrame(submitted_data, index=[0])
    with tab_data:
        st.table(df)
    
    

#msg = f"[D] full data: {st.session_state.full_data}"
#print(msg)
#st.info(msg)
    
if tab_inference.button("Get cetacean- prediction")    :
    #pipe = pipeline("image-classification", model="Saving-Willy/cetacean-classifier", trust_remote_code=True)
    cetacean_classifier = AutoModelForImageClassification.from_pretrained("Saving-Willy/cetacean-classifier", trust_remote_code=True)
    tab_inference.title("Cetacean? Or Not?")
    if uploaded_filename is not None:
        col1, col2 = tab_inference.columns(2)

        # I think I'm repeating this, for now just let it slide. Fix after prototype 1 done
        image = Image.open(uploaded_filename)
        col1.image(image, use_column_width=True)
        out = cetacean_classifier(image) # get top 3
        
        
        print(out)        
        tab_inference.write(f"model outputs: {out} |{len(out)}")
  
    pass

if tab_inference.button("Get Hotdog Prediction"):   
    
    pipeline = pipeline(task="image-classification", model="julien-c/hotdog-not-hotdog")
    tab_inference.title("Hot Dog? Or Not?")

    #file_name = st.file_uploader("Upload a hot dog candidate image")

    if uploaded_filename is not None:
        col1, col2 = tab_inference.columns(2)

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
        
        tab_inference.write(f"Submitted Data: {json.dumps(st.session_state.full_data)}")
        
print(f"[D] full data after inference: {st.session_state.full_data}")
        
        
