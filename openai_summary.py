import os
import time
import yaml
import re
from openai import OpenAI
from ratelimit import limits, sleep_and_retry
from prompts import get_summary_messages

# Load config file
with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

@sleep_and_retry
@limits(calls=50, period=60)  # 50 calls per minute
def get_openai_summary(article_data):
    try:
        # Initialize OpenAI client with API key from .env
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Prepare the content for summarization - removed title
        content_text = "\n".join(article_data['content'])
        
        # Call OpenAI API for summarization using config values
        response = client.chat.completions.create(
            model=config['openai']['model'],
            messages=get_summary_messages(content_text),
            max_tokens=config['openai']['max_tokens'],
            temperature=config['openai']['temperature']
        )
        
        # Get summary and clean it up
        summary = response.choices[0].message.content
        summary = re.sub(r'<[^>]+>', '', summary)  # Remove HTML tags
        summary = summary.replace('\\n', '\n')  # Replace escaped newlines
        summary = re.sub(r'\n{3,}', '\n\n', summary)  # Replace 3+ newlines with double newlines
        summary = summary.strip()  # Remove leading/trailing whitespace
        
        # Return only the required fields
        return {
            'url': article_data['url'],
            'summary': summary,
            'date': article_data.get('date', '')
        }
        
    except Exception as e:
        print(f"Error getting OpenAI summary: {e}")
        return {
            'url': article_data.get('url', ''),
            'summary_error': str(e),
            'date': article_data.get('date', '')
        }