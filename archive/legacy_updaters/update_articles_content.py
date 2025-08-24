#!/usr/bin/env python3
"""
Update articles with scraped content manually
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
    
    # Content for Track 16 - Teresa Torres article
    track_16_content = """# Everyone Can Do Continuous Discovery—Even You! Here's How

Originally published: August 2, 2023 by Teresa Torres | Last updated: August 1, 2024

Have you heard? My new book Continuous Discovery Habits is now available. Get the product trio's guide to a structured and sustainable approach to continuous discovery.

One of the most common responses I get when I talk about continuous discovery is: "That would never work in my organization." But after working with thousands of product people and organizations of all kinds, I can tell you that everyone is capable of making progress on their continuous discovery journey.

It's all about finding the small steps you can take to build these habits.

While I understand that every situation is unique, I tend to see three main categories of resistance to continuous discovery. Luckily, I have some recommendations for how to overcome each type of resistance and meet people where they are.

## The Three Common Scenarios

### 1. The Feature Factory
In this scenario, you're given a backlog of features to build and told to just ship them. There's no time for discovery, and you're measured solely on output.

**What you can do:**
- Start identifying hidden assumptions in your features
- Ask "What needs to be true for this feature to be successful?"
- Begin documenting these assumptions, even if you can't test them immediately
- Look for small opportunities to validate assumptions

### 2. The Messy Middle
You have some autonomy but inconsistent support for discovery. Sometimes you can do research, sometimes you can't.

**What you can do:**
- Create small experiments within your existing workflow
- Interview customers during user testing sessions
- Use customer support tickets as discovery insights
- Build allies who support discovery practices

### 3. Reverting to Old Habits
You start with good intentions but gradually slip back into building without discovery.

**What you can do:**
- Create systems and reminders to maintain discovery habits
- Set weekly discovery goals
- Make discovery visible to your team and stakeholders
- Celebrate discovery wins, no matter how small

## The Key: Start Where You Are

The most important thing is to start where you are, not where you think you should be. Every organization can take steps toward continuous discovery, even if they're small ones.

Remember: perfect is the enemy of good. Any amount of customer contact and assumption testing is better than none.

## Building Discovery Habits

The goal is to build sustainable habits, not to achieve perfection overnight. Focus on:

- Weekly customer contact
- Regular assumption mapping
- Small-scale testing and validation
- Creating "bright spots" in your organization

These habits compound over time and create organizational change from the ground up."""

    # Content for Track 32 - Build vs Buy in the Age of AI
    track_32_content = """# Build vs Buy in the Age of AI

One topic that has been around since the beginning of the tech industry is whether we should build or buy in order to solve some problem.

This question applies to traditional IT, as well as to every product team.

There are often one or more buy alternatives, but each comes with an associated cost, and usually limitations in functionality. Building comes with its own well-known challenges, both in terms of creation time and cost, and ongoing maintenance.

## Key Insights

### Historical Approach
- For most companies, if the problem represents a core competency, they usually build
- If the problem is outside core competency, they try to buy
- Many problems are too specialized to have buy options

### The Rise of User Programming
- Started in 1979 with VisiCalc spreadsheet
- Enabled non-technical people to create "programs"
- Generative AI is now creating a new generation of user-programming tools

### The Future of Business Software
Cagan argues that business software won't be entirely replaced by user-programmed solutions because:
- Complex business solutions have thousands of intricate business rules
- Most non-technical people don't understand these complex business logic requirements

### Emerging Model
The future of "build vs buy" will likely be "yes to both":
- Companies will continue buying complex component services
- These components will be designed for both human and AI agent access
- AI agents will be created by vendors, system integrators, and end customers

