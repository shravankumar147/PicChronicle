import os
import shutil
from datetime import datetime
from PIL import Image, ExifTags
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure these paths as needed
SOURCE_FOLDER = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\data\unorganized'
DESTINATION_FOLDER = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\data\organized'

# Create a geolocator instance for reverse geocoding
geolocator = Nominatim(user_agent="photo_organizer")

def get_exif_date(image_path):
    """Extract date from EXIF metadata, if available."""
    try:
        img = Image.open(image_path)
        exif_data = img._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                if tag_name == 'DateTimeOriginal':
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading EXIF data for {image_path}: {e}")
    return None

def get_file_date(image_path):
    """Get file creation/modification date as fallback."""
    try:
        timestamp = os.path.getctime(image_path) if os.name == 'nt' else os.path.getmtime(image_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"Error retrieving file date for {image_path}: {e}")
    return None

def get_best_date(image_path):
    """Return the best available date for an image."""
    return get_exif_date(image_path) or get_file_date(image_path)

def get_gps_coords(exif_data):
    """Extract GPS coordinates from EXIF data if available."""
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return None

    gps_data = {ExifTags.GPSTAGS.get(k, k): v for k, v in gps_info.items()}
    if {'GPSLatitude', 'GPSLatitudeRef', 'GPSLongitude', 'GPSLongitudeRef'}.issubset(gps_data):
        lat = get_decimal_from_dms(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef'])
        lon = get_decimal_from_dms(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
        return lat, lon
    return None

def get_decimal_from_dms(dms, ref):
    """Convert GPS DMS format to decimal degrees."""
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    return -decimal if ref in ['S', 'W'] else decimal

def reverse_geocode(coords):
    """Reverse geocode GPS coordinates to a city/region name."""
    try:
        location = geolocator.reverse(coords, timeout=10)
        if location and location.raw.get('address'):
            for key in ('city', 'town', 'village', 'county', 'state'):
                if key in location.raw['address']:
                    return location.raw['address'][key].replace(' ', '_')
    except GeocoderTimedOut:
        print(f"Geocoding timed out for {coords}")
    except Exception as e:
        print(f"Error during reverse geocoding: {e}")
    return None

def organize_image(image_path):
    """Process a single image: extract date and location, move to the right folder."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif() or {}
    except Exception as e:
        print(f"Cannot open {image_path}: {e}")
        return

    date_taken = get_best_date(image_path)
    if not date_taken:
        print(f"No date available for {image_path}, moving to 'Unknown_Date'")
        date_taken = datetime.now()
    
    year, month, day = date_taken.strftime('%Y'), date_taken.strftime('%m'), date_taken.strftime('%d')
    gps_coords = get_gps_coords(exif_data)
    location_folder = reverse_geocode(gps_coords) if gps_coords else ''

    dest_folder = os.path.join(DESTINATION_FOLDER, year, month, day, location_folder if location_folder else '')
    os.makedirs(dest_folder, exist_ok=True)

    try:
        filename = os.path.basename(image_path)
        destination_path = os.path.join(dest_folder, filename)
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
    """Check if a file is an image by extension."""
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))

def main():
    """Walk through the source folder and process each image file."""
    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if is_image_file(file):
                organize_image(os.path.join(root, file))

if __name__ == '__main__':
    main()