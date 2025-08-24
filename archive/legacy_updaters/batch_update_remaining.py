#!/usr/bin/env python3
"""
Batch update all remaining articles with missing full_content
"""
import json
import re
from typing import Dict, List, Any, Tuple

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

def clean_content(content: str) -> str:
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

def get_remaining_articles() -> Tuple[List[Dict], str]:
    """Get all articles that still need content"""
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    articles = load_articles(file_path)
    
    remaining = []
    for i, article in enumerate(articles):
        if needs_content(article):
            remaining.append({
                'index': i,
                'track_id': article['track_id'],
                'title': article['title'],
                'url': article['url']
            })
    
    return remaining, file_path

def update_article_in_json(file_path: str, track_id: int, content: str) -> bool:
    """Update a specific article with content"""
    articles = load_articles(file_path)
    
    for article in articles:
        if article['track_id'] == track_id:
            cleaned_content = clean_content(content)
            article['full_content'] = cleaned_content
            article['read_time'] = estimate_read_time(cleaned_content)
            save_articles(file_path, articles)
            print(f"✅ Updated Track {track_id}: {article['title']}")
            return True
    
    print(f"❌ Track {track_id} not found")
    return False

def main():
    """Main function to get remaining articles"""
    remaining, file_path = get_remaining_articles()
    
    print(f"Found {len(remaining)} articles still needing content:")
    print("="*80)
    
    for i, article in enumerate(remaining):
        print(f"{i+1:2d}. Track {article['track_id']:2d}: {article['title']}")
        print(f"     URL: {article['url']}")
        print()
    
    return remaining, file_path

if __name__ == "__main__":
    remaining_articles, json_file_path = main()
    print(f"\n🚀 Ready to process {len(remaining_articles)} articles!")