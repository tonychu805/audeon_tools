#!/usr/bin/env python3
import json
import re
from typing import Dict

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
                height = int(width * 0.6)
                return {
                    "url": img_url,
                    "caption": "",
                    "width": width,
                    "height": height
                }
    
    # Look for LinkedIn images
    linkedin_images = re.findall(r'https://media\.licdn\.com/[^)"\s\]]+', content)
    if linkedin_images:
        for img_url in linkedin_images:
            if 'article-cover_image' in img_url or 'article-inline_image' in img_url:
                return {
                    "url": img_url,
                    "caption": "",
                    "width": 1200,
                    "height": 630
                }
    
    # Look for Substack images
    substack_images = re.findall(r'https://substackcdn\.com/[^)"\s\]]+', content)
    if substack_images:
        for img_url in substack_images:
            if 'image/fetch' in img_url and not ('w_64' in img_url or 'w_32' in img_url):
                return {
                    "url": img_url,
                    "caption": "",
                    "width": 1200,
                    "height": 630
                }
    
    # Look for SlideShare images
    slideshare_images = re.findall(r'https://image\.slidesharecdn\.com/[^)"\s\]]+', content)
    if slideshare_images:
        return {
            "url": slideshare_images[0],
            "caption": "",
            "width": 1200,
            "height": 630
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
    nav_elements = [
        r'Sign up', r'Sign in', r'Follow', r'Subscribe', r'Share', r'Listen', 
        r'Medium Logo', r'Write', r'Open in app', r'Follow publication',
        r'View comments?\s*\(\d*\)', r'See all from', r'More from', r'Recommended from Medium',
        r'Help', r'Status', r'About', r'Careers', r'Press', r'Blog', r'Privacy', r'Rules', r'Terms',
        r'protected by \*\*reCAPTCHA\*\*', r'reCAPTCHA', r'Recaptcha requires verification',
        r'Continue to join or sign in', r'User Agreement', r'Privacy Policy', r'Cookie Policy',
        r'LinkedIn', r'New to LinkedIn', r'Join now', r'Others also viewed', r'Show more',
        r'Ad for Scribd subscription', r'Skip to next slide', r'Your browser does not support'
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
        if len(line) < 3:
            continue
        if any(word in line.lower() for word in ['follow', 'subscribe', 'sign up', 'sign in', 'listen', 'skip to']):
            continue
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def estimate_read_time(content: str) -> str:
    """Estimate reading time based on word count"""
    if not content:
        return "5 min read"
    
    words = len(content.split())
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

# Scraped contents from batch 2
scraped_contents = {
    "https://melissaperri.com/blog/2018/10/02/escaping-the-build-trap": "404 - Page Not Found",
    
    "https://www.linkedin.com/pulse/strategy-product-teams-roman-pichler-olf0e": """# Strategy and Product Teams

Strategy and product teams are both key to achieving product success. But what exactly do we mean by strategy? Which one is most relevant for product teams? To what extent should the teams shape strategic decisions? And what role does the head of product play? These are the questions I discuss in this article.

## What is Strategy?

Strategy derives from the ancient Greek word strategos, which means army leader or general. For centuries, the term was primarily used in a military context to describe how battles were fought. Today, there is an abundance of strategies—think of business, marketing, sales, technology, operations, and, of course, product strategy, for example. Fortunately, only a few strategies are important for product teams. These are captured in Figure 1.

The Strategy Stack in Figure 1 consists of five layers and seven elements. These are the business strategy, which is also referred to as corporate strategy, the product portfolio strategy, the technology strategy, and the product strategy, as well as the product roadmap, the technology roadmap, and the product backlog. The backlog is not a strategic plan, but I've added it to the stack to show how strategic decisions can be translated into tactical ones.

Note that I've ordered the elements according to their importance, with the most important at the top. As a consequence, higher-level strategies guide lower-level ones. For example, the business strategy guides the portfolio strategy, which directs the product strategy. The latter, in turn, drives the product roadmap, which directs the product backlog. This creates alignment and ensures that the decisions across the different layers are consistent.

## Product Strategy and Ownership

Out of the four strategies shown in Figure 1, the product strategy is most significant for a product team. It describes the approach chosen to achieve product success. To do this, I find it helpful to describe the following four elements:

- The target group—the users and customers who should benefit from the product.
- The needs—the problem the product should help solve for the users and customers, or the benefit it should offer.
- The business goals—the benefits the product should generate for the company that's developing and providing it.
- The standout features—those aspects that make it special and set it apart from competing offerings.

If you are looking for a tool to capture the product strategy, try my Product Vision Board, which you can download for free together with a handy checklist from my website.

Traditionally, the product strategy is owned by the head of product, the person in charge of the product management group. Sometimes, the role is also called Chief Product Officer and VP or Director of Product Management, depending on the size and structure of the organisation.

Having a single individual in charge of the strategy can offer consistent decision-making and close alignment: Different product teams are guided by the head of product's decisions. However, this approach has several drawbacks, too, including the following four:

- Slow decisions: The head of product can become a bottleneck, especially when the portfolio grows and more products are added. Consequently, decisions might be delayed, and product teams might not be able to quickly progress their products.
- Being overworked: The head of product can become overworked. As a people manager, they have to look after the individual product people and the entire product management group. Consequently, they can experience stress, reduced productivity, and, in the longer term, health issues.
- Strategy-execution chasm: If the product team members don't fully understand or sufficiently buy into the product strategy, a strategy-execution chasm can open up, and the strategy is not effectively translated into detailed product decisions. The UX and product features may therefore not align with the strategy.
- Lack of in-depth knowledge: The head of product might be too far removed from the day-to-day product management work to fully understand the impact of strategic product decisions. At the same time, this can make it difficult to leverage insights from the product discovery and delivery work to adapt and evolve the product strategy—think of user feedback you collect on early product increments, for example. In the worst case, the wrong strategic decisions are taken.

## Empowering Product Teams to Make Strategic Decisions

If having the head of product in charge of product strategy is not always effective, then what's the alternative? My recommendation is to empower product teams to own the strategies of their products. Consequently, a product team is given the authority to create and evolve the product strategy over time. This offers three key benefits:

- Fast decision-making and strategy-execution alignment: The product strategy, discovery, and delivery work are now carried out by the same people. This speeds up the decision-making process and maximises the chances that strategic decisions are effectively executed.
- Increased productivity: As the team now owns a product in its entirety, the members' motivation and productivity are usually increased.
- Value focus: Taking ownership of strategic decisions encourages the team to focus on user and customer needs, as well as business goals, instead of being primarily concerned with product features.

As good as this might sound, there are two key challenges with this solution. First, the product team may lack the necessary expertise to get the product strategy right. Second, the increased autonomy may result in misalignment. In the worst case, different product teams create diverging strategies and take their products in opposite directions. Let's explore how these two challenges can be addressed.

### Upskilling People and Forming Extended Product Teams

A product team that consists of a product person, a developer, and a UX designer is well-equipped to carry out product discovery and delivery work. But such a team often lacks the expertise to make the right strategic product decisions. There are two factors at play: First, the product person does not always have the necessary skills to methodically develop a winning product strategy and an actionable product roadmap. This can be addressed by upskilling the individual, for example, by attending training courses, making time for self-study, and being coached by the head of product.

Second, a small product team usually struggles to make the right decisions to successfully monetise their product. It typically lacks the necessary marketing, sales, support, legal, finance, and operations know-how, depending on the type of product and the company structure. To address this issue, I recommend forming an extended product team.""",

    "https://blackboxofpm.substack.com/p/scaling-conversational-commerce-43fdc3a82a44": """# Scaling Conversational Commerce

We just enabled 325,000 merchants to sell in messaging, without building a bot.

Our team at Shopify has been working on "conversational commerce" for about year now. On Oct 5th, we launched the ability for hundreds of thousands of Shopify merchants to get their products into chat threads and sell directly to their customers through Messenger.

While we were thrilled to get some awesome press coverage, a part of the story that many got wrong was that Shopify had built a bot. We didn't. In the experience you see above, there's no natural language processing, AI, or even character in the responses. Hardly a bot.

We did something subtly different, but powerful: we simply enabled a merchant's product catalogue to exist richly inside of Messenger, and then we got out of the way.

As much as we love the innovation happening in the conversational commerce space, our opinion today is that bots are not the right medium to drive it forward. Instead, we believe that fostering great human conversations between businesses and customers is the right approach.

To unbundle how we got to that line of thinking, it's good to start from the beginning. Our team's exploration of conversational commerce started a year ago with a simple premise, which I'm sharing verbatim from an internal doc I wrote just after we got started:

Commerce is a deeply human behaviour that our species has been doing since the dawn of civilization, and for millennia things have generally stayed the same: people walked into stores and then bought things.

Then a few decades ago, the internet happened and now we rarely go into a store unless we have to. As consumers, we've saved a lot of time, gained more product selection, and received cheaper prices as a result, but something we've lost was the intimacy with a business that we used to have: that interaction with a shopkeeper, whom we shared our needs with and then relied on to find us the right products.

Although the growth of online shopping has been tremendous, we have failed to bring back that intimacy into the user experience. In fact, as good as we've become at designing shopping websites and apps, we really haven't evolved beyond a simple digitization of the Sears catalogue.

Messaging enables us to rekindle the conversations we used to have with businesses, and recapture that lost intimacy.

The key insight of the premise is that conversational commerce is not something new that we have to teach people to do; it's something natural that we took away with the rise of online shopping.

This being Shopify, the thing we did next was to build some shit, in the form a hack days project on the concept. We used Messenger as the exploration canvas but this was way before the Messenger Platform even existed, so basically we made it all up using animation prototypes.

The hack days project that started it all

Exploration #1: Getting into a thread with a business should be seamless and in context.

We explored the scenario of asking a friend who's a product expert in category X for advice.

Exploration #2: When asked a product question by customer, a business would need quick access to their product catalogues so they could easily respond.

We dreamed up this keyboard thing

Exploration #3: Since messaging a business still isn't a common thing, we need a better way to foster conversations.

We landed on a simple button businesses embed on their websites to initiate a conversation

Aside from being hella cool at the time, the discussions and research from the hack days taught us something. Even though online shopping had suppressed our natural commerce-conversation behaviours, people were still finding a way to do it. They were doing it through comments on a business page, through email back and forth with the business, through messaging friends for advice, and by sharing links.

We recognized then that our work in conversational commerce should be less about prescribing the conversation, and more about enabling it. What "enabling it" actually meant, was facilitating the entire customer journey inside of messaging.

This customer journey became our roadmap:

1. Discover — We need a way to get people into conversations.

2. Converse — The biggest one, we need a way for both customers and businesses to have rich commerce conversations so they can agree on the right product.

3. Buy — We need to facilitate a transaction.

4. Support — We need a way to keep an order context in chat after the purchase has been made, in case the customer has a problem or needs to be notified of a change.

From idea to reality

In Shopify parlance, we set out to draw the owl. To be honest, at the time we really had no idea how to actually achieve this because the messaging platforms weren't yet public. Around December 2015, we formally partnered with the Messenger team to make something happen, and got access to some of their private SDKs, as well as explored other technologies we could leverage.

Since the beginning of this year, we've launched a set of products that at first glance may seem like experiments or small features, but upon closer inspection were really all pieces towards enabling the conversational commerce journey.

Feb 22nd, 2016 — We launched Shopkey, an iOS keyboard that gives Shopify businesses their product catalogue in their pocket.

Incredible how close this was to our imagined hack day project

The impact to the customer journey:

Businesses could now seamlessly access their shop from their pocket, and the coolest thing was that as an OS-level keyboard, they could do this in any messaging app and even email.

As cool as this was, we felt this feature only gave us 50% progress on the "Converse" part of the journey, since it only the business had access their products, the customer had no way to browse them on their end.

April 12th, 2016 — We launched Messenger Channel at F8, enabling businesses to start conversations with customers by sending them order receipts and delivery notifications in Messenger.

Businesses could embed this widget into their checkout flow

The impact to the customer journey:

This clearly gave us a check mark on the "Support" section of the journey, but also added 50% to the "Discover" section because it created a chat thread with existing customers, who often used it as a starting point for their next purchase. The downside was still that there was no great way for a new customer to enter into a conversation.

May 30th, 2016 — We quietly shipped a feature that enabled businesses to embed a "Message Us" button onto their online stores

What a business configured in Shopify's admin

Example implementation on a store

The impact to the customer journey:

This bumped up "Discover" to green since it finally enabled new potential customers to have their first transaction with a business go through messaging.

Oct 5, 2016 — We launched the ability to shop in Messenger.

To try it out just message the page: 

Customers can now access a Shopify business' products in Messenger, share them with friends, and checkout via web-view from the app.

The impact to the customer journey:

This completed the second half of the "Converse" part of the journey by also enabling customers to explore and bring up products in conversations. It also made progress on the payments front, but the experience can still be improved so we're leaving that at yellow for now.

A complete journey, if still imperfect

Those four product launches collectively completed the customer journey we had set out to build nine months prior. In retrospect, it's crazy to reflect on how close some of our earliest — completely made up - hack days ideas came to fruition, and that's exactly what I was doing when I wrote this tweet on launch day:

Human conversations are still the most important

Our team isn't close to done, we will continue to dive deeper into rekindling the natural interactions of commerce and conversation. But today, we can confidently say that hundreds of thousands of businesses on Shopify can facilitate an entire customer journey through messaging, and they will do so with their own words.

Only time will tell how both customers and businesses adopt these interactions at scale, but if there's anything that Shopify's product history has taught us, it's that businesses will use the tools you give them in ways that you cannot predict, and will ultimately unlock more potential from them that you ever anticipated.

Wait, what about bots? Why didn't we build them?

Because we want the developer ecosystem to do it for us.

Shopify is a platform for hundreds of thousands of businesses, and with that comes enormous diversity. It's that diversity which makes creating generalized bots for every business so difficult:

1. Shopify businesses care deeply about their brands, and their customers care about the people behind them. Bots can take away the voice of your brand.

2. AI isn't ready for the diversity of businesses on Shopify. We all love Dominoes pizza bot, or Uber's bot, but the reason they can delight users is because are for a single use case and brand. Shopify's 300,000+ merchants sell products accross hundreds of product categories, and in as many languages; there is no generalized NLP and/or AI that can currently handle that diversity.

To build great bots would mean building hundreds of them, specific to the needs of each niche, which is something that would take us too long to do.

But that doesn't mean the developer ecosystem can't.""",

    "https://www.sachinrekhi.com/the-art-of-product-management": """# The Art of Product Management

Product managers drive the vision, strategy, design, and execution of their product.

While one can often quickly comprehend the basic responsibilities of the role, mastering each of these dimensions is truly an art form that one is constantly honing.

## Vision

A compelling vision articulates how the world will be a better place if you succeed

The Best Format: A Customer-Centric Vision Narrative

"Full sentences are harder to write. They have verbs. The paragraphs have a genuine logical structure. Humans can't often write complete nonsense when they are forced to write using full sentences."

Vision Narrative: Amazon.com 1997 Shareholder Letter

"But this is Day 1 for the Internet and, if we execute well, for Amazon.com. Today, online commerce saves customers money and precious time. Tomorrow, through personalization, online commerce will accelerate the very process of discovery."

Vision Narrative: PayPal Speech in 1999

"The need PayPal answers is monumental. Paper money is an ancient technology and an inconvenient means of payment. You can run out of it. It wears out. It can get lost or stolen. In the 21st century, people need a form of money that's more convenient and secure, something that can be accessed from anywhere with a PDA or an internet connection."

Vision Narrative: Apple Introduces the iPhone in 2007

"Most advanced phones are called smart phones. They combine a phone plus some e-mail capability, plus they say it's the internet. It's sort of the baby internet. It's not really the internet, it's kind of the baby internet. And they're not so smart and they're not so easy to use, and so if you kind of make a Business School 101 graph of the smart axis and the easy-to-use axis, you can see that they don't do a great job. What we want to do is make a leapfrog product that is way smarter than any mobile device has ever been, and super-easy to use."

Communicating The Vision

A vision is valuable only if it inspires the entire team

Communicating The Vision: The Power of Repetition

Just as it takes 7 impressions to garner a response to a marketing message, it takes countless repetitions of a vision to have it resonate with a team.

## Strategy

A compelling strategy details exactly how you'll dominate your market

A vision should be stable, but your strategy needs to be iterated on and refined until you find product/market fit

Best Format: Product/Market Fit Hypotheses

Ditch the business plan; instead focus on a few-page summary that captures each of your hypotheses for achieving product/market fit

The Product/Market Fit Hypotheses

1. Target Audience
2. Problem You're Solving
3. Value Propositions
4. Strategic Differentiation
5. Competition
6. Acquisition Strategy
7. Monetization Strategy
8. KPIs

1. Target Audience

This is not your pitch deck, so don't think about the broadest possible definition of your TAM Instead think about the narrowest possible definition of customers for whom you're creating 10x value

2. Problem You're Solving

Is the problem you're solving for your customer a vitamin or a painkiller?

3. Value Propositions

Not the feature list, but instead the promise to your customer on the value you will deliver for them

4. Strategic Differentiation

Why is your solution 10x better than the leading alternatives?

5. Competition

How will your solution win against direct competitors and indirect alternatives?

6. Acquisition Strategy

How will you find & attract your potential customers? And how will you do so cost-effectively?

7. Monetization Strategy

What are your primary and secondary ways to make money? Is there strong willingness to pay?

8. KPIs

What are the right metrics for you to know if you are headed in the right direction?

Minimize your dimensions of innovation

Don't innovate on ALL dimensions

## Design

A compelling design delivers a useful, usable, and delightful experience to your customers

Delivering a useful & usable product has proven techniques, but how do you build truly delightful experiences?

By bringing emotional intelligence to your product design

Start by falling in love with the problem you are solving for your target customers

But not… with the solution

Develop Personas

Personas are fictional characters developed to represent the different archetypes of users of your product

Increase Exposure Hours

"It's the closest thing we've found to a silver bullet when it comes to reliably improving the designs teams produce."

Deliver delight by adding a desired emotion dimension to your product design process

Delight Through Attention to Detail

Slack sweats the details: Emojis, Onboarding, Animations, Reliable Notifications

Measure Delight Through Net Promoter Score (NPS)

High EQ: Facebook Sharing

Facebook not only made the sharing process frictionless, but more importantly provided instant social validation through likes and comments

High EQ: Instagram Filters

Instagram made your mundane photos share-worthy in seconds with beautiful photo filters

High EQ: Slack's Watercooler

Slack brought the classic R&D team watercooler conversation right into Slack through common channels

## Execution

Relentless execution ultimately determines whether you'll make your vision a reality

Execution isn't just project management, but doing whatever it takes to win

You must also ensure you're pointing the team in the right direction

Execution Loop: Define. Validate. Iterate.

1. Define your hypotheses
2. Validate each hypothesis
3. Iterate based on learnings

#1 Goal: Increase execution loop velocity

Fast iteration requires clear decision rights

Who owns this decision?

But… no shortcut for building shared context

Establish yourself as the curator, not the creator of great ideas

Favor decisions today over decisions tomorrow

The enemy of decision-making is time

Reward engineering velocity over elegance

Instead of rewarding teams with elegant architectural solutions to yesterday's problems, reward teams that rapidly iterate and discover the right problems to solve and minimum viable solutions to test

Invest in Retrospectives

Improve your ability to accurately forecast (and ultimately improve) engineering cost & product outcomes through retrospectives

Metrics: Learn to Read the Matrix

Build your intuition for metrics by spending time every day reviewing a few critical acquisition, activation, engagement, retention, referral, and revenue metrics""",

    "https://www.sachinrekhi.com/annual-planning-and-the-art-of-roadmapping": "Blog post not found."
}

def main():
    """Update articles with batch 2 scraped content"""
    json_file = "/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json"
    
    with open(json_file, 'r', encoding='utf-8') as f:
        articles = json.load(f)
    
    updated_count = 0
    failed_urls = []
    
    for article in articles:
        url = article["url"]
        
        if url in scraped_contents:
            scraped_content = scraped_contents[url]
            
            # Handle 404 or inaccessible URLs
            if "404" in scraped_content or "Page Not Found" in scraped_content or "Blog post not found" in scraped_content:
                failed_urls.append(url)
                print(f"❌ Failed to scrape: {article['title']} - URL not accessible")
                continue
            
            # Clean and update content
            cleaned_content = clean_content_for_audio(scraped_content)
            article["full_content"] = cleaned_content
            
            # Update read time
            article["read_time"] = estimate_read_time(cleaned_content)
            
            # Extract and update main image
            main_image = extract_main_image_from_content(scraped_content)
            if main_image["url"]:
                article["main_image"] = main_image
            
            updated_count += 1
            print(f"✅ Updated: {article['title']}")
    
    print(f"\n📊 Batch 2 Results:")
    print(f"Successfully updated: {updated_count}")
    print(f"Failed URLs: {len(failed_urls)}")
    for url in failed_urls:
        print(f"  - {url}")
    
    # Save updated articles
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved updated articles to {json_file}")

if __name__ == "__main__":
    main()