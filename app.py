import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from openai_summary import get_openai_summary
from json_to_txt import convert_summaries_to_txt
from dotenv import load_dotenv
import os
import time
import shutil
import yaml
from article_scraper import get_article_content
from file_utils import save_summaries

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load environment variables from .env file
load_dotenv()

# Create results directory if it doesn't exist
RESULTS_DIR = 'articles'
os.makedirs(RESULTS_DIR, exist_ok=True)

def load_existing_summaries():
    """Load existing summaries from JSON file or create new structure"""
    json_file = os.path.join(RESULTS_DIR, 'all_summaries.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'summaries': []}

def main():
    try:
        # Load existing summaries
        all_summaries = load_existing_summaries()
        
        # Create a set of existing URLs for quick lookup
        existing_urls = {summary['url'] for summary in all_summaries['summaries']}
        
        with open('link.txt', 'r') as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
            
        for url in urls:
            # Skip if URL has already been processed
            if url in existing_urls:
                print(f"\nSkipping already processed URL: {url}")
                continue
                
            print(f"\nProcessing: {url}")
            
            # Get article content
            article_data = get_article_content(url)
            
            # Get OpenAI summary
            print("Getting OpenAI summary...")
            article_data = get_openai_summary(article_data)
            
            if 'summary' in article_data:
                # Create summary entry
                summary_entry = {
                    'url': url,
                    'summary': article_data['summary'],
                    'date': datetime.now().isoformat()
                }
                
                # Add to summaries list
                all_summaries['summaries'].append(summary_entry)
                existing_urls.add(url)  # Add to set of processed URLs
                print("Summary added successfully!")
            else:
                print(f"Failed to get summary: {article_data.get('summary_error', 'Unknown error')}")
        
        # Save all summaries
        save_summaries(all_summaries)
        
        # Convert to text file
        print("\nConverting summaries to text file...")
        convert_summaries_to_txt()
            
    except FileNotFoundError:
        print("link.txt file not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 