import os
import shutil
from datetime import datetime
from PIL import Image, ExifTags
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure these paths as needed
SOURCE_FOLDER = r'data\unorganized'
DESTINATION_FOLDER = r'data\organized'

# Create a geolocator instance for reverse geocoding (using OpenStreetMap's Nominatim)
geolocator = Nominatim(user_agent="photo_organizer")

def get_exif_data(image):
    """
    Extracts EXIF data from an image and returns a dictionary with human-readable tags.
    """
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = ExifTags.TAGS.get(tag, tag)
            exif_data[decoded] = value
    return exif_data

def get_date_taken(exif_data):
    """
    Returns a datetime object from the 'DateTimeOriginal' EXIF tag, if available.
    """
    date_str = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
    if date_str:
        try:
            return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
        except ValueError:
            return None
    return None

def get_file_creation_date(image_path):
    """Get file creation or modification date as fallback"""
    try:
        timestamp = os.path.getmtime(image_path)  # Modification time as fallback
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"Error retrieving date for {image_path}: {e}")
        return None

def get_decimal_from_dms(dms, ref):
    """
    Converts GPS coordinates stored in EXIF to decimal format.
    """
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    if ref in ['S', 'W']:
        decimal = -decimal
    return decimal

def get_gps_coords(exif_data):
    """
    Extracts GPS coordinates (latitude and longitude) from EXIF data if available.
    """
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return None

    gps_data = {}
    for key in gps_info.keys():
        decoded = ExifTags.GPSTAGS.get(key, key)
        gps_data[decoded] = gps_info[key]

    if 'GPSLatitude' in gps_data and 'GPSLatitudeRef' in gps_data and \
       'GPSLongitude' in gps_data and 'GPSLongitudeRef' in gps_data:
        lat = get_decimal_from_dms(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef'])
        lon = get_decimal_from_dms(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
        return (lat, lon)
    return None

def reverse_geocode(coords):
    """
    Uses geopy to reverse geocode GPS coordinates to a city/region name.
    Returns a string (e.g., "New York") if available, or None otherwise.
    """
    try:
        location = geolocator.reverse(coords, timeout=10)
        if location and location.raw and 'address' in location.raw:
            address = location.raw['address']
            # Try to obtain the city, town, or county.
            for key in ('city', 'town', 'village', 'county', 'state'):
                if key in address:
                    return address[key].replace(' ', '_')  # Replace spaces with underscores for folder names
    except GeocoderTimedOut:
        print("Geocoding timed out for coordinates:", coords)
    except Exception as e:
        print("Error during reverse geocoding:", e)
    return None

def organize_image(image_path):
    """
    Processes a single image: extracts date and GPS info, then moves it into the corresponding folder.
    """
    try:
        with Image.open(image_path) as img:
            exif_data = get_exif_data(img)
    except Exception as e:
        print(f"Cannot open {image_path}: {e}")
        return

    # Determine the capture date
    date_taken = get_date_taken(exif_data)  # Your existing EXIF extraction function
    if date_taken is None:
        date_taken = get_file_creation_date(image_path)  # Use fallback

    if not date_taken:
        print(f"No date information for {image_path}. Skipping...")
        return
    
    year = date_taken.strftime('%Y')
    month = date_taken.strftime('%m')
    date = date_taken.strftime('%d')

    # Determine location if available
    gps_coords = get_gps_coords(exif_data)
    location_folder = ''
    if gps_coords:
        location_name = reverse_geocode(gps_coords)
        if location_name:
            location_folder = location_name

    # Build the destination folder path
    dest_folder = os.path.join(DESTINATION_FOLDER, year, month, date)
    if location_folder:
        dest_folder = os.path.join(dest_folder, location_folder)

    # Create the destination folder if it does not exist
    os.makedirs(dest_folder, exist_ok=True)

    # Move the file
    try:
        filename = os.path.basename(image_path)
        destination_path = os.path.join(dest_folder, filename)
        # If a file with the same name exists, modify the filename
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(destination_path):
            destination_path = os.path.join(dest_folder, f"{base}_{counter}{ext}")
            counter += 1

        shutil.move(image_path, destination_path)
        print(f"Moved {image_path} -> {destination_path}")
    except Exception as e:
        print(f"Error moving {image_path}: {e}")

def is_image_file(filename):
    """
    Checks if a file is an image based on its extension.
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    return any(filename.lower().endswith(ext) for ext in image_extensions)

def main():
    # Walk through the source folder and process each image file
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if is_image_file(file):
                image_path = os.path.join(root, file)
                organize_image(image_path)

if __name__ == '__main__':
    main()
