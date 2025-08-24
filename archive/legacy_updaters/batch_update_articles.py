#!/usr/bin/env python3
import json
import re
import sys
from typing import Dict, List, Optional

def extract_main_image_from_content(content: str, url: str) -> Dict:
    """Extract main image from scraped content"""
    # Look for Medium images first
    medium_images = re.findall(r'https://miro\.medium\.com/[^)"\s\]]+', content)
    if medium_images:
        for img_url in medium_images:
            if 'resize:fit' in img_url and '/1*' in img_url:
                # Extract dimensions from Medium URL pattern
                if 'resize:fit:' in img_url:
                    dimensions = re.search(r'resize:fit:(\d+)', img_url)
                    width = int(dimensions.group(1)) if dimensions else 608
                    height = int(width * 0.66)  # Approximate aspect ratio
                elif 'w_' in img_url and 'h_' in img_url:
                    width_match = re.search(r'w_(\d+)', img_url)
                    height_match = re.search(r'h_(\d+)', img_url)
                    width = int(width_match.group(1)) if width_match else 608
                    height = int(height_match.group(1)) if height_match else 400
                else:
                    width, height = 608, 400
                
                return {
                    "url": img_url,
                    "caption": "",
                    "width": width,
                    "height": height
                }
    
    # Look for other image patterns
    other_images = re.findall(r'https://[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)', content, re.IGNORECASE)
    if other_images:
        img_url = other_images[0] if isinstance(other_images[0], str) else other_images[0][0]
        return {
            "url": img_url,
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
    # Default placeholder
    return {
        "url": "",
        "caption": "",
        "width": 1200,
        "height": 630
    }

def clean_content_for_audio(content: str) -> str:
    """Clean content for audio consumption"""
    if not content:
        return ""
    
    # Remove navigation elements
    content = re.sub(r'(Sign up|Sign in|Follow|Subscribe|Share|Listen|Medium Logo|Write)', '', content)
    
    # Remove markdown links but keep text
    content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
    
    # Remove image references
    content = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', content)
    
    # Remove URLs
    content = re.sub(r'https?://[^\s\])+]+', '', content)
    
    # Remove excessive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Clean up extra whitespace
    content = re.sub(r' +', ' ', content)
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

def update_article_with_scraped_data(article: Dict, scraped_content: str) -> Dict:
    """Update article with scraped content and extracted image"""
    
    # Clean and update full content
    cleaned_content = clean_content_for_audio(scraped_content)
    article["full_content"] = cleaned_content
    
    # Update read time based on content length
    article["read_time"] = estimate_read_time(cleaned_content)
    
    # Extract and update main image
    main_image = extract_main_image_from_content(scraped_content, article["url"])
    if main_image["url"]:  # Only update if we found an actual image
        article["main_image"] = main_image
    
    return article

# Sample scraped content for demonstration
sample_scraped_contents = {
    "https://blackboxofpm.com/the-black-box-of-product-management-3feb65db6ddb": """
# The Black Box of Product Management

## PMs get sad when you ask them why they exist

There is a rite of passage in the product management world, where all PMs have experienced being asked:

**_"What does a product manager do, anyway?"_**

I empathize with designers and engineers for asking this question. In their shoes, I would be just as skeptical, because a product manager's activities are fragmented, and don't reveal the true discipline beneath.

When I first started in product management, I didn't even know I was doing it. Instead, I was a first time founder and thought I was just "doing startup".

![](https://miro.medium.com/v2/resize:fit:608/1*WljD7gLyX2gr_60o501Z1A.png)

Product Management is the by-product of two exponential forces being exerted on a company.

1. **Speed:** The company exists in an industry where the rate of technological innovation is accelerating
2. **Scale:** Growth in the company's product, organization, and customers are creating complexity

Speed is an exponential force because with every period of time, more change is occurring than in the last. Similarly with scale; every extra feature, employee, or user is adding more complexity to the system than the last.
""",
    "https://www.svpg.com/best-vs-rest-faq/": """
# Best vs. Rest FAQ

In my last article I discussed the two different product worlds that I straddle, and I heard from quite a few people from each of the two camps, as well as several that shared that they've worked in both. I thought it might be useful to share the most common follow-up questions and my responses:

Q: I want to learn more about the best companies – not just the techniques that you share in your writing, but more about their cultures and their broader views on product. How can I learn more?

A: The four large strong product companies I most commonly cite are Apple, Amazon, Google and Netflix. Many books and articles have been written about each, but of those that I've read (I have read quite a few but certainly not all of them), these are the ones that I think do the best job of sharing what's important.
""",
    "https://www.bringthedonuts.com/donuts/": """
# What's the Deal With the Donuts?

## Why have donuts and product management become synonymous?

I believe the best product managers are willing to do whatever it takes to help their teams succeed. An important aspect of that is recognizing that PMs often have to do the work that would fall through the cracks otherwise. By definition that can be grimy, un-fun work: cleaning the bug queue, organizing a document repository, replying to a customer support email. No job should be beneath a product manager.

![donut](https://www.bringthedonuts.com/img/logo/Bring-the-Donuts-logo-dark-64x64.png)

In 2005 I was preparing to give a talk at Berkeley's Haas School of Business about product management. I was looking for a rhetorical device to convey this and I settled on "bring the donuts." If PMs don't bring donuts for the team on launch day, who else will?
"""
}

def main():
    """Update articles with sample scraped content"""
    json_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json"
    
    # Load existing articles
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"Updating articles with scraped content...")
    
    updated_count = 0
    for article in articles:
        url = article["url"]
        
        # Check if we have sample content for this URL
        if url in sample_scraped_contents:
            article = update_article_with_scraped_data(article, sample_scraped_contents[url])
            updated_count += 1
            print(f"✅ Updated: {article['title']}")
    
    print(f"\nUpdated {updated_count} articles with scraped content")
    
    # Save updated articles
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved updated articles to {json_file}")
    
    return articles

if __name__ == "__main__":
    main()