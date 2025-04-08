import os
import shutil
import json
from datetime import datetime

# Configure paths
SOURCE_FOLDER = r'D:\DCIM\100CANON\organized'  # Your organized directory
DESTINATION_FOLDER = r'C:\Users\shravan\Documents\Personal\Photos'     # Change this to your desired destination
METADATA_FILE = os.path.join(SOURCE_FOLDER, "metadata.json")

# File extensions to include
SUPPORTED_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.tiff', '.bmp')
SUPPORTED_VIDEO_EXTENSIONS = ('.mp4', '.mov')

def load_metadata():
    """Load the existing metadata file if it exists"""
    if os.path.exists(METADATA_FILE):
        try:
            with open(METADATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print("Warning: Corrupt metadata.json file. Will copy based on file structure.")
    return None

def copy_from_metadata(metadata):
    """Copy files based on metadata entries"""
    if not metadata or "files" not in metadata:
        return False

    copied_count = 0
    skipped_count = 0
    
    print(f"Starting copy process using metadata file...")
    
    for file_info in metadata["files"]:
        if file_info.get("file_type") in ["IMAGES", "VIDEOS"]:  # Skip RAW files
            source_path = file_info.get("filepath")
            
            if os.path.exists(source_path):
                # Create relative path from SOURCE_FOLDER to maintain structure
                rel_path = os.path.relpath(os.path.dirname(source_path), SOURCE_FOLDER)
                dest_dir = os.path.join(DESTINATION_FOLDER, rel_path)
                os.makedirs(dest_dir, exist_ok=True)
                
                dest_path = os.path.join(dest_dir, os.path.basename(source_path))
                
                # Skip if file already exists at destination
                if os.path.exists(dest_path):
                    print(f"Skipping existing file: {dest_path}")
                    skipped_count += 1
                    continue
                
                try:
                    shutil.copy2(source_path, dest_path)  # copy2 preserves metadata
                    copied_count += 1
                    print(f"Copied: {source_path} -> {dest_path}")
                except Exception as e:
                    print(f"Error copying {source_path}: {e}")
    
    print(f"Metadata-based copy complete. Copied {copied_count} files, skipped {skipped_count} existing files.")
    return True

def copy_by_directory_structure():
    """Copy files by traversing directory structure"""
    copied_count = 0
    skipped_count = 0
    
    print(f"Starting copy process by directory structure...")
    
    for root, dirs, files in os.walk(SOURCE_FOLDER):
        # Skip raw directories
        if "raw" in os.path.basename(root).lower():
            continue
            
        for file in files:
            # Skip metadata file and non-media files
            if file == "metadata.json" or not file.lower().endswith(SUPPORTED_IMAGE_EXTENSIONS + SUPPORTED_VIDEO_EXTENSIONS):
                continue
                
            source_path = os.path.join(root, file)
            
            # Create relative path from SOURCE_FOLDER to maintain structure
            rel_path = os.path.relpath(root, SOURCE_FOLDER)
            dest_dir = os.path.join(DESTINATION_FOLDER, rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            
            dest_path = os.path.join(dest_dir, file)
            
            # Skip if file already exists at destination
            if os.path.exists(dest_path):
                print(f"Skipping existing file: {dest_path}")
                skipped_count += 1
                continue
            
            try:
                shutil.copy2(source_path, dest_path)  # copy2 preserves metadata
                copied_count += 1
                print(f"Copied: {source_path} -> {dest_path}")
            except Exception as e:
                print(f"Error copying {source_path}: {e}")
    
    print(f"Directory-based copy complete. Copied {copied_count} files, skipped {skipped_count} existing files.")

def main():
    # Create destination folder if it doesn't exist
    os.makedirs(DESTINATION_FOLDER, exist_ok=True)
    
    print(f"Source folder: {SOURCE_FOLDER}")
    print(f"Destination folder: {DESTINATION_FOLDER}")
    
    # Try to use metadata file first
    metadata = load_metadata()
    metadata_copy_success = False
    
    if metadata:
        metadata_copy_success = copy_from_metadata(metadata)
    
    # Fall back to directory structure if metadata approach fails
    if not metadata_copy_success:
        print("Using directory structure method...")
        copy_by_directory_structure()
    
    print("Copy operation completed.")

if __name__ == "__main__":
    main()