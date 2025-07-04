# PicChronicle

PicChronicle is a Python-based tool that automatically organizes your photos by extracting EXIF data to sort images into folders by year, month, and (when available) location. It uses reverse geocoding to convert GPS coordinates into city or region names, making it easy to browse and archive your memories. Additionally, it stores image metadata in JSON format, including detected objects, faces, and tags.

## Features

- **EXIF Data Extraction:** Reads image metadata to retrieve the date the photo was taken.
- **Automatic Folder Organization:** Creates a folder structure by year, month, and day.
- **Location-Based Categorization:** Uses reverse geocoding (via Nominatim) to further organize photos by city or region if GPS data is available.
- **Metadata Storage:** Stores image details in structured JSON format, including filename, creation date, location, detected objects, faces, and tags.
- **Duplicate Handling:** Renames files if a duplicate file name exists in the target directory.
- **Cross-Platform:** Works on Windows, macOS, and Linux.

## Prerequisites

- Python 3.6 or higher
- [Pillow](https://pypi.org/project/Pillow/) for image processing
- [geopy](https://pypi.org/project/geopy/) for reverse geocoding
- [face-recognition](https://pypi.org/project/face-recognition/) for face detection (optional)
- [imageai](https://pypi.org/project/imageai/) or [YOLO](https://pjreddie.com/darknet/yolo/) for object detection (optional)

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
   pip install Pillow geopy face-recognition imageai
   ```

## Usage

First run the script to organize your photos:

```bash
python picchronicle.py
```
Then run copy_media_for_cloud.py to copy your photos to the cloud ready, meaning it excludes raw files and other media that are not needed in the cloud.

```bash
python copy_media_for_cloud.py
```

Then run the ftp_upload.py script to upload the organized photos to your FTP server:

```bash
python ftp_upload.py
```

This will upload the organized photos to your FTP server, and remove local copies of the photos after successful upload, temporarily storing them in a local trash folder, for later deletion.



1. **Configure Paths:**

   Open the main script file (e.g., `picchronicle.py`) and set the `SOURCE_FOLDER` and `DESTINATION_FOLDER` variables to the paths of your image collection and where you want the organized photos to be stored.

2. **Run the Script:**

   ```bash
   python picchronicle.py
   ```

   The script will recursively scan the source folder, extract EXIF data from each image, and move them into a structured folder hierarchy while saving metadata in a JSON file.

## How It Works

- **Extracting EXIF Data:**  
  The script uses Pillow to read image metadata and extract the capture date (`DateTimeOriginal`) and GPS information.

- **Organizing by Date:**  
  It creates a folder structure in the format: `DESTINATION_FOLDER/<Year>/<Month>/<Date>`.

- **Reverse Geocoding for Location:**  
  If GPS coordinates are present, the script uses geopy's Nominatim service to convert the coordinates into a city or region name, further categorizing the images.

- **Metadata Storage:**  
  Each image's metadata, including filename, creation date, location, detected objects, faces, and tags, is stored in a structured JSON file.

## Visualization

Below is a visual representation of the image organization workflow:

<details>
  <summary>📌 Click to Expand Workflow Diagram (PNG)</summary>

  ![Workflow Diagram](assets/PicChronicle_FlowChart.png)

</details>

<details>
  <summary>📌 Click to Expand Workflow Diagram (Mermaid)</summary>

```mermaid
graph TD;
    A[Start] --> B[Scan Source Folder for Images]
    B --> C{Extract EXIF Data}
    C -->|Date Found| D[Organize by Year/Month/Day]
    C -->|No Date| E[Use File Creation Date]
    D & E --> F{Extract GPS Data}
    F -->|GPS Found| G[Reverse Geocode Location]
    F -->|No GPS| H[Store in 'Unknown Location']
    G --> I[Organize by City/Region]
    I & H --> J[Move to Destination Folder]
    J --> K[Store Metadata in JSON]
    J --> L[Perform Object & Face Detection]
    L --> M[Store Detected Objects/Faces]
    K & M --> N[Update Metadata Database]
    N --> O[End]
```
</details>

## Configuration

### Setting up Configuration Files

1. **Environment Variables (.env)**
   - Copy `src/.env.example` to `src/.env`
   - Update the values in `.env` with your FTP server credentials:
     ```
     FTP_HOST = "your.ftp.server"
     FTP_USER = "your_username"
     FTP_PASS = "your_password"
     ```
   - Optional: Configure SSL/TLS settings if using secure FTP

2. **Application Configuration (config.yaml)**
   - Copy `src/config.yaml.example` to `src/config.yaml`
   - Update the paths in `config.yaml`:
     ```yaml
     ftp:
       local_folder: "/path/to/your/local/photos"
       remote_folder: "/path/on/ftp/server"
       use_env_credentials: true
     ```
   - Set `use_env_credentials` to `true` to use credentials from `.env` file
   - Alternatively, set it to `false` and configure credentials directly in `config.yaml`

### Security Notes

- Never commit sensitive files to version control
- The following files are ignored by `.gitignore`:
  - `.env` and `config.yaml` (configuration files)
  - `*.pem`, `*.key`, `*.crt`, `*.csr` (SSL/TLS certificates)
  - `credentials.json` and other credential files
  - Log files and debug information
- Always use environment variables or secure secret management for sensitive data
- Keep your SSL/TLS certificates in a secure location
- Regularly rotate passwords and access credentials

## Contributing

Contributions are welcome! If you have ideas for improvements or find any issues, please open an issue or submit a pull request. When contributing, please follow the existing code style and include tests where applicable.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Pillow](https://pypi.org/project/Pillow/) for image processing.
- [geopy](https://pypi.org/project/geopy/) for geocoding services.
- OpenStreetMap Nominatim for reverse geocoding API.
- [face-recognition](https://pypi.org/project/face-recognition/) for face detection.
- [imageai](https://pypi.org/project/imageai/) for object detection.
