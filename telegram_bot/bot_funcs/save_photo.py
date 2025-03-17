import json
import os


# Function to load saved file_id from JSON file
def load_file_id():
    file_path = "file_ids.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("logo")
    return None

# Function to save file_id to JSON file
def save_file_id(file_id):
    file_path = "file_ids.json"
    data = {}

    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

    data["logo"] = file_id  # Save with a key for easy lookup

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
