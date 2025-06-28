import os
import time
import yaml
from ftplib import FTP, error_perm, all_errors
from dotenv import load_dotenv

# === Load credentials and config ===
load_dotenv()

with open("src/config.yaml", "r") as f:
    config = yaml.safe_load(f)
ftp_config = config.get("mobile_ftp", {})

FTP_HOST = os.getenv("MOBILE_FTP_HOST")
FTP_PORT = int(os.getenv("MOBILE_FTP_PORT", "21"))
FTP_USER = os.getenv("MOBILE_FTP_USER")
FTP_PASS = os.getenv("MOBILE_FTP_PASS")

LOCAL_FOLDER = ftp_config.get("local_folder", ".")
REMOTE_ROOT = ftp_config.get("remote_root", "/")

# === Enable/Disable dry run (True = no uploads) ===
DRY_RUN = True
# === FTP passive mode (try toggling if issues occur) ===
USE_PASSIVE_MODE = True
# === Retry attempts on connection issues ===
MAX_RETRIES = 3


def ensure_ftp_path(ftp, path):
    """Ensure directory path exists on FTP server."""
    for part in path.strip("/").split("/"):
        try:
            if part not in ftp.nlst():
                if DRY_RUN:
                    print(f"🧪 [Dry Run] Would create directory: {part}")
                else:
                    ftp.mkd(part)
                    print(f"📂 Created: {part}")
            ftp.cwd(part)
        except error_perm as e:
            if not str(e).startswith("550"):
                raise
            print(f"⚠️  Cannot create or access '{part}': {e}")


def connect_ftp():
    """Try connecting to FTP server with retries."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔌 Attempt {attempt}: Connecting to {FTP_HOST}:{FTP_PORT}...")
            ftp = FTP()
            ftp.connect(FTP_HOST, FTP_PORT, timeout=10)
            print("🔐 Connected. Logging in...")
            ftp.login(FTP_USER, FTP_PASS)
            ftp.set_pasv(USE_PASSIVE_MODE)
            print("✅ FTP login successful. Passive mode:", USE_PASSIVE_MODE)
            return ftp
        except all_errors as e:
            print(f"⚠️  Connection attempt {attempt} failed: {e}")
            time.sleep(2)
    print("❌ Could not connect to FTP server after retries.")
    return None


def upload_folder():
    ftp = connect_ftp()
    if not ftp:
        return

    try:
        for root, _, files in os.walk(LOCAL_FOLDER):
            rel_path = os.path.relpath(root, LOCAL_FOLDER)
            ftp_path = os.path.join(REMOTE_ROOT, rel_path).replace("\\", "/")

            ftp.cwd("/")  # Reset to root before creating path
            ensure_ftp_path(ftp, ftp_path)

            remote_files = []
            try:
                remote_files = ftp.nlst()
            except all_errors as e:
                print(f"⚠️  Couldn't list files in {ftp.pwd()}: {e}")

            for file in files:
                local_file = os.path.join(root, file)

                # Skip if file already exists with same size
                if file in remote_files:
                    try:
                        remote_size = ftp.size(file)
                        local_size = os.path.getsize(local_file)
                        if remote_size == local_size:
                            print(f"⏭️  Skipping {file} (already uploaded)")
                            continue
                    except Exception as e:
                        print(f"⚠️  Could not compare sizes for {file}: {e}")

                if DRY_RUN:
                    print(f"🧪 [Dry Run] Would upload {file} to {ftp.pwd()}/")
                else:
                    with open(local_file, "rb") as f:
                        print(f"📤 Uploading {file} to {ftp.pwd()}/")
                        ftp.storbinary(f"STOR {file}", f)

        ftp.quit()
        print("✅ Upload complete.")

    except all_errors as e:
        print(f"❌ FTP Error during upload: {e}")


if __name__ == "__main__":
    upload_folder()
