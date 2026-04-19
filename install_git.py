import urllib.request
import zipfile
import os
import sys

URL = "https://github.com/git-for-windows/git/releases/download/v2.44.0.windows.1/MinGit-2.44.0-64-bit.zip"
ZIP_PATH = "mingit.zip"
EXTRACT_PATH = "portable_git"

print(f"Downloading {URL}...")
try:
    urllib.request.urlretrieve(URL, ZIP_PATH)
    print("Download complete.")
except Exception as e:
    print(f"Error downloading: {e}")
    sys.exit(1)

print(f"Extracting to {EXTRACT_PATH}...")
try:
    os.makedirs(EXTRACT_PATH, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(EXTRACT_PATH)
    print("Extraction complete.")
except Exception as e:
    print(f"Error extracting: {e}")
    sys.exit(1)
    
print("Cleaning up...")
try:
    os.remove(ZIP_PATH)
    print("Done. Portable Git is ready!")
except Exception as e:
    print(f"Cleanup error (ignored): {e}")
