#!/usr/bin/env python3
"""
Script to update articles missing main image URLs using Firecrawl MCP
"""

import json
import time
import requests
from typing import Dict, List, Optional
import re
from bs4 import BeautifulSoup

def load_articles() -> List[Dict]:
    """Load articles from JSON file"""
    with open('/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json', 'r') as f:
        return json.load(f)

def save_articles(articles: List[Dict]) -> None:
    """Save articles back to JSON file"""
    with open('/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json', 'w') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

def extract_main_image_from_html(html_content: str, url: str) -> Optional[str]:
    """Extract main image URL from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Common patterns for main images
    image_patterns = [
        # Open Graph image
        'meta[property="og:image"]',
        'meta[property="og:image:url"]',
        # Twitter Card image
        'meta[name="twitter:image"]',
        'meta[name="twitter:image:src"]',
        # Hero/banner images
        '.hero img',
        '.banner img',
        '.article-banner img',
        'article img:first-of-type',
        '.post-featured-image img',
        '.featured-image img',
        # First image in content
        '.content img:first-of-type',
        '.post-content img:first-of-type',
        'img[src*="featured"]',
        'img[src*="hero"]',
        'img[src*="banner"]'
    ]
    
    for pattern in image_patterns:
        if pattern.startswith('meta'):
            meta = soup.select_one(pattern)
            if meta and meta.get('content'):
                img_url = meta.get('content')
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    from urllib.parse import urljoin
                    img_url = urljoin(url, img_url)
                if img_url and img_url.startswith('http'):
                    return img_url
        else:
            img = soup.select_one(pattern)
            if img and img.get('src'):
                img_url = img.get('src')
                if img_url.startswith('//'):
                    img_url = 'https:' + img_url
                elif img_url.startswith('/'):
                    from urllib.parse import urljoin
                    img_url = urljoin(url, img_url)
                if img_url and img_url.startswith('http'):
                    return img_url
    
    return None

def get_articles_missing_images(articles: List[Dict]) -> List[Dict]:
    """Get articles that are missing main image URLs"""
    missing = []
    for article in articles:
        main_image = article.get('main_image', {})
        if not main_image or not main_image.get('url', '').strip():
            missing.append(article)
    return missing

def update_article_with_image(article: Dict, image_url: str) -> None:
    """Update article with main image URL"""
    if 'main_image' not in article:
        article['main_image'] = {}
    
    article['main_image']['url'] = image_url
    print(f"✓ Updated '{article['title']}' with image: {image_url}")

def main():
    """Main function to update missing images"""
    print("Loading articles...")
    articles = load_articles()
    
    print("Finding articles missing main images...")
    missing_images = get_articles_missing_images(articles)
    print(f"Found {len(missing_images)} articles missing main images")
    
    if not missing_images:
        print("No articles missing images!")
        return
    
    print("\nStarting image extraction...")
    updated_count = 0
    
    for i, article in enumerate(missing_images, 1):
        title = article.get('title', 'Unknown')
        url = article.get('url', '')
        
        print(f"\n[{i}/{len(missing_images)}] Processing: {title}")
        print(f"URL: {url}")
        
        try:
            # Simple HTTP request to get the page
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Extract main image
            image_url = extract_main_image_from_html(response.text, url)
            
            if image_url:
                update_article_with_image(article, image_url)
                updated_count += 1
            else:
                print(f"✗ No main image found for: {title}")
            
            # Small delay to be respectful
            time.sleep(1)
            
        except Exception as e:
            print(f"✗ Error processing {title}: {str(e)}")
            continue
    
    print(f"\n=== Summary ===")
    print(f"Total articles processed: {len(missing_images)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed to update: {len(missing_images) - updated_count}")
    
    if updated_count > 0:
        print("\nSaving updated articles...")
        save_articles(articles)
        print("✓ Articles saved successfully!")

if __name__ == "__main__":
    main()