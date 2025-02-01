import os
import shutil
import json
from datetime import datetime
from PIL import Image, ExifTags
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Configure paths
SOURCE_FOLDER = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\data\unorganized'
DESTINATION_FOLDER = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\data\organized'
METADATA_FILE = os.path.join(DESTINATION_FOLDER, "metadata.json")

# Initialize geolocator
geolocator = Nominatim(user_agent="photo_organizer")

def load_existing_metadata():
    """Loads existing metadata from JSON file."""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupt metadata.json file. Creating a new one.")
    return {"images": []}

def save_metadata(metadata):
    """Saves metadata to JSON file."""
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4)

def get_exif_data(image):
    """Extracts EXIF metadata from an image."""
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            for tag, value in info.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                exif_data[decoded] = value
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
    return exif_data

def get_exif_date(image_path):
    """Extracts date from EXIF metadata if available."""
    try:
        with Image.open(image_path) as img:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    if tag_name == 'DateTimeOriginal':
                        return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"EXIF date error for {image_path}: {e}")
    return None

def get_file_date(image_path):
    """Gets file creation/modification date as a fallback."""
    try:
        timestamp = os.path.getctime(image_path) if os.name == 'nt' else os.path.getmtime(image_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"File date error for {image_path}: {e}")
    return None

def get_best_date(image_path):
    """Determines the best available date."""
    return get_exif_date(image_path) or get_file_date(image_path)

def get_decimal_from_dms(dms, ref):
    """Converts EXIF GPS coordinates to decimal format."""
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1]
    seconds = dms[2][0] / dms[2][1]
    decimal = degrees + (minutes / 60.0) + (seconds / 3600.0)
    return -decimal if ref in ['S', 'W'] else decimal

def get_gps_coords(exif_data):
    """Extracts GPS coordinates from EXIF metadata."""
    gps_info = exif_data.get('GPSInfo')
    if not gps_info:
        return None

    gps_data = {ExifTags.GPSTAGS.get(key, key): gps_info[key] for key in gps_info.keys()}
    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
        return (
            get_decimal_from_dms(gps_data['GPSLatitude'], gps_data['GPSLatitudeRef']),
            get_decimal_from_dms(gps_data['GPSLongitude'], gps_data['GPSLongitudeRef'])
        )
    return None

def reverse_geocode(coords):
    """Gets location name from coordinates."""
    try:
        location = geolocator.reverse(coords, timeout=10)
        if location and 'address' in location.raw:
            return location.raw['address'].get('city') or location.raw['address'].get('state')
    except GeocoderTimedOut:
        print("Geocoding timed out.")
    except Exception as e:
        print(f"Reverse geocoding error: {e}")
    return None

def organize_image(image_path, metadata):
    """Processes an image and stores its metadata."""
    try:
        with Image.open(image_path) as img:
            exif_data = get_exif_data(img)
    except Exception as e:
        print(f"Cannot open {image_path}: {e}")
        return

    # Determine the best date
    date_taken = get_best_date(image_path)
    if not date_taken:
        print(f"No date available for {image_path}. Skipping.")
        return

    year, month, day = date_taken.strftime('%Y'), date_taken.strftime('%m'), date_taken.strftime('%d')

    # Extract location
    gps_coords = get_gps_coords(exif_data)
    location_name = reverse_geocode(gps_coords) if gps_coords else "Unknown_Location"

    # Define destination folder
    dest_folder = os.path.join(DESTINATION_FOLDER, year, month, day, location_name)
    os.makedirs(dest_folder, exist_ok=True)

    # Move file to the destination
    filename = os.path.basename(image_path)
    destination_path = os.path.join(dest_folder, filename)
    shutil.move(image_path, destination_path)

    # Store metadata
    metadata["images"].append({
        "filename": filename,
        "filepath": destination_path,
        "creation_date": date_taken.isoformat(),
        "exif_data": {k: str(v) for k, v in exif_data.items() if isinstance(v, (str, int, float))},
        "location": {
            "latitude": gps_coords[0] if gps_coords else None,
            "longitude": gps_coords[1] if gps_coords else None,
            "city": location_name
        },
        "detected_objects": [],  # Placeholder for future ML-based object detection
        "faces_detected": [],  # Placeholder for face recognition
        "tags": []  # User-defined tags in future updates
    })

    print(f"Organized {image_path} -> {destination_path}")

def is_image_file(filename):
    """Checks if a file is an image based on extension."""
    return filename.lower().endswith(('.jpg', '.jpeg', '.png', '.tiff', '.bmp'))

def main():
    """Main function to process all images."""
    metadata = load_existing_metadata()

    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if is_image_file(file):
                organize_image(os.path.join(root, file), metadata)

    save_metadata(metadata)

if __name__ == '__main__':
    main()
