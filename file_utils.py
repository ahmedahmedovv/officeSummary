import json
import os
import shutil
from datetime import datetime
import yaml

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

RESULTS_DIR = config['output']['directory']

def save_to_json(data, filename):
    """Save data to a JSON file in the specified directory."""
    try:
        filepath = os.path.join(RESULTS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Content saved to {filepath}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

def save_summaries(data):
    """Save summaries to JSON file with optional backup"""
    json_file = os.path.join(RESULTS_DIR, 'all_summaries.json')
    
    # Create backup if enabled
    if config['output']['backup'] and os.path.exists(json_file):
        backup_name = f"backup_{datetime.now().strftime(config['output']['date_format'])}.json"
        backup_path = os.path.join(RESULTS_DIR, backup_name)
        shutil.copy2(json_file, backup_path)
    
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Summaries saved to {json_file}") 