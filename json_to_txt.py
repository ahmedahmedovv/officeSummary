import json
import os
import re
from datetime import datetime

def clean_text(text):
    """Remove all types of whitespace and normalize text"""
    # Convert any Unicode whitespace to regular space
    text = re.sub(r'\s+', ' ', text)
    # Remove any remaining whitespace at ends
    return text.strip()

def convert_summaries_to_txt():
    # Input and output paths
    json_file = 'articles/all_summaries.json'
    output_dir = 'articles/txt_summaries'
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Read JSON file
        with open(json_file, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Create a single text file with all summaries
        output_file = os.path.join(output_dir, f'summaries_{datetime.now().strftime("%Y%m%d")}.txt')
        
        with open(output_file, 'w', encoding='utf-8', newline='') as txt_file:
            for summary in data['summaries']:
                txt_file.write(f"{summary['url'].strip()}\r\n")
                txt_file.write(f"{summary['date'].strip()}\r\n")
                txt_file.write(f"{clean_text(summary['summary'])}\r\n")
                txt_file.write("=" * 80 + "\r\n")
                
        print(f"Summaries converted to text file: {output_file}")
        
    except Exception as e:
        print(f"Error converting summaries to text: {e}") 