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
@limits(calls=config['rate_limiting']['requests_per_minute'], period=60)  # Use config for rate limiting
def get_openai_summary(article_data):
    try:
        client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            timeout=config['openai']['request_timeout']  # Add timeout from config
        )
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Prepare the content for summarization - removed title
        content_text = "\n".join(article_data['content'])
        
        # Add retry logic from config
        for attempt in range(config['openai']['retry_attempts']):
            try:
                response = client.chat.completions.create(
                    model=config['openai']['model'],
                    messages=get_summary_messages(content_text),
                    max_tokens=config['openai']['max_tokens'],
                    temperature=config['openai']['temperature'],
                    presence_penalty=config['openai']['presence_penalty'],
                    frequency_penalty=config['openai']['frequency_penalty'],
                    top_p=config['openai']['top_p']
                )
                break
            except Exception as e:
                if attempt == config['openai']['retry_attempts'] - 1:
                    raise e
                time.sleep(2 ** attempt)  # Exponential backoff
        
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