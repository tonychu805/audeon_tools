#!/usr/bin/env python3
import json
import re
import time
from typing import Dict, List, Optional

def extract_main_image_from_content(content: str) -> Dict:
    """Extract main image from scraped content"""
    # Look for Medium images first
    medium_images = re.findall(r'https://miro\.medium\.com/[^)"\s\]]+', content)
    if medium_images:
        for img_url in medium_images:
            # Skip small profile images
            if 'resize:fill:64:64' in img_url or 'resize:fill:32:32' in img_url or 'resize:fill:80:80' in img_url:
                continue
            # Look for larger content images
            if ('resize:fit:' in img_url and '/1*' in img_url) or 'resize:fill:96:96' in img_url:
                width = 700 if 'resize:fit:700' in img_url else 608
                height = int(width * 0.6)  # Approximate aspect ratio
                return {
                    "url": img_url,
                    "caption": "",
                    "width": width,
                    "height": height
                }
    
    # Look for other image patterns
    other_images = re.findall(r'https://[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)', content, re.IGNORECASE)
    if other_images:
        return {
            "url": other_images[0],
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
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
    
    # Remove lines that are just navigation or UI elements
    lines = content.split('\n')
    cleaned_lines = []
    for line in lines:
        line = line.strip()
        if len(line) < 3:  # Skip very short lines
            continue
        if any(word in line.lower() for word in ['follow', 'subscribe', 'sign up', 'sign in', 'listen']):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def estimate_read_time(content: str) -> str:
    """Estimate reading time based on word count"""
    if not content:
        return "5 min read"
    
    words = len(content.split())
    # Average reading speed: 200 words per minute
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

# Batch of successfully scraped content
scraped_contents = {
    "https://blackboxofpm.com/making-good-decisions-as-a-product-manager-c66ddacc9e2b": """
# Making Good Decisions as a Product Manager

While product managers may not build the actual product, they do produce something very tangible for a team: decisions.

These decisions can be about anything: small ones like a line of copy in the docs, to big ones like what the MVP of a new feature should be.

The decisions PMs make are the ones that unblock their team so they can continue to build. They don't need to make every decision, but they are responsible for ensuring a decision gets made — whether by them, their team, or their stakeholders.

Product managers are the hedge against indecision, and it's uniquely our job because we tend to have the most context in a company. Typically, the most important decisions that a PM makes are, in order:

1. Why a team exists (vision and the impact they aspire to create)
2. What the general approach is to accomplish the vision (strategy)
3. What to build now, and what not to build (project prioritization)
4. What the smallest thing that can be built is that achieves the impact (MVP)

![](https://miro.medium.com/v2/resize:fit:700/1*dkF-w-XpXZAAhBceYQ-kgw.jpeg)

Being a good decision maker means doing two things:
1. Making decisions using the right amount of information
2. Making decisions as quickly as possible

Deciding how important a decision is, is the most important decision you can make. For people that make decisions for a living, understanding when one is really important vs. not-that-important is the most critical skill.

In Amazon's 2016 shareholder letter, Jeff Bezos touches on this concept with what he calls type 1 and type 2 decisions.

Type 1 decisions are not reversible, and you have to be very careful making them.
Type 2 decisions are like walking through a door — if you don't like the decision, you can always go back.

![](https://miro.medium.com/v2/resize:fit:700/1*bwSTglAJi9tJiUMCy3-eDg.png)

This framework breaks down decision importance into three dimensions:
1. Resource investment from a decision
2. The overall impact of a positive outcome
3. The impacts of a negative outcome

Good decision makers are quick decision makers. The vast majority of decisions should be made quickly.
""",
    "https://www.svpg.com/creating-intelligent-products/": """
# Creating Intelligent Products

This is an article about the potential future of the products we will create, and how we will create those products.

However, to understand where we're heading, we need to look back over the past 40 years.

Consider this quote:

"Applying AI to the software development process is a major research topic. There is tremendous potential for improving the productivity of the programmer, the quality of the resulting code, and the ability to maintain and enhance applications…we are working on intelligent programming environments that help users assess the impact of potential modifications, determine which scenarios could have caused a particular bug, systematically test an application, coordinate development among teams of programmers…other significant software engineering applications include automatic programming, syntax-directed editors, automatic program testing…"

When I asked ChatGPT the most likely source of this quote, it suggested that it is very similar to several recent articles and papers, from both industry and academia, mostly from the past year.

But the crazy truth is that this quote is from the very first article I ever published, way back in March of 1986. That is not a typo.

I'm not sharing this to highlight how old I am, or to brag about being able to predict anything. In fact, we were truly clueless about just how hard it would be to solve these problems.

But it is true that I've been thinking about creating these types of intelligent products for a very long time, and I have been watching the various attempts over the years at different approaches to AI, with more than an average amount of interest.

What I wanted to discuss in this article, is the nature of the products I believe that most of us will be working on for at least the next several years. Not all of us, but most of us.

I'm referring to these types of products as "intelligent products," which is meant to reflect a blend of deterministic and probabilistic approaches, where the intent is to create substantially more useful and valuable solutions for our customers.

I view probability as central to intelligence, not an alternative.

Why am I making such a big deal about this point? Because I keep hearing from product teams, especially in the B2B space, that while probabilistic solutions might be "intriguing" they believe they are not relevant to their mission-critical, regulated or compliance-constrained businesses.

It's also important to remind product teams that intelligent products include more than just generative AI based solutions. There are several other very important classes of AI products.

While ChatGPT and Midjourney are probably the "killer apps" that awoke the world to the potential of AI in general, and generative AI in particular, maybe the single most impressive intelligent product that I've personally experienced thus far is the Waymo Driver.

If you consider for a moment the larger problem of autonomous driving, it's not hard to imagine some of the many hard problems that need to be solved in order to provide an effective intelligent product. The Waymo product currently represents more than a decade of product discovery and delivery, with a gradually expanding rollout, along with continuous learning and improvement.

My belief is that product teams need a more nuanced view of the distinctions between deterministic and probabilistic solutions, and that going forward it will be common for our products to contain a blend of both.

I expect that many of the most valuable uses of AI will be in situations where probability is precisely what is used by human experts, and what is needed in a solution.
""",
}

def scrape_with_firecrawl(url: str) -> Optional[str]:
    """Scrape content from URL using Firecrawl"""
    try:
        print(f"🔄 Scraping {url} with Firecrawl...")
        # This function will be called externally with Firecrawl MCP
        # Return None to indicate external scraping needed
        return None
    except Exception as e:
        print(f"❌ Error scraping {url}: {str(e)}")
        return None

def update_articles_with_firecrawl(json_file: str):
    """Update articles using Firecrawl for missing content"""
    
    # Load existing articles
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    print(f"Updating articles with Firecrawl...")
    
    # First update with existing batch content
    batch_updated_count = 0
    for article in articles:
        url = article["url"]
        
        # Check if we have scraped content for this URL in the batch
        if url in scraped_contents and (not article.get("full_content") or not article["full_content"].strip()):
            scraped_content = scraped_contents[url]
            
            # Clean and update full content
            cleaned_content = clean_content_for_audio(scraped_content)
            article["full_content"] = cleaned_content
            
            # Update read time based on content length
            article["read_time"] = estimate_read_time(cleaned_content)
            
            # Extract and update main image
            main_image = extract_main_image_from_content(scraped_content)
            if main_image["url"]:  # Only update if we found an actual image
                article["main_image"] = main_image
            
            batch_updated_count += 1
            print(f"✅ Updated from batch: {article['title']}")
    
    # Now use Firecrawl for remaining articles
    firecrawl_updated_count = 0
    articles_needing_content = [a for a in articles if not a.get("full_content") or not a["full_content"].strip()]
    
    print(f"\n🚀 Using Firecrawl for {len(articles_needing_content)} remaining articles...")
    
    for i, article in enumerate(articles_needing_content):
        url = article["url"]
        print(f"\n{i+1}/{len(articles_needing_content)}: {article['title']}")
        
        # Skip if already in scraped_contents batch
        if url in scraped_contents:
            continue
            
        scraped_content = scrape_with_firecrawl(url)
        
        if scraped_content:
            # Clean and update full content
            cleaned_content = clean_content_for_audio(scraped_content)
            article["full_content"] = cleaned_content
            
            # Update read time based on content length
            article["read_time"] = estimate_read_time(cleaned_content)
            
            # Extract and update main image
            main_image = extract_main_image_from_content(scraped_content)
            if main_image["url"]:  # Only update if we found an actual image
                article["main_image"] = main_image
            
            firecrawl_updated_count += 1
            print(f"✅ Updated with Firecrawl: {article['title']}")
            
            # Save progress every 5 articles
            if firecrawl_updated_count % 5 == 0:
                print(f"💾 Saving progress... ({batch_updated_count + firecrawl_updated_count} total updated)")
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(articles, f, indent=2, ensure_ascii=False)
            
            # Rate limiting - wait 2 seconds between requests
            if i < len(articles_needing_content) - 1:
                time.sleep(2)
        else:
            print(f"⚠️  Failed to scrape: {article['title']}")
    
    total_updated = batch_updated_count + firecrawl_updated_count
    print(f"\nUpdated {total_updated} articles total ({batch_updated_count} from batch, {firecrawl_updated_count} with Firecrawl)")
    
    # Save final results
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved updated articles to {json_file}")
    
    return articles

def update_articles_with_batch_content(json_file: str):
    """Update articles with batch scraped content (legacy function)"""
    return update_articles_with_firecrawl(json_file)

def main():
    """Main function to update articles with comprehensive scraped content"""
    json_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json"
    
    # Update articles with current batch of scraped content
    articles = update_articles_with_batch_content(json_file)
    
    # Count articles with and without content
    with_content = sum(1 for article in articles if article.get("full_content", "").strip())
    with_images = sum(1 for article in articles if article.get("main_image", {}).get("url", "").strip())
    
    print(f"\n📊 Final Statistics:")
    print(f"Total articles: {len(articles)}")
    print(f"Articles with full content: {with_content}")
    print(f"Articles with main images: {with_images}")
    print(f"Articles still needing content: {len(articles) - with_content}")
    print(f"Articles still needing images: {len(articles) - with_images}")
    
    return articles

if __name__ == "__main__":
    main()