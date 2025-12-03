import json
import urllib.request
from datetime import datetime
import re

def scrape_linkedin_feed():
    """
    Scrapes LinkedIn company page directly and generates a clean JSON feed.
    Uses LinkedIn's public RSS endpoint (if available) or web scraping.
    """

    # LinkedIn company URL
    linkedin_company_url = "https://www.linkedin.com/company/bluedot-environmental-ltd"

    # Try LinkedIn's RSS feed endpoint first
    # Note: LinkedIn removed public RSS feeds, so we'll use a workaround
    # We'll fetch the public company page HTML and parse it

    try:
        # Set up headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        req = urllib.request.Request(
            f"{linkedin_company_url}/posts/",
            headers=headers
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')

        # Parse posts from HTML
        # LinkedIn uses JSON-LD structured data in script tags
        posts = []

        # Look for script tags with type="application/ld+json"
        json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        matches = re.findall(json_ld_pattern, html, re.DOTALL)

        for match in matches:
            try:
                data = json.loads(match)
                if isinstance(data, dict) and data.get('@type') == 'Organization':
                    # Found organization data, but posts are not in structured data
                    pass
            except:
                continue

        # Alternative: Look for posts in the HTML using regex
        # This is fragile but works for public pages

        # Pattern to find post text (this is approximate and may need adjustment)
        post_pattern = r'<div[^>]*class="[^"]*feed-shared-update-v2__description[^"]*"[^>]*>(.*?)</div>'
        post_matches = re.findall(post_pattern, html, re.DOTALL | re.IGNORECASE)

        cleaned_items = []

        for idx, post_html in enumerate(post_matches[:10]):
            # Clean HTML tags
            text = re.sub(r'<[^>]+>', '', post_html)
            text = text.strip()

            # Decode HTML entities
            text = text.replace('&amp;', '&')
            text = text.replace('&lt;', '<')
            text = text.replace('&gt;', '>')
            text = text.replace('&quot;', '"')
            text = text.replace('&#39;', "'")
            text = text.replace('&nbsp;', ' ')

            # Remove extra whitespace
            text = re.sub(r'\s+', ' ', text).strip()

            # Skip if too short
            if len(text) < 30:
                continue

            # Skip metadata patterns
            if re.match(r'^\d+\s*followers', text, re.IGNORECASE):
                continue

            cleaned_item = {
                'id': f"post-{idx}",
                'url': f"{linkedin_company_url}/posts/",
                'title': 'Bluedot Environmental Update',
                'content_text': text,
                'date_published': datetime.now().isoformat(),
                'image': None  # Images would require more complex parsing
            }

            cleaned_items.append(cleaned_item)

            if len(cleaned_items) >= 10:
                break

        # If we didn't find posts via scraping, create a fallback message
        if len(cleaned_items) == 0:
            print("⚠️  Could not scrape posts directly from LinkedIn")
            print("LinkedIn's public pages are difficult to scrape without authentication")
            print("Creating a placeholder feed...")

            cleaned_items = [{
                'id': 'placeholder',
                'url': linkedin_company_url,
                'title': 'Bluedot Environmental Update',
                'content_text': 'Unable to fetch LinkedIn posts. Please visit our LinkedIn page for the latest updates.',
                'date_published': datetime.now().isoformat(),
                'image': None
            }]

        # Create feed
        output = {
            'version': 'https://jsonfeed.org/version/1.1',
            'title': 'Bluedot Environmental - LinkedIn Feed',
            'home_page_url': linkedin_company_url,
            'feed_url': 'https://raw.githubusercontent.com/jr430889-alt/linkedin-feed/main/feed.json',
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
        print("\n⚠️  Direct LinkedIn scraping failed. This is expected - LinkedIn blocks most scrapers.")
        print("Recommendation: Use RSS.app ($8-10/month) or keep using SimpleFeedMaker with better filtering.")

        # Create error feed
        output = {
            'version': 'https://jsonfeed.org/version/1.1',
            'title': 'Bluedot Environmental - LinkedIn Feed',
            'home_page_url': 'https://www.linkedin.com/company/bluedot-environmental-ltd',
            'feed_url': 'https://raw.githubusercontent.com/jr430889-alt/linkedin-feed/main/feed.json',
            'description': 'Latest updates from Bluedot Environmental on LinkedIn',
            'items': [{
                'id': 'error',
                'url': 'https://www.linkedin.com/company/bluedot-environmental-ltd',
                'title': 'Feed Error',
                'content_text': 'Unable to fetch LinkedIn posts directly. LinkedIn blocks automated scraping.',
                'date_published': datetime.now().isoformat(),
                'image': None
            }]
        }

        with open('feed.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return False

if __name__ == '__main__':
    scrape_linkedin_feed()
