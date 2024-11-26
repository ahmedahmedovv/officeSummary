import feedparser

def parse_rss_feed(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        articles.append({
            'url': entry.link,
            'title': entry.title,
            'published': entry.published if 'published' in entry else None
        })
    return articles 