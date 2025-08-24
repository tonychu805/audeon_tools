#!/usr/bin/env python3
"""
Batch script to scrape all remaining articles using Firecrawl
"""
import json
import time
from typing import Dict, List, Any

def load_articles(file_path: str) -> List[Dict[str, Any]]:
    """Load articles from JSON file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_articles(file_path: str, articles: List[Dict[str, Any]]) -> None:
    """Save articles to JSON file"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

def needs_content(article: Dict[str, Any]) -> bool:
    """Check if article needs full_content populated"""
    return not article.get('full_content') or not article['full_content'].strip()

def clean_content_for_audio(content: str) -> str:
    """Clean content for audio consumption - simplified version"""
    if not content:
        return ""
    
    import re
    
    # Remove navigation and UI elements
    nav_elements = [
        r'Sign up', r'Sign in', r'Follow', r'Subscribe', r'Share', r'Listen', 
        r'Medium Logo', r'Write', r'Open in app', r'Follow publication',
        r'View comments?\s*\(\d*\)', r'See all from', r'More from', r'Recommended from Medium',
        r'Help', r'Status', r'About', r'Careers', r'Press', r'Blog', r'Privacy', r'Rules', r'Terms',
        r'protected by \*\*reCAPTCHA\*\*', r'reCAPTCHA', r'Recaptcha requires verification'
    ]
    
    for element in nav_elements:
        content = re.sub(element, '', content, flags=re.IGNORECASE)
    
    # Remove markdown links but keep text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Remove image references
    content = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', content)
    
    # Remove URLs
    content = re.sub(r'https?://[^\s\])+]+', '', content)
    
    # Remove email addresses
    content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', content)
    
    # Remove excessive newlines and whitespace
    content = re.sub(r'\n{3,}', '\n\n', content)
    content = re.sub(r' {2,}', ' ', content)
    content = content.strip()
    
    return content

def estimate_read_time(content: str) -> str:
    """Estimate reading time based on word count"""
    if not content:
        return "5 min read"
    
    words = len(content.split())
    # Average reading speed: 200 words per minute
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

def get_articles_needing_content(file_path: str):
    """Get list of articles that need content"""
    articles = load_articles(file_path)
    needing_content = []
    
    for article in articles:
        if needs_content(article):
            needing_content.append({
                'track_id': article['track_id'],
                'title': article['title'],
                'url': article['url']
            })
    
    return needing_content, articles

def main():
    """Main function to identify articles needing scraping"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    
    print("🔍 Analyzing articles that need content...")
    needing_content, all_articles = get_articles_needing_content(file_path)
    
    print(f"Found {len(needing_content)} articles needing content:")
    print("\n" + "="*80)
    
    for i, article in enumerate(needing_content, 1):
        print(f"{i:2d}. Track {article['track_id']:2d}: {article['title']}")
        print(f"     URL: {article['url']}")
        print()
    
    print("="*80)
    print(f"\n🚀 Ready to batch scrape {len(needing_content)} articles!")
    print("\nThis script will help organize the batch scraping process.")
    print("You can now proceed to scrape these URLs systematically.")
    
    return needing_content

if __name__ == "__main__":
    articles_to_scrape = main()