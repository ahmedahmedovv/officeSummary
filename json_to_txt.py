import json
import os
import re
from datetime import datetime
import gzip
import yaml

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

def clean_text(text):
    """Remove all types of whitespace and normalize text"""
    # Convert any Unicode whitespace to regular space
    text = re.sub(r'\s+', ' ', text)
    # Remove any remaining whitespace at ends
    return text.strip()

def format_date(date_str):
    """Convert ISO date format to 'day-month-year' format"""
    try:
        # Parse the ISO format date
        date_obj = datetime.fromisoformat(date_str.split('.')[0])  # Remove microseconds
        # Format it to desired format (day-month-year)
        return date_obj.strftime("%d-%m-%Y")
    except:
        return date_str  # Return original if parsing fails

def convert_summaries_to_txt():
    # Use config paths
    json_file = os.path.join(config['output']['directory'], 'all_summaries.json')
    output_dir = os.path.join(config['output']['directory'], 'txt_summaries')
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Use config date format
        output_file = os.path.join(
            output_dir, 
            f"{config['output']['file_prefix']}_{datetime.now().strftime(config['output']['date_format'])}.txt"
        )
        
        # Compress if configured
        if config['output']['compress']:
            output_file += '.gz'
            open_func = gzip.open
        else:
            open_func = open
        
        with open(output_file, 'w', encoding='utf-8', newline='') as txt_file:
            for summary in data['summaries']:
                txt_file.write(f"{summary['url'].strip()}\r\n")
                txt_file.write(f"{format_date(summary['date'])}\r\n")
                txt_file.write(f"{clean_text(summary['summary'])}\r\n")
                txt_file.write("\r\n")  # Single newline between summaries
                
        print(f"Summaries converted to text file: {output_file}")
        
    except Exception as e:
        print(f"Error converting summaries to text: {e}") 