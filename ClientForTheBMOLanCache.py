import requests
import os
import hashlib
import json

SERVER_URL = 'http://127.0.0.1:5000'  # Change this to the URL of your server
LOCAL_DIRECTORY = '/path/to/local/directory'  # Change this to your local directory path

def calculate_checksum(file_path):
    """Calculate the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def fetch_remote_hashes():
    """Fetch the hashes.json from the server."""
    response = requests.get(f"{SERVER_URL}/hashes.json")
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch remote hashes")

def sync_files(remote_hashes):
    """Sync the files based on remote hashes."""
    if not os.path.exists(LOCAL_DIRECTORY):
        os.makedirs(LOCAL_DIRECTORY)

    # Load local hashes if exists
    local_hashes_path = os.path.join(LOCAL_DIRECTORY, 'hashes.json')
    if os.path.exists(local_hashes_path):
        with open(local_hashes_path, 'r') as f:
            local_hashes = json.load(f)
    else:
        local_hashes = {}

    # Compare and download/update files
    for path, remote_hash in remote_hashes.items():
        local_path = os.path.join(LOCAL_DIRECTORY, path)
        local_hash = local_hashes.get(path)
        if not local_hash or local_hash != remote_hash:
            print(f"Updating {path}...")
            download_file(path, local_path)
    
    # Update local hashes.json
    with open(local_hashes_path, 'w') as f:
        json.dump(remote_hashes, f, indent=4)

def download_file(remote_path, local_path):
    """Download a file from the server."""
    url = f"{SERVER_URL}/files/{remote_path}"
    response = requests.get(url, stream=True)
    os.makedirs(os.path.dirname(local_path), existent_ok=True)
    if response.status_code == 200:
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

if __name__ == "__main__":
    try:
        remote_hashes = fetch_remote_hashes()
        sync_files(remote_hashes)
        print("Sync completed.")
    except Exception as e:
        print(f"Error: {e}")

