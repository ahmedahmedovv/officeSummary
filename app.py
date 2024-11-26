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

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

# Load environment variables from .env file
load_dotenv()

# Create results directory if it doesn't exist
RESULTS_DIR = 'articles'
os.makedirs(RESULTS_DIR, exist_ok=True)

def get_article_content(url):
    try:
        # Use scraping config
        headers = config['scraping']['headers']
        timeout = config['scraping']['timeout']
        
        response = requests.get(
            url, 
            headers=headers,
            timeout=timeout
        )
        response.raise_for_status()
        
        # Add delay between requests
        time.sleep(config['scraping']['delay_between_requests'])
        
        # Parse the HTML content
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Create a dictionary to store the article data
        article_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': '',
            'content': []
        }
        
        # Find the article title
        title = soup.find('h1')
        if title:
            article_data['title'] = title.text.strip()
        
        # Find the main article content
        article_content = soup.find('article') or soup.find(class_='article-content')
        
        if article_content:
            # Get all paragraphs from the article
            paragraphs = article_content.find_all('p')
            article_data['content'] = [p.text.strip() for p in paragraphs if p.text.strip()]
        else:
            article_data['error'] = "Couldn't find article content. The website might be using JavaScript to load content."
            
        return article_data
            
    except requests.RequestException as e:
        return {'error': f"Error fetching the webpage: {e}", 'url': url}
    except Exception as e:
        return {'error': f"An error occurred: {e}", 'url': url}

def save_to_json(data, filename):
    try:
        filepath = os.path.join(RESULTS_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
        print(f"Content saved to {filepath}")
    except Exception as e:
        print(f"Error saving to JSON file: {e}")

def load_existing_summaries():
    """Load existing summaries from JSON file or create new structure"""
    json_file = os.path.join(RESULTS_DIR, 'all_summaries.json')
    try:
        with open(json_file, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'summaries': []}

def save_summaries(data):
    """Save summaries to JSON file"""
    json_file = os.path.join(config['output']['directory'], 'all_summaries.json')
    
    # Create backup if enabled
    if config['output']['backup'] and os.path.exists(json_file):
        backup_name = f"backup_{datetime.now().strftime(config['output']['date_format'])}.json"
        backup_path = os.path.join(config['output']['directory'], backup_name)
        shutil.copy2(json_file, backup_path)
    
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
    print(f"Summaries saved to {json_file}")

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