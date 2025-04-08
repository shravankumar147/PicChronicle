import os
from ftplib import FTP
from dotenv import load_dotenv
from omegaconf import OmegaConf

# Load Configurations
config = OmegaConf.load("config.yaml")

# Load environment variables
load_dotenv()

# FTP Server Configuration
FTP_HOST = os.getenv("FTP_HOST") if config.ftp.use_env_credentials else config.ftp.get("host")
FTP_USER = os.getenv("FTP_USER") if config.ftp.use_env_credentials else config.ftp.get("user")
FTP_PASS = os.getenv("FTP_PASS") if config.ftp.use_env_credentials else config.ftp.get("password")

LOCAL_FOLDER = config.ftp.local_folder
REMOTE_FOLDER = config.ftp.remote_folder

def upload_file(ftp, local_file, remote_path):
    """Uploads a single file to the FTP server."""
    with open(local_file, "rb") as file:
        ftp.storbinary(f"STOR {remote_path}", file)
        print(f"✅ Uploaded: {local_file} -> {remote_path}")

def ensure_remote_directory(ftp, remote_path):
    """Creates remote directories if they don’t exist."""
    dirs = remote_path.strip("/").split("/")
    path = ""
    for dir in dirs:
        path += f"/{dir}"
        try:
            ftp.cwd(path)
        except:
            ftp.mkd(path)
            print(f"📂 Created directory: {path}")

def upload_directory(ftp, local_folder, remote_folder):
    """Recursively uploads all files in a local folder to the FTP server."""
    for root, _, files in os.walk(local_folder):
        relative_path = os.path.relpath(root, LOCAL_FOLDER)
        remote_path = os.path.join(remote_folder, relative_path).replace("\\", "/")
        
        ensure_remote_directory(ftp, remote_path)

        for file in files:
            local_file = os.path.join(root, file)
            remote_file = f"{remote_path}/{file}"
            upload_file(ftp, local_file, remote_file)

def main():
    """Main function to connect and transfer files."""
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"✅ Connected to FTP: {FTP_HOST}")

        upload_directory(ftp, LOCAL_FOLDER, REMOTE_FOLDER)
        
        ftp.quit()
        print("🎉 All files uploaded successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
