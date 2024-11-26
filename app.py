import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from openai_summary import get_openai_summary
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create results directory if it doesn't exist
RESULTS_DIR = 'articles'
os.makedirs(RESULTS_DIR, exist_ok=True)
SUMMARIES_FILE = os.path.join(RESULTS_DIR, 'all_summaries.json')

def get_article_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        article_data = {
            'url': url,
            'scraped_at': datetime.now().isoformat(),
            'title': '',
            'content': []
        }
        
        title = soup.find('h1')
        if title:
            article_data['title'] = title.text.strip()
        
        article_content = soup.find('article') or soup.find(class_='article-content')
        if article_content:
            paragraphs = article_content.find_all('p')
            article_data['content'] = [p.text.strip() for p in paragraphs if p.text.strip()]
            
        return article_data
            
    except Exception as e:
        return {'error': f"An error occurred: {e}", 'url': url}

def load_existing_summaries():
    try:
        if os.path.exists(SUMMARIES_FILE):
            with open(SUMMARIES_FILE, 'r', encoding='utf-8') as file:
                return json.load(file)
    except Exception:
        pass
    return {'summaries': []}

def save_summaries(summaries):
    with open(SUMMARIES_FILE, 'w', encoding='utf-8') as file:
        json.dump(summaries, file, ensure_ascii=False, indent=2)
    print(f"Summaries saved to {SUMMARIES_FILE}")

def main():
    try:
        # Load existing summaries
        all_summaries = load_existing_summaries()
        
        with open('link.txt', 'r') as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
            
        for url in urls:
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
                    'title': article_data.get('title', ''),
                    'summary': article_data['summary'],
                    'date': datetime.now().isoformat()
                }
                
                # Add to summaries list
                all_summaries['summaries'].append(summary_entry)
                print("Summary added successfully!")
            else:
                print(f"Failed to get summary: {article_data.get('summary_error', 'Unknown error')}")
        
        # Save all summaries
        save_summaries(all_summaries)
            
    except FileNotFoundError:
        print("link.txt file not found!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()