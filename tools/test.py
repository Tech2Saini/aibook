import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlparse
import json,os
# Create your views here.


def get_base_url(url):
    parsed_url = urlparse(url)
    return f"{parsed_url.scheme}://{parsed_url.netloc}"

def fetch_ai_tool_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": url
        }
        response = requests.get(url)
        # response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Fetch favicon
        icons = [link["href"] for link in soup.find_all("link", rel=lambda x: x and "icon" in x.lower())]

        new_icons = []
        for link in icons:
            if not link.startswith('http'):
                new_icons.append(get_base_url(url=url)+link)
            else:
                new_icons.append(link)
        
        favicon = new_icons[0] if len(new_icons)> 0 else ""



        print("The icons are : ",new_icons)
        
        # Fetch page title
        title = soup.title.string.strip() if soup.title else None

        # Fetch page description
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag["content"] if description_tag else None
        

        if description is None:
            meta_og_desc_tag = soup.find("meta", attrs={"property": "og:description"})
            og_description = meta_og_desc_tag["content"] if meta_og_desc_tag else None

            description = og_description
            if description is None:
                og_title_tag = soup.find("meta", attrs={"property": "og:title"})

                # Extract content attribute if found
                og_title = og_title_tag["content"] if og_title_tag else None
                description = og_title

        # Fetch keywords
        keywords_tag = soup.find("meta", attrs={"name": "keywords"})
        if keywords_tag:
            keywords = keywords_tag["content"].split(",")
        else:
            # Alternative way to get keywords by analyzing text
            text = soup.get_text(" ", strip=True)
            words = text.split()
            keywords = list(set(words[:20]))  # Taking first 20 unique words as keywords
        
        data = {
            "url": url,
            "favicon": favicon,
            "title": title,
            "description": "---" if description is None else description,
            "keywords": keywords,
        }
        
        return json.dumps(data, indent=4)
        
    except requests.RequestException as e:
        return json.dumps({"error": str(e)})

# Example Usage
# print(fetch_ai_tool_data("https://en.wikipedia.org/wiki/Louisville_Muhammad_Ali_International_Airport"))
