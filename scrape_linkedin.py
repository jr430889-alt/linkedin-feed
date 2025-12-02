import json
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

class LinkedInParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.posts = []
        self.current_post = {}
        
def scrape_linkedin_feed():
    """
    Scrapes LinkedIn company page and generates a clean JSON feed.
    This uses SimpleFeedMaker as a source but cleans the data.
    """
    
    # Source feed URL
    source_url = "https://simplefeedmaker.com/feeds/ebd69ced1b67c454dfb039862cd2f1ab.json"
    
    try:
        # Fetch the source feed
        with urllib.request.urlopen(source_url) as response:
            data = json.loads(response.read().decode())
        
        # Filter and clean posts
        cleaned_items = []
        
        for item in data.get('items', [])[:10]:  # Get max 10 posts
            # Get text content
            text = item.get('content_text', '') or item.get('summary', '') or item.get('title', '')
            
            # Clean metadata - remove company info, follower counts
            text = text.strip()
            
            # Remove patterns like "Company Name | 299 followers | "
            import re
            text = re.sub(r'^.*?\d+\s+followers.*?\|.*?\|', '', text, flags=re.IGNORECASE).strip()
            text = re.sub(r'^.*?followers.*?LinkedIn\.', '', text, flags=re.IGNORECASE).strip()
            text = re.sub(r'^[^|]*\|[^|]*\|', '', text).strip()
            
            # Skip if text is too short or looks like metadata
            if len(text) < 20 or 'Executive Director at' in text or 'followers' in text.lower():
                continue
            
            # Only include Bluedot Environmental posts (filter by title or content)
            title = item.get('title', '')
            if 'Bluedot Environmental' not in title:
                continue
            
            # Check for images (exclude logos)
            image_url = None
            if item.get('image'):
                img = item['image'].lower()
                if not any(x in img for x in ['company-logo', '_200_200', '_100_100', 'logo', 'profile']):
                    image_url = item['image']
            
            cleaned_item = {
                'id': item.get('id', f"post-{len(cleaned_items)}"),
                'url': item.get('url', 'https://www.linkedin.com/company/bluedot-environmental-ltd'),
                'title': 'Bluedot Environmental Update',
                'content_text': text,
                'date_published': item.get('date_published', datetime.now().isoformat()),
                'image': image_url
            }
            
            cleaned_items.append(cleaned_item)
        
        # Create clean feed
        output = {
            'version': 'https://jsonfeed.org/version/1.1',
            'title': 'Bluedot Environmental - LinkedIn Feed',
            'home_page_url': 'https://www.linkedin.com/company/bluedot-environmental-ltd',
            'feed_url': 'https://raw.githubusercontent.com/YOUR_USERNAME/linkedin-feed/main/feed.json',
            'description': 'Latest updates from Bluedot Environmental on LinkedIn',
            'items': cleaned_items
        }
        
        # Save to file
        with open('feed.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Successfully generated feed with {len(cleaned_items)} posts")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    scrape_linkedin_feed()
