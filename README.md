# PicChronicle

PicChronicle is a Python-based tool that automatically organizes your photos by extracting EXIF data to sort images into folders by year, month, and (when available) location. It uses reverse geocoding to convert GPS coordinates into city or region names, making it easy to browse and archive your memories.

## Features

- **EXIF Data Extraction:** Reads image metadata to retrieve the date the photo was taken.
- **Automatic Folder Organization:** Creates a folder structure by year and month.
- **Location-Based Categorization:** Uses reverse geocoding (via Nominatim) to further organize photos by city or region if GPS data is available.
- **Duplicate Handling:** Renames files if a duplicate file name exists in the target directory.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## Prerequisites

- Python 3.6 or higher
- [Pillow](https://pypi.org/project/Pillow/) for image processing
- [geopy](https://pypi.org/project/geopy/) for reverse geocoding

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/PicChronicle.git
   cd PicChronicle
   ```

2. **Create a Virtual Environment (Optional but Recommended):**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   Alternatively, install dependencies manually:

   ```bash
   pip install Pillow geopy
   ```

## Usage

1. **Configure Paths:**

   Open the main script file (e.g., `picchronicle.py`) and set the `SOURCE_FOLDER` and `DESTINATION_FOLDER` variables to the paths of your image collection and where you want the organized photos to be stored.

2. **Run the Script:**

   ```bash
   python picchronicle.py
   ```

   The script will recursively scan the source folder, extract EXIF data from each image, and move them into a structured folder hierarchy.

## How It Works

- **Extracting EXIF Data:**  
  The script uses Pillow to read image metadata and extract the capture date (`DateTimeOriginal`) and GPS information.

- **Organizing by Date:**  
  It creates a folder structure in the format: `DESTINATION_FOLDER/<Year>/<Month>/`.

- **Reverse Geocoding for Location:**  
  If GPS coordinates are present, the script uses geopy's Nominatim service to convert the coordinates into a city or region name, further categorizing the images.

## Contributing

Contributions are welcome! If you have ideas for improvements or find any issues, please open an issue or submit a pull request. When contributing, please follow the existing code style and include tests where applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pillow](https://pypi.org/project/Pillow/) for image processing.
- [geopy](https://pypi.org/project/geopy/) for geocoding services.
- OpenStreetMap Nominatim for reverse geocoding API.
