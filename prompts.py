SUMMARY_SYSTEM_PROMPT = "You are a helpful assistant that summarizes articles. Provide a concise summary in the original article's language."

# Add the new prompt constant
with open('myprompt.txt', 'r') as file:
    DETAILED_SUMMARY_PROMPT = file.read().strip()

def get_summary_messages(content_text):
    """
    Generate the messages array for article summarization using the detailed prompt
    """
    messages = [
        {
            "role": "system",
            "content": DETAILED_SUMMARY_PROMPT
        },
        {
            "role": "user",
            "content": (
                f"Article to summarize:\n\n"
                f"{content_text}"
            )
        }
    ]
    return messages 