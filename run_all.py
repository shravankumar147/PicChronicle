import subprocess
import sys
import os

# Optional: Activate the venv if not already activated
# Usually handled by Cmder/batch, but we can enforce it for safety.
VENV_PYTHON = os.path.join("venv", "Scripts", "python.exe")

if not os.path.exists(VENV_PYTHON):
    print("❌ Virtual environment not found at:", VENV_PYTHON)
    sys.exit(1)

scripts = [
    "src/picchronicle.py",
    "src/copy_media_for_cloud.py",
    "src/ftp_dir_upload.py"
]

def run_script(script_path):
    print(f"\n��� Running {script_path} ...")
    try:
        subprocess.run([VENV_PYTHON, script_path], check=True)
        print(f"✅ Completed {script_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script_path} (exit code {e.returncode})")
        sys.exit(e.returncode)

def main():
    for script in scripts:
        run_script(script)
    print("\n��� All scripts completed successfully.")

if __name__ == "__main__":
    main()