## Key Takeaway
"The hard part is rarely building and delivering the solution; the hard part is discovering the right solution to build.\""""

    # Content for Track 34 - Product management trends 2025
    track_34_content = """# Product management trends 2025: 10 predictions for the future

In 2025, artificial intelligence (AI) is set to transform every stage of the product lifecycle—from how teams plan and build to how they launch, learn, and iterate. This shift isn't just changing what product teams deliver—it's fundamentally redefining their roles and how they work.

## Key Trends

### 1. AI-Powered Product Strategy

According to the report, "76% of product leaders expect their investment in AI to grow next year." AI is helping teams:
- Write product briefs quickly
- Match roadmap initiatives to strategic goals
- Automate launch updates
- Manage complex organizational budgets

### 2. From Features to Revenue

The report highlights that "92% of product leaders now own revenue outcomes." This means:
- Embracing product-led growth
- Partnering across sales, marketing, and customer success
- Connecting product development to market performance

### 3. Depth Over Breadth

Product leaders currently spend "more than 66% of their week on manual work." AI is expected to:
- Automate routine tasks
- Enable deeper expertise
- Shift focus from generalist to specialist roles

### 4. Smarter Feedback Loops

Currently, "40% of leaders still rely on teams of humans to parse, analyze, and make sense of ever-growing volumes of feedback." AI will help by:
- Analyzing feedback across multiple channels
- Identifying real-time trends
- Prioritizing insights more effectively

### 5-10. Additional Trends

The article outlines five more key trends:
- A strong product point of view
- AI-powered workflow automation
- Enhanced market intelligence
- Digital product centrality
- Rise of the full-stack product manager
- Accelerated category disruption cycles

## The Future of Product Management

The core message is that AI is transforming product management, making teams faster, more strategic, and more impact-driven. Success will belong to teams willing to "rethink assumptions, ask sharper questions, and continuously adapt.\""""

    # Content for Track 49 - Kano Model
    track_49_content = """# The Complete Guide to the Kano Model

## Introduction

The article is a comprehensive guide to the Kano Model, a methodology for understanding customer satisfaction with product features. It was written by Daniel Zacarias and published on Folding Burritos.

## Key Concepts of the Kano Model

### Satisfaction vs. Functionality

The Kano Model introduces two key dimensions:
- **Satisfaction**: Ranging from total satisfaction (delight) to total dissatisfaction
- **Functionality**: Representing how much of a feature is implemented

### Four Categories of Features

1. **Performance Features**: Linear relationship between functionality and satisfaction
2. **Must-be Features**: Basic expectations that don't increase satisfaction
3. **Attractive Features**: Unexpected features that delight customers
4. **Indifferent Features**: Features customers don't care about

### The Kano Questionnaire

The model uses a pair of questions for each feature:
- How do you feel if you have the feature?
- How do you feel if you do not have the feature?

## Using the Kano Model

The guide outlines a three-step process:

1. **Choose Features and Users**
   - Select features with meaningful user benefits
   - Choose a specific customer demographic or persona

2. **Gather Customer Data**
   - Write clear, benefit-focused questions
   - Use visual prototypes when possible
   - Ask about feature importance

3. **Analyze Results**
   - Use discrete or continuous analysis methods
   - Prioritize features based on customer satisfaction potential

## Practical Implementation

The article provides a practical approach to conducting a Kano analysis:
- Select 3 features maximum
- Choose 15+ customers per demographic
- Create an interactive survey
- Use provided analysis tools and spreadsheets

## Conclusion

The Kano Model is a tool to help product managers and designers understand and prioritize features that create customer satisfaction and delight."""

    # Content for Track 50 - Jobs to Be Done
    track_50_content = """# Know Your Customers' "Jobs to Be Done"

## By Clayton M. Christensen, Taddy Hall, Karen Dillon, and David S. Duncan

### Idea in Brief

Innovation success rates are shockingly low worldwide. Marketers and product developers focus too much on customer profiles and data correlations, instead of understanding what customers are truly trying to achieve in a specific circumstance.

### The Core Concept: Jobs to Be Done

The fundamental problem with most innovation approaches is that companies rely too heavily on correlational data about customers. Instead, businesses should focus on understanding the "job to be done" - the specific progress a customer wants to make in a given circumstance.

> When we buy a product, we essentially "hire" it to help us do a job.

### Key Principles of Jobs to Be Done

1. Jobs are complex and multifaceted
2. Circumstances matter more than customer characteristics
3. Jobs have functional, social, and emotional dimensions
4. Good innovations solve problems with previously inadequate solutions

### Case Study: Condo Development

The authors describe a condo development project where sales were initially poor. By understanding the deeper "job" customers were trying to accomplish - transitioning their lives and managing emotional attachments to possessions - the developers transformed their approach.

Key changes included:
- Providing moving services
- Offering storage solutions
- Creating space for meaningful items like dining room tables

### Designing Around Jobs

Successful innovations like American Girl dolls and Reese's Minis demonstrate how understanding the specific job customers need done can drive product development.

### Organizational Alignment

Companies must align their processes, experiences, and offerings around the job to be done. Southern New Hampshire University's online education program exemplifies this approach by redesigning everything to support adult learners' specific needs.

### Conclusion

> Innovation can be far more predictable—and far more profitable—if you start by identifying jobs that customers are struggling to get done.

The article argues that by shifting focus from demographic data to understanding customers' fundamental goals, companies can create more meaningful and successful innovations."""

    # Update articles
    update_article(file_path, 16, track_16_content)
    update_article(file_path, 32, track_32_content)
    update_article(file_path, 34, track_34_content)
    update_article(file_path, 49, track_49_content)
    update_article(file_path, 50, track_50_content)
    print("Updated articles 16, 32, 34, 49, and 50 with content")

if __name__ == "__main__":
    main()