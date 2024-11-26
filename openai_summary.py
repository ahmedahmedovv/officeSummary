import os
import time
from openai import OpenAI
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=50, period=60)  # 50 calls per minute
def get_openai_summary(article_data):
    try:
        # Initialize OpenAI client with API key from .env
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        if not os.getenv('OPENAI_API_KEY'):
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Prepare the content for summarization
        content_text = "\n\n".join([
            f"Title: {article_data['title']}",
            "Content:",
            "\n".join(article_data['content'])
        ])
        
        # Call OpenAI API for summarization
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes articles. Provide a concise summary in the original article's language."},
                {"role": "user", "content": f"Please summarize this article:\n\n{content_text}"}
            ]
        )
        
        # Add summary to article data
        article_data['summary'] = response.choices[0].message.content
        return article_data
        
    except Exception as e:
        print(f"Error getting OpenAI summary: {e}")
        article_data['summary_error'] = str(e)
        return article_data