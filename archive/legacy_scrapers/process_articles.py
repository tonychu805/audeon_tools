#!/usr/bin/env python3
import json
import re
import time
from datetime import datetime
from typing import Dict, List, Optional
import os
import sys

# Add the parent directory to the Python path so we can import firecrawl if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def extract_articles_from_markdown(markdown_file_path: str) -> List[Dict]:
    """Extract article information from markdown file"""
    articles = []
    
    with open(markdown_file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Pattern to match numbered articles with title, author, URL, and description
    pattern = r'(\d+)\.\s+\*\*(.*?)\*\*\s*-\s*(.*?)\s*\n\s*https://([^\s]+)\s*\n\s*\*(.*?)\*'
    
    matches = re.findall(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        article_num, title, author, url, description = match
        
        # Clean up the data
        title = title.strip()
        author = author.strip()
        url = f"https://{url.strip()}"
        description = description.strip()
        
        # Try to extract community/source from URL
        community = "Unknown"
        if "blackboxofpm.com" in url or "medium.com" in url:
            community = "Medium / Black Box of PM"
        elif "svpg.com" in url:
            community = "SVPG"
        elif "bringthedonuts.com" in url:
            community = "Bring the Donuts"
        elif "producttalk.org" in url:
            community = "Product Talk"
        elif "melissaperri.com" in url:
            community = "Melissa Perri"
        elif "mindtheproduct.com" in url:
            community = "Mind The Product"
        elif "a16z.com" in url:
            community = "Andreessen Horowitz"
        elif "paulgraham.com" in url:
            community = "Paul Graham"
        elif "amplitude.com" in url:
            community = "Amplitude"
        elif "intercom.com" in url:
            community = "Intercom"
        elif "romanpichler.com" in url:
            community = "Roman Pichler"
        elif "sachinrekhi.com" in url:
            community = "Sachin Rekhi"
        elif "hbr.org" in url:
            community = "Harvard Business Review"
        
        # Determine category based on content
        category = "Product Management"
        sub_category = ["product_strategy"]
        
        if "leadership" in title.lower() or "manager" in title.lower():
            sub_category = ["leadership"]
        elif "discovery" in title.lower() or "research" in title.lower():
            sub_category = ["product_discovery"]
        elif "strategy" in title.lower() or "framework" in title.lower():
            sub_category = ["product_strategy"]
        elif "ai" in title.lower() or "intelligent" in title.lower():
            sub_category = ["ai_products"]
        elif "okr" in title.lower() or "goal" in title.lower():
            sub_category = ["goal_setting"]
        elif "data" in title.lower() or "metric" in title.lower():
            sub_category = ["data_analytics"]
        
        article = {
            "track_id": len(articles) + 1,
            "title": title,
            "url": url,
            "creator": author,
            "community": community,
            "category": category,
            "sub_category": sub_category,
            "summary": description,
            "releaseDate": "2025-08-20",  # Default date
            "full_content": "",  # Will be filled by scraping
            "read_time": "10 min read",  # Default
            "main_image": {
                "url": "",
                "caption": title,
                "width": 1200,
                "height": 630
            },
            "voices": []
        }
        
        articles.append(article)
    
    return articles

def main():
    """Main processing function"""
    markdown_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw/Curated Content List for Audiobook App.markdown"
    json_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json"
    
    # Extract articles from markdown
    print("Extracting articles from markdown file...")
    new_articles = extract_articles_from_markdown(markdown_file)
    print(f"Found {len(new_articles)} articles to process")
    
    # Load existing JSON file
    existing_articles = []
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            existing_articles = json.load(f)
        print(f"Loaded {len(existing_articles)} existing articles")
    except FileNotFoundError:
        print("No existing JSON file found, starting fresh")
    
    # Update track_ids to continue from existing articles
    start_id = len(existing_articles) + 1
    for i, article in enumerate(new_articles):
        article["track_id"] = start_id + i
    
    # Combine articles
    all_articles = existing_articles + new_articles
    
    # Save the updated JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully added {len(new_articles)} new articles to JSON file")
    print(f"Total articles in JSON: {len(all_articles)}")
    
    # Print first few new articles for verification
    print("\nFirst few new articles:")
    for article in new_articles[:3]:
        print(f"- {article['title']} by {article['creator']}")
        print(f"  URL: {article['url']}")
        print(f"  Community: {article['community']}")
        print()

if __name__ == "__main__":
    main()