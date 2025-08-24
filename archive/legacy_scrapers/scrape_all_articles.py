#!/usr/bin/env python3
import json
import re
import time
from typing import Dict, List, Optional
import sys
import os

def extract_main_image_from_content(content: str, url: str) -> Dict:
    """Extract main image from scraped content"""
    default_image = {
        "url": "",
        "caption": "",
        "width": 1200,
        "height": 630
    }
    
    # Look for Medium images
    medium_images = re.findall(r'https://miro\.medium\.com/[^)"\s]+', content)
    if medium_images:
        # Get the first substantial image (skip small profile pics)
        for img_url in medium_images:
            if 'resize:fit' in img_url or 'resize:fill' in img_url:
                # Extract dimensions from URL if available
                width_match = re.search(r'w_(\d+)', img_url)
                height_match = re.search(r'h_(\d+)', img_url)
                
                width = int(width_match.group(1)) if width_match else 1200
                height = int(height_match.group(1)) if height_match else 630
                
                return {
                    "url": img_url,
                    "caption": "",
                    "width": width,
                    "height": height
                }
    
    # Look for other common image patterns
    other_images = re.findall(r'https://[^)"\s]+\.(jpg|jpeg|png|webp)', content, re.IGNORECASE)
    if other_images:
        return {
            "url": other_images[0][0] if isinstance(other_images[0], tuple) else other_images[0],
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
    return default_image

def clean_content_for_audio(content: str) -> str:
    """Clean content for audio consumption"""
    # Remove markdown links but keep the text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Remove image references
    content = re.sub(r'!\[[^\]]*\]\([^)]+\)', '', content)
    
    # Remove excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Remove navigation and UI elements
    content = re.sub(r'(Sign up|Sign in|Follow|Subscribe|Share|Listen)', '', content)
    
    # Remove social media links
    content = re.sub(r'https?://[^\s]+', '', content)
    
    # Clean up extra whitespace
    content = re.sub(r' +', ' ', content)
    content = content.strip()
    
    return content

def estimate_read_time(content: str) -> str:
    """Estimate reading time based on word count"""
    words = len(content.split())
    # Average reading speed: 200 words per minute
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def scrape_article_with_firecrawl(url: str) -> Dict:
    """
    This function would use Firecrawl to scrape an article
    For now, it returns a placeholder structure
    """
    # In a real implementation, this would call Firecrawl
    # For demonstration, returning a basic structure
    return {
        "content": f"Content would be scraped from {url}",
        "image": {
            "url": "",
            "caption": "",
            "width": 1200,
            "height": 630
        }
    }

def main():
    """Main function to scrape all articles"""
    json_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json"
    
    # Load existing articles
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"Starting to scrape {len(articles)} articles...")
    
    # Create a list to track URLs for batch processing
    urls_to_scrape = []
    for article in articles:
        urls_to_scrape.append(article["url"])
    
    print(f"URLs to scrape: {len(urls_to_scrape)}")
    print("First 5 URLs:")
    for i, url in enumerate(urls_to_scrape[:5]):
        print(f"{i+1}. {url}")
    
    # For now, let's create a structure that can be easily updated with real Firecrawl results
    # The actual scraping will be done via the Firecrawl tool in the CLI
    
    # Save the URLs list for reference
    with open("/tmp/urls_to_scrape.txt", 'w') as f:
        for url in urls_to_scrape:
            f.write(f"{url}\n")
    
    print(f"\nSaved {len(urls_to_scrape)} URLs to /tmp/urls_to_scrape.txt")
    print("These URLs are ready for batch scraping with Firecrawl")
    
    return urls_to_scrape

if __name__ == "__main__":
    urls = main()