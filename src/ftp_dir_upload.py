import os
import shutil
from ftplib import FTP
from dotenv import load_dotenv
from omegaconf import OmegaConf

# Load configuration and environment
config = OmegaConf.load("src/config.yaml")
load_dotenv()

# FTP credentials
FTP_HOST = os.getenv("FTP_HOST") if config.ftp.use_env_credentials else config.ftp.get("host")
FTP_USER = os.getenv("FTP_USER") if config.ftp.use_env_credentials else config.ftp.get("user")
FTP_PASS = os.getenv("FTP_PASS") if config.ftp.use_env_credentials else config.ftp.get("password")

# Folder paths
LOCAL_FOLDER = config.ftp.local_folder
REMOTE_FOLDER = config.ftp.remote_folder
TRASH_FOLDER = os.path.join(LOCAL_FOLDER, ".trash")

def move_to_trash(local_file):
    """Moves a file to .trash, preserving relative folder structure."""
    rel_path = os.path.relpath(local_file, LOCAL_FOLDER)
    
    # if not os.path.commonpath([LOCAL_FOLDER, local_file]).startswith(LOCAL_FOLDER): 
    #     raise ValueError("local_file is outside of LOCAL_FOLDER")

    if not is_within_folder(LOCAL_FOLDER, local_file):
        raise ValueError("local_file is outside of LOCAL_FOLDER")


    trash_file_path = os.path.join(TRASH_FOLDER, rel_path)
    os.makedirs(os.path.dirname(trash_file_path), exist_ok=True)

    try:
        shutil.move(local_file, trash_file_path)
        print(f"🧹 Moved to .trash: {rel_path}")
    except Exception as e:
        print(f"⚠️ Failed to move to trash: {rel_path}, Error: {e}")

def file_exists_on_ftp(ftp, remote_path):
    """Check if file exists on FTP server by listing the remote directory."""
    remote_dir = os.path.dirname(remote_path)
    file_name = os.path.basename(remote_path)

    try:
        ftp.cwd(remote_dir)
        files = ftp.nlst()
        return file_name in files
    except Exception:
        return False

def upload_file(ftp, local_file, remote_path):
    """Upload file if it doesn't exist, then move to .trash."""
    if file_exists_on_ftp(ftp, remote_path):
        print(f"⏩ Skipped (already exists): {remote_path}")
        return

    with open(local_file, "rb") as file:
        ftp.storbinary(f"STOR {remote_path}", file)
        print(f"✅ Uploaded: {local_file} -> {remote_path}")

    move_to_trash(local_file)

def ensure_remote_directory(ftp, remote_path):
    """Create remote directory path recursively if it doesn't exist."""
    dirs = remote_path.strip("/").split("/")
    path = ""
    for dir in dirs:
        path += f"/{dir}"
        try:
            ftp.cwd(path)
        except Exception:
            try:
                ftp.mkd(path)
                print(f"📂 Created directory: {path}")
            except Exception as e:
                print(f"⚠️ Failed to create remote directory: {path}, Error: {e}")

def upload_directory(ftp, local_folder, remote_folder):
    """Walk through local directory and upload all files."""
    for root, _, files in os.walk(local_folder):
        # Skip the .trash directory
        if TRASH_FOLDER in root:
            continue

        relative_path = os.path.relpath(root, LOCAL_FOLDER)
        remote_path = os.path.join(remote_folder, relative_path).replace("\\", "/")

        ensure_remote_directory(ftp, remote_path)

        for file in files:
            local_file = os.path.join(root, file)
            remote_file = f"{remote_path}/{file}"
            upload_file(ftp, local_file, remote_file)

def is_within_folder(base_folder, target_file):
    base_folder = os.path.abspath(os.path.normcase(os.path.normpath(base_folder)))
    target_file = os.path.abspath(os.path.normcase(os.path.normpath(target_file)))
    return os.path.commonpath([base_folder, target_file]) == base_folder

def main():
    """Main entrypoint."""
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        print(f"✅ Connected to FTP: {FTP_HOST}")

        os.makedirs(TRASH_FOLDER, exist_ok=True)
        upload_directory(ftp, LOCAL_FOLDER, REMOTE_FOLDER)

        ftp.quit()
        print("🎉 Upload completed. Files moved to .trash.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
