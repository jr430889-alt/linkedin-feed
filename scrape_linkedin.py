import json
import urllib.request
from datetime import datetime
import re

def scrape_linkedin_feed():
    """
    Uses SimpleFeedMaker but with MUCH better filtering and cleaning.
    Only keeps posts that are actually FROM Bluedot Environmental.
    """

    # Source feed URL from SimpleFeedMaker
    source_url = "https://simplefeedmaker.com/feeds/ebd69ced1b67c454dfb039862cd2f1ab.json"

    try:
        # Fetch the source feed
        with urllib.request.urlopen(source_url) as response:
            data = json.loads(response.read().decode())

        cleaned_items = []

        for item in data.get('items', []):
            # Get title to check which company posted
            title = item.get('title', '')

            # ONLY accept posts where the title is "Bluedot Environmental Ltd." or similar
            if 'Bluedot Environmental' not in title:
                print(f"⏭️  Skipping post from: {title}")
                continue

            # Get text content
            text = item.get('content_text', '') or item.get('summary', '') or item.get('title', '')
            text = text.strip()

            # Aggressively remove ALL metadata patterns
            # Pattern: "Bluedot Environmental Ltd.299 followers2wReport this post"
            original_text = text

            # Remove company name and follower count at start
            text = re.sub(r'^Bluedot Environmental Ltd\.', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^\d+\s*followers', '', text, flags=re.IGNORECASE)
            text = re.sub(r'^\d+[wdhm]', '', text)  # Remove time indicators like "2w", "1d"
            text = re.sub(r'^Report this post', '', text, flags=re.IGNORECASE)

            # Remove any remaining leading metadata
            text = re.sub(r'^[^a-zA-Z]*', '', text)  # Remove leading non-letters
            text = text.strip()

            # Skip if text is too short after cleaning
            if len(text) < 30:
                print(f"⏭️  Skipping short post: {text[:50]}")
                continue

            # Skip if it's a job posting or metadata-only
            skip_patterns = [
                r'^Executive Director at',
                r'^Senior .* at',
                r'^Manager at',
                r'^\d+\s*followers'
            ]

            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, text, re.IGNORECASE):
                    should_skip = True
                    break

            if should_skip:
                print(f"⏭️  Skipping metadata post: {text[:50]}")
                continue

            # Get URL
            url = item.get('url', 'https://www.linkedin.com/company/bluedot-environmental-ltd')

            # Get date
            date_str = item.get('date_published', datetime.now().isoformat())

            # Check for images (no logos)
            image_url = None
            if item.get('image'):
                img = item['image'].lower()
                if not any(x in img for x in ['company-logo', '_200_200', '_100_100', 'logo', 'profile']):
                    image_url = item['image']

            cleaned_item = {
                'id': item.get('id', f"post-{len(cleaned_items)}"),
                'url': url,
                'title': 'Bluedot Environmental Update',
                'content_text': text,
                'date_published': date_str,
                'image': image_url
            }

            cleaned_items.append(cleaned_item)
            print(f"✅ Added post: {text[:80]}...")

            # Stop after we have 10 good posts
            if len(cleaned_items) >= 10:
                break

        # Create clean feed
        output = {
            'version': 'https://jsonfeed.org/version/1.1',
            'title': 'Bluedot Environmental - LinkedIn Feed',
            'home_page_url': 'https://www.linkedin.com/company/bluedot-environmental-ltd',
            'feed_url': 'https://raw.githubusercontent.com/jr430889-alt/linkedin-feed/main/feed.json',
            'description': 'Latest updates from Bluedot Environmental on LinkedIn',
            'items': cleaned_items
        }

        # Save to file
        with open('feed.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Successfully generated feed with {len(cleaned_items)} posts")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    scrape_linkedin_feed()
