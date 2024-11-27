import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import yaml
import os

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

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