import time
import subprocess
import psutil
import os
import hashlib
from datetime import datetime

# === CONFIG ===
TARGET_DRIVE = 'D:\\'
WATCH_PATH = os.path.join(TARGET_DRIVE, 'DCIM')  # Update to actual folder
SCRIPT_PATH = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\run_all.py'
VENV_PYTHON = r'C:\Users\shravan\Documents\Python_Scripts\PicChronicle\venv\Scripts\python.exe'
HASH_RECORD_FILE = 'usb_file_hashes.txt'
SCAN_INTERVAL = 3

# === CATEGORIES ===
EXT_CATEGORIES = {
    "Images": ['.jpg', '.jpeg', '.png'],
    "RAW": ['.cr2', '.nef', '.arw', '.rw2', '.orf'],
    "Videos": ['.mp4', '.mov', '.avi', '.mkv'],
}

# === HELPERS ===
def drive_connected():
    return TARGET_DRIVE in [part.device for part in psutil.disk_partitions()]

def compute_file_hash(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def get_file_hashes(folder):
    file_hashes = {}
    for root, _, files in os.walk(folder):
        for file in files:
            path = os.path.join(root, file)
            hash_val = compute_file_hash(path)
            if hash_val:
                file_hashes[path] = hash_val
    return file_hashes

def load_previous_hashes():
    if not os.path.exists(HASH_RECORD_FILE):
        return {}
    with open(HASH_RECORD_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return dict(line.strip().split('::') for line in lines if '::' in line)

def save_current_hashes(hashes):
    with open(HASH_RECORD_FILE, 'w', encoding='utf-8') as f:
        for path, hash_val in hashes.items():
            f.write(f"{path}::{hash_val}\n")

def get_extension_category(ext):
    ext = ext.lower()
    for category, extensions in EXT_CATEGORIES.items():
        if ext in extensions:
            return category
    return "Other"

def classify_new_files(current_hashes, previous_hashes):
    new_files = {path: hash for path, hash in current_hashes.items()
                 if path not in previous_hashes or previous_hashes[path] != hash}
    
    stats = {"Images": 0, "RAW": 0, "Videos": 0, "Other": 0}
    for path in new_files:
        ext = os.path.splitext(path)[1]
        category = get_extension_category(ext)
        stats[category] += 1
    return new_files, stats

# === MAIN ===
def main():
    print("🔍 Watching for USB insertion + new files...")
    already_connected = False

    while True:
        time.sleep(SCAN_INTERVAL)
        connected = drive_connected()

        if connected and not already_connected:
            print(f"📥 USB detected at {TARGET_DRIVE}")
            if os.path.exists(WATCH_PATH):
                current_hashes = get_file_hashes(WATCH_PATH)
                previous_hashes = load_previous_hashes()
                new_files, stats = classify_new_files(current_hashes, previous_hashes)

                if new_files:
                    print(f"\n📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"🆕 {len(new_files)} new/modified files found:")
                    for cat, count in stats.items():
                        if count > 0:
                            print(f"  - {cat}: {count}")
                    
                    confirm = input("\n❓ Do you want to run run_all.py now? (y/n): ").strip().lower()
                    if confirm == 'y':
                        subprocess.run([VENV_PYTHON, SCRIPT_PATH])
                        save_current_hashes(current_hashes)
                        print("✅ Script executed.")
                    else:
                        print("❌ Skipped script execution.")
                else:
                    print("✅ No new files found.")
            else:
                print(f"⚠️ Folder not found: {WATCH_PATH}")

            already_connected = True

        elif not connected and already_connected:
            print("📤 USB removed.")
            already_connected = False

if __name__ == "__main__":
    main()
