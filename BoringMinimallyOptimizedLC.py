import os
import hashlib
import json
from flask import Flask, send_from_directory, jsonify, safe_join

app = Flask(__name__)

# Configuration
DIRECTORY = '/path/to/your/directory'  # Update this to the directory you want to serve

def calculate_checksum(file_path):
    """Calculate the MD5 checksum of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def prepare_directory_structure(directory):
    """Walk through the directory, hash files, and write structure to hashes.json."""
    dir_structure = {}
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            relative_path = os.path.relpath(file_path, directory)
            dir_structure[relative_path] = calculate_checksum(file_path)

    hashes_path = os.path.join(directory, 'hashes.json')
    with open(hashes_path, 'w') as f:
        json.dump(dir_structure, f, indent=4)
    return hashes_path

@app.route('/files/<path:path>')
def serve_file(path):
    """Serve a file from the directory."""
    return send_from_directory(DIRECTORY, path)

@app.route('/hashes.json')
def serve_hashes():
    """Serve the hashes.json file."""
    hashes_path = safe_join(DIRECTORY, 'hashes.json')
    with open(hashes_path, 'r') as f:
        hashes_data = json.load(f)
    return jsonify(hashes_data)

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python script.py <directory_path>")
        sys.exit(1)
    
    DIRECTORY = sys.argv[1]  # Update DIRECTORY with command line argument
    hashes_path = prepare_directory_structure(DIRECTORY)
    print(f"Directory structure and hashes written to {hashes_path}")

    # Start the Flask web server
    app.run(debug=True, port=5000)

