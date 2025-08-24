#!/usr/bin/env python3
"""
Batch update articles with scraped content from successful WebFetch calls
"""
import json
import re

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

def update_article(file_path: str, track_id: int, content: str):
    """Update a specific article with content"""
    with open(file_path, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    # Find and update the article
    for article in articles:
        if article['track_id'] == track_id:
            cleaned_content = clean_content(content)
            article['full_content'] = cleaned_content
            article['read_time'] = estimate_read_time(cleaned_content)
            print(f"✅ Updated Track {track_id}: {article['title']}")
            break
    
    # Save the updated articles
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

def main():
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    
    # Content from successful WebFetch calls
    
    # Track 37 - Building a Culture of Accountability for Empowered Product Teams
    track_37_content = """# Building a Culture of Accountability for Empowered Product Teams

Originally published: March 15, 2023 by Teresa Torres | Last updated: September 16, 2024

**Have you heard?** My new book [_Continuous Discovery Habits_](https://amzn.to/3hGkNYT) is now available. Get the product trio's guide to a structured and sustainable approach to continuous discovery.

_I recently sat down with fellow Product Talk coach and instructor [Hope Gurion](https://fearless-product.com/about-me) to discuss how leaders can hold empowered [product teams](https://www.producttalk.org/2024/06/product-trios/) accountable to [outcomes](https://www.producttalk.org/2024/07/shifting-from-outputs-to-outcomes/)._

_You can watch the video of our conversation or check out a lightly edited version of the transcript below._

## Full Transcript

### What Is an Empowered Product Team?

**Hope Gurion** describes an empowered product team as having:
- Clarity of purpose
- A clear measure of success (outcome)
- Discretion over how they spend time
- Working towards an important company goal

### Autonomous vs. Empowered Teams: What's the Difference?

Empowered teams are not completely autonomous. They:
- Have high decision-making power
- Recognize their contribution to company value streams
- May need to handle inter-team dependencies
- Are not completely isolated from organizational expectations

### Focusing on Outcomes and Strategic Impact

Key points about empowered teams:
- Leaders set strategic context
- Teams reach outcomes consistent with that context
- Not every moment is spent on the primary outcome
- Some time is dedicated to "keep the lights on" work

### How Do You Hold Empowered Teams Accountable?

Recommended accountability practices:
1. Regular "discovery demos" every 2-3 weeks
   - Teams share learning
   - Focus on progress towards outcomes
   - Cross-team learning opportunity

2. Quarterly reviews
   - Comprehensive look at quarter's learning
   - Assess impact on outcome
   - Plan for next quarter"""

    # Track 40 - Roman's Product Strategy Model
    track_40_content = """# Roman's Product Strategy Model

## Introduction

Making the right strategic decisions is crucial to achieve product success. Many product teams lack a systematic approach to creating and evolving a product strategy.

## The Model

Roman Pichler developed a product strategy model with four key artifacts:

1. **Product Vision**: The ultimate purpose and positive change a product aims to create. 
   - Example: "help people eat healthily"

2. **Product Strategy**: The approach to realizing the vision, involving four key choices:
   - Selecting needs to address
   - Determining target market
   - Choosing standout features
   - Setting business goals

3. **Product Roadmap**: Describes strategy implementation over 6-12 months
   - Based on product goals
   - Includes dates, features, and metrics

4. **Product Backlog**: Tactical items derived from roadmap goals

## Key Principles

- Strategy validation is critical
- Decisions become more specific as you move from vision to backlog
- The process is cyclical and bidirectional
- Collaborative workshops are essential for buy-in

## Validation Process

The model emphasizes an iterative, risk-driven validation approach using Lean Startup and Design Thinking principles.

## Collaborative Approach

The product leader leads strategy workshops, with a Scrum Master facilitating to ensure:
- Expertise is leveraged
- Shared understanding is created
- Maximum stakeholder buy-in

The full article provides detailed insights into each component of Roman Pichler's product strategy model."""

    # Track 42 - Are You Data-driven, Data-informed or Data-inspired?
    track_42_content = """# Are You Data-driven, Data-informed or Data-inspired?

Have you noticed recently an increase in the usage of the terms 'data-driven', 'data-informed', and 'data-inspired' around your office? It might seem like your co-workers are just jumping on the buzzword bandwagon and throwing words around. But, you would be remiss to completely ignore them because these three phrases hold powerful meaning and are incredibly useful if you know what they represent and how to apply them correctly.

## What Do These Terms Mean?

Data-driven, data-informed, and data-inspired describe how data should be used:

- **Data-driven**: You have the exact data needed to make a decision. As the author states, it will "tell you exactly the answer you need to know in terms of what to do next."

- **Data-informed**: Everyone is aware of the current performance and why the product is performing the way it is in order to make optimizations to your strategies.

- **Data-inspired**: Means trendspotting. This takes a few different data sources to put the story together since predicting future customer expectations is difficult to do with one data source.

## Best Practices

The best-case scenario is teams establish mindsets to leverage all three use cases because:

1. Using these terms properly removes friction between teams
2. They ensure teams are using data properly

## Data-Driven Approach

### Characteristics:
- Requires a predetermined measurement plan
- Needs a predetermined sample size
- Involves team members with statistical methodology knowledge

### Best Use Cases:
- Answering specific business questions
- Ensuring product changes won't negatively impact the business

### Example Questions:
- When is the best time to release a product?
- What design performs better?
- How much money will we make next month?

### Limitations:
- Data is one-dimensional
- Should validate solutions, not guide new strategies

## Data-Informed Approach

### Key Characteristics:
- Understand performance of KPIs
- Know both "what and why"
- Refine future strategies based on insights

### Best Use Cases:
- Strategizing product changes
- Prioritizing feature backlogs

## Data-Inspired Approach

### Key Characteristics:
- Identify emerging trends
- Combine multiple data sources
- Predict future customer expectations"""

    # Track 51 - How to Scale the Scrum Product Owner
    track_51_content = """# How to Scale the Scrum Product Owner

By Roman Pichler

## Scaling and the Product Life Cycle

The article discusses three main approaches to scaling the product owner role, depending on the product's life cycle stage:

### Key Principles
- For young products, keep a single product owner
- As products grow, consider sharing responsibilities
- The scaling approach should match the product's maturity level

## Scaling Options

### Option 1: Feature and Component Owners
- Suitable from near product-market fit to maturity
- Overall product owner manages strategy and stakeholders
- Feature/component owners manage specific product assets

### Option 2: Unbundling and Product Variants
- Break up the product into separate offerings
- Create new products with dedicated owners
- Examples: Facebook Messenger, iPod variants

### Option 3: Strategic and Tactical Product Roles
- Separate strategic (product manager) and tactical (product owner) roles
- Best used when product is stable/mature
- Risks misalignment if used too early in product lifecycle

## Recommended Approach

| Option | When to Use |
|--------|-------------|
| Single product owner | Before product-market fit |
| Product and feature owners | Close to product-market fit to maturity |
| Product variants/unbundling | As needed |
| Strategic and tactical roles | When product is stable/mature |

The key is to select the scaling technique that best supports the product's current stage and future success."""

    # Update all articles
    update_article(file_path, 37, track_37_content)
    update_article(file_path, 40, track_40_content)
    update_article(file_path, 42, track_42_content)
    update_article(file_path, 51, track_51_content)
    
    print("Updated 4 articles successfully!")

if __name__ == "__main__":
    main()