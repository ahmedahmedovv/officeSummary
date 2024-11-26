import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from openai_summary import get_openai_summary  # Import the new module
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Create results directory if it doesn't exist
RESULTS_DIR = 'articles'
os.makedirs(RESULTS_DIR, exist_ok=True)

def get_article_content(url):
    try:
        # Send GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        
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

def main():
    try:
        with open('link.txt', 'r') as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]
            
        for url in urls:
            print(f"\nFetching content from: {url}")
            
            # Get article content
            article_data = get_article_content(url)
            
            # Get OpenAI summary
            print("Getting OpenAI summary...")
            article_data = get_openai_summary(article_data)  # Use the imported function
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            url_part = url.rstrip('/').split('/')[-1][:30]
            filename = f"article_{timestamp}_{url_part}.json"
            
            # Save as JSON
            save_to_json(article_data, filename)
            
    except FileNotFoundError:
        print("link.txt file not found!")
    except Exception as e:
        print(f"Error reading link.txt: {e}")

if __name__ == "__main__":
    main() 