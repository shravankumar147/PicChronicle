import os
import shutil
import json
from datetime import datetime
from PIL import Image, ExifTags
import exifread
from fractions import Fraction

# Configure paths
SOURCE_FOLDER = r'D:\DCIM\100CANON'
DESTINATION_FOLDER = r'D:\DCIM\100CANON\organized'
METADATA_FILE = os.path.join(DESTINATION_FOLDER, "metadata.json")

SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp', '.cr3')
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov')

def load_existing_metadata():
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupt metadata.json file. Creating a new one.")
    return {"files": []}


import numbers
from fractions import Fraction

def convert_metadata_to_json_serializable(metadata):
    """Converts metadata dictionary to a JSON-serializable format."""
    def convert_value(value):
        if isinstance(value, bytes):  # Convert bytes to string
            return value.decode(errors="ignore")
        if isinstance(value, (Fraction, numbers.Rational)):  # Convert IFDRational and Fraction to float
            return float(value)
        if isinstance(value, dict):  # Recursively process dictionaries
            return {k: convert_value(v) for k, v in value.items()}
        if isinstance(value, list):  # Recursively process lists
            return [convert_value(v) for v in value]
        return value

    return {k: convert_value(v) for k, v in metadata.items()}

def save_metadata(metadata):
    """Saves metadata to JSON file after making it serializable."""
    json_serializable_metadata = convert_metadata_to_json_serializable(metadata)
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(json_serializable_metadata, f, indent=4)


def extract_exif(image):
    exif_data = {}
    try:
        info = image._getexif()
        if info:
            exif_data = {ExifTags.TAGS.get(tag, tag): value for tag, value in info.items()}
    except Exception as e:
        print(f"Error extracting EXIF data: {e}")
    return exif_data

def extract_cr3_exif(file_path):
    try:
        with open(file_path, 'rb') as f:
            tags = exifread.process_file(f)
            return {str(tag): str(value) for tag, value in tags.items()}
    except Exception as e:
        print(f"Error reading CR3 file {file_path}: {e}")
        return {}

def extract_date(exif_data, is_raw=False):
    date_key = 'EXIF DateTimeOriginal' if is_raw else 'DateTimeOriginal'
    try:
        if date_key in exif_data:
            return datetime.strptime(str(exif_data[date_key]), "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Date parsing error: {e}")
    return None

def get_file_date(file_path):
    try:
        timestamp = os.path.getctime(file_path) if os.name == 'nt' else os.path.getmtime(file_path)
        return datetime.fromtimestamp(timestamp)
    except Exception as e:
        print(f"File date error for {file_path}: {e}")
    return None

def organize_file(file_path, metadata):
    filename = os.path.basename(file_path)
    file_ext = os.path.splitext(filename)[1].lower()
    
    is_raw = file_ext == '.cr3'
    is_video = file_ext in SUPPORTED_VIDEO_EXTENSIONS
    
    exif_data = {}
    date_taken = None
    
    try:
        if is_raw:
            exif_data = extract_cr3_exif(file_path)
            date_taken = extract_date(exif_data, is_raw=True) or get_file_date(file_path)
        elif file_ext in SUPPORTED_IMAGE_EXTENSIONS:
            with Image.open(file_path) as img:
                exif_data = extract_exif(img)
                date_taken = extract_date(exif_data) or get_file_date(file_path)
        else:
            date_taken = get_file_date(file_path)  # For videos or unknown types
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return
    
    if not date_taken:
        print(f"No date available for {file_path}. Skipping.")
        return
    
    year, month, day = date_taken.strftime('%Y'), date_taken.strftime('%m'), date_taken.strftime('%d')
    category = 'raw' if is_raw else 'videos' if is_video else 'images'
    dest_folder = os.path.join(DESTINATION_FOLDER, year, month, day, category)
    os.makedirs(dest_folder, exist_ok=True)
    destination_path = os.path.join(dest_folder, filename)
    
    try:
        shutil.move(file_path, destination_path)
        metadata["files"].append({
            "filename": filename,
            "filepath": destination_path,
            "creation_date": date_taken.isoformat(),
            # "exif_data": exif_data,
            "file_type": category.upper()
        })
        print(f"Organized {file_path} -> {destination_path}")
    except Exception as e:
        print(f"Failed to move {file_path}: {e}")

def is_supported_file(filename):
    return filename.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS)

def main():
    metadata = load_existing_metadata()
    
    for root, _, files in os.walk(SOURCE_FOLDER):
        for file in files:
            if is_supported_file(file):
                organize_file(os.path.join(root, file), metadata)
    
    save_metadata(metadata)

if __name__ == '__main__':
    main()
    
    print("Finished organizing files.")