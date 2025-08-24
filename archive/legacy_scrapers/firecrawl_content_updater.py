#!/usr/bin/env python3
"""
Script to update articles_with_summaries.json with full_content using Firecrawl MCP
"""
import json
import time
import re
from typing import Dict, List, Any, Optional

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
    """Clean content for audio consumption"""
    if not content:
        return ""
    
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
    
    for i, article in enumerate(articles):
        if needs_content(article):
            needing_content.append({
                'index': i,
                'track_id': article['track_id'],
                'title': article['title'],
                'url': article['url']
            })
    
    return needing_content, articles

def update_article_content(articles: List[Dict[str, Any]], index: int, scraped_content: str):
    """Update a specific article with scraped content"""
    if scraped_content:
        # Clean the content
        cleaned_content = clean_content_for_audio(scraped_content)
        
        # Update the article
        articles[index]['full_content'] = cleaned_content
        articles[index]['read_time'] = estimate_read_time(cleaned_content)
        
        print(f"✅ Updated article {articles[index]['track_id']}: {articles[index]['title']}")
        return True
    else:
        print(f"❌ No content retrieved for article {articles[index]['track_id']}")
        return False

def main():
    """Main function to update articles with Firecrawl content"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    
    print("🔍 Loading articles that need content...")
    needing_content, all_articles = get_articles_needing_content(file_path)
    
    print(f"Found {len(needing_content)} articles needing content")
    
    return needing_content, all_articles, file_path

if __name__ == "__main__":
    needing_content, all_articles, file_path = main()
    print(f"\n📋 Articles to process: {len(needing_content)}")
    print("Ready for Firecrawl scraping...")