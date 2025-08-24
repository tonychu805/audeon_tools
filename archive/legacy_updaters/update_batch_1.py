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
        if len(line) < 3:
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
    minutes = max(1, round(words / 200))
    return f"{minutes} min read"

# Scraped contents from batch 1
scraped_contents = {
    "https://a16z.com/good-product-managerbad-product-manager/": "404 - Page Not Found",
    "https://www.bringthedonuts.com/donuts/": """# What's the Deal With the Donuts?

## Why have donuts and product management become synonymous?

I believe the best product managers are willing to do whatever it takes to help their teams succeed. An important aspect of that is recognizing that PMs often have to do the work that would fall through the cracks otherwise. By definition that can be grimy, un-fun work: cleaning the bug queue, organizing a document repository, replying to a customer support email. No job should be beneath a product manager. PMs are more humble servants than "CEOs of the product." They put their teams first, they do what needs to be done, and they demonstrate that every day.

In 2005 I was preparing to give a talk at Berkeley's Haas School of Business about product management. I was looking for a rhetorical device to convey this and I settled on "bring the donuts." If PMs don't bring donuts for the team on launch day, who else will? I'm not sure why I picked donuts. At the time my competitive cycling career was still flourishing and bagels were more my style. But donuts it was, and the concept stuck.

Since then, product management and donuts have sort of become synonymous. People message me on social media with photos of the donuts they're bringing, PM meetups and conferences serve donuts, and when I meet an early career PM, there's a good chance they'll bring donuts too (a practice my officemates wholeheartedly endorse.)

One of my favorite quotes comes from this Buzzfeed interview with Jason Goldman:

"Startups are run by people who do what's necessary at the time it's needed. A lot of time that's unglamorous work. A lot of times that's not heroic work. Is that heroic? Is that standing on a stage in a black turtleneck, in front of 20,000 people talking about the future of phones? No. But that's how companies are built. That person who did that for the iPhone launch at Apple, we don't know who he is. All we know is that Steve Jobs came up with the iPhone. But he didn't ship it. The person who bought the donuts did."

So, keep bringing those donuts.""",

    "https://pmarchive.com/guide_to_startups_part4.html": """This post is all about the only thing that matters for a new startup.

But first, some theory:

If you look at a broad cross-section of startups—say, 30 or 40 or more; enough to screen out the pure flukes and look for patterns—two obvious facts will jump out at you.

First obvious fact: there is an incredibly wide divergence of success—some of those startups are insanely successful, some highly successful, many somewhat successful, and quite a few of course outright fail.

Second obvious fact: there is an incredibly wide divergence of caliber and quality for the three core elements of each startup— team, product, and market.

At any given startup, the team will range from outstanding to remarkably flawed; the product will range from a masterpiece of engineering to barely functional; and the market will range from booming to comatose.

And so you start to wonder—what correlates the most to success— team, product, or market? Or, more bluntly, what causes success? And, for those of us who are students of startup failure— what's most dangerous: a bad team, a weak product, or a poor market?

Let's start by defining terms.

The caliber of a startup team can be defined as the suitability of the CEO, senior staff, engineers, and other key staff relative to the opportunity in front of them.

You look at a startup and ask, will this team be able to optimally execute against their opportunity? I focus on effectiveness as opposed to experience, since the history of the tech industry is full of highly successful startups that were staffed primarily by people who had never "done it before".

The quality of a startup's product can be defined as how impressive the product is to one customer or user who actually uses it: How easy is the product to use? How feature rich is it? How fast is it? How extensible is it? How polished is it? How many (or rather, how few) bugs does it have?

The size of a startup's market is the the number, and growth rate, of those customers or users for that product.

(Let's assume for this discussion that you can make money at scale—that the cost of acquiring a customer isn't higher than the revenue that customer will generate.)

Some people have been objecting to my classification as follows: "How great can a product be if nobody wants it?" In other words, isn't the quality of a product defined by how appealing it is to lots of customers?

No. Product quality and market size are completely different.

Here's the classic scenario: the world's best software application for an operating system nobody runs. Just ask any software developer targeting the market for BeOS, Amiga, OS/2, or NeXT applications what the difference is between great product and big market.

So:

If you ask entrepreneurs or VCs which of team, product, or market is most important, many will say team. This is the obvious answer, in part because in the beginning of a startup, you know a lot more about the team than you do the product, which hasn't been built yet, or the market, which hasn't been explored yet.

Plus, we've all been raised on slogans like "people are our most important asset"—at least in the US, pro-people sentiments permeate our culture, ranging from high school self-esteem programs to the Declaration of Independence's inalienable rights to life, liberty, and the pursuit of happiness—so the answer that team is the most important feels right.

And who wants to take the position that people don't matter?

On the other hand, if you ask engineers, many will say product. This is a product business, startups invent products, customers buy and use the products. Apple and Google are the best companies in the industry today because they build the best products. Without the product there is no company. Just try having a great team and no product, or a great market and no product. What's wrong with you? Now let me get back to work on the product.

Personally, I'll take the third position—I'll assert that market is the most important factor in a startup's success or failure.

Why?

In a great market—a market with lots of real potential customers—the market pulls product out of the startup.

The market needs to be fulfilled and the market will be fulfilled, by the first viable product that comes along.

The product doesn't need to be great; it just has to basically work. And, the market doesn't care how good the team is, as long as the team can produce that viable product.

In short, customers are knocking down your door to get the product; the main goal is to actually answer the phone and respond to all the emails from people who want to buy.

And when you have a great market, the team is remarkably easy to upgrade on the fly.

This is the story of search keyword advertising, and Internet auctions, and TCP/IP routers.

Conversely, in a terrible market, you can have the best product in the world and an absolutely killer team, and it doesn't matter— you're going to fail.

You'll break your pick for years trying to find customers who don't exist for your marvelous product, and your wonderful team will eventually get demoralized and quit, and your startup will die.

This is the story of videoconferencing, and workflow software, and micropayments.

In honor of Andy Rachleff, formerly of Benchmark Capital, who crystallized this formulation for me, let me present Rachleff's Law of Startup Success:

The #1 company-killer is lack of market.

Andy puts it this way:

- When a great team meets a lousy market, market wins.
- When a lousy team meets a great market, market wins.
- When a great team meets a great market, something special happens.

You can obviously screw up a great market—and that has been done, and not infrequently—but assuming the team is baseline competent and the product is fundamentally acceptable, a great market will tend to equal success and a poor market will tend to equal failure. Market matters most.

And neither a stellar team nor a fantastic product will redeem a bad market.

OK, so what?

Well, first question: Since team is the thing you have the most control over at the start, and everyone wants to have a great team, what does a great team actually get you?

Hopefully a great team gets you at least an OK product, and ideally a great product.

However, I can name you a bunch of examples of great teams that totally screwed up their products. Great products are really, really hard to build.

Hopefully a great team also gets you a great market—but I can also name you lots of examples of great teams that executed brilliantly against terrible markets and failed. Markets that don't exist don't care how smart you are.

In my experience, the most frequent case of great team paired with bad product and/or terrible market is the second- or third-time entrepreneur whose first company was a huge success. People get cocky, and slip up. There is one high-profile, highly successful software entrepreneur right now who is burning through something like $80 million in venture funding in his latest startup and has practically nothing to show for it except for some great press clippings and a couple of beta customers—because there is virtually no market for what he is building.

Conversely, I can name you any number of weak teams whose startups were highly successful due to explosively large markets for what they were doing.

Finally, to quote Tim Shephard: "A great team is a team that will always beat a mediocre team, given the same market and product."

Second question: Can't great products sometimes create huge new markets?

Absolutely.

This is a best case scenario, though.

VMWare is the most recent company to have done it—VMWare's product was so profoundly transformative out of the gate that it catalyzed a whole new movement toward operating system virtualization, which turns out to be a monster market.

And of course, in this scenario, it also doesn't really matter how good your team is, as long as the team is good enough to develop the product to the baseline level of quality the market requires and get it fundamentally to market.

Understand I'm not saying that you should shoot low in terms of quality of team, or that VMWare's team was not incredibly strong—it was, and is. I'm saying, bring a product as transformative as VMWare's to market and you're going to succeed, full stop.

Short of that, I wouldn't count on your product creating a new market from scratch.

Third question: as a startup founder, what should I do about all this?

Let's introduce Rachleff's Corollary of Startup Success:

The only thing that matters is getting to product/market fit.

Product/market fit means being in a good market with a product that can satisfy that market.

You can always feel when product/market fit isn't happening. The customers aren't quite getting value out of the product, word of mouth isn't spreading, usage isn't growing that fast, press reviews are kind of "blah", the sales cycle takes too long, and lots of deals never close.

And you can always feel product/market fit when it's happening. The customers are buying the product just as fast as you can make it—or usage is growing just as fast as you can add more servers. Money from customers is piling up in your company checking account. You're hiring sales and customer support staff as fast as you can. Reporters are calling because they've heard about your hot new thing and they want to talk to you about it. You start getting entrepreneur of the year awards from Harvard Business School. Investment bankers are staking out your house. You could eat free for a year at Buck's.

Lots of startups fail before product/market fit ever happens.

My contention, in fact, is that they fail because they never get to product/market fit.

Carried a step further, I believe that the life of any startup can be divided into two parts: before product/market fit (call this "BPMF") and after product/market fit ("APMF").

When you are BPMF, focus obsessively on getting to product/market fit.

Do whatever is required to get to product/market fit. Including changing out people, rewriting your product, moving into a different market, telling customers no when you don't want to, telling customers yes when you don't want to, raising that fourth round of highly dilutive venture capital—whatever is required.

When you get right down to it, you can ignore almost everything else.

I'm not suggesting that you do ignore everything else—just that judging from what I've seen in successful startups, you can.

Whenever you see a successful startup, you see one that has reached product/market fit—and usually along the way screwed up all kinds of other things, from channel model to pipeline development strategy to marketing plan to press relations to compensation policies to the CEO sleeping with the venture capitalist. And the startup is still successful.

Conversely, you see a surprising number of really well-run startups that have all aspects of operations completely buttoned down, HR policies in place, great sales model, thoroughly thought-through marketing plan, great interview processes, outstanding catered food, 30" monitors for all the programmers, top tier VCs on the board— heading straight off a cliff due to not ever finding product/market fit.

Ironically, once a startup is successful, and you ask the founders what made it successful, they will usually cite all kinds of things that had nothing to do with it. People are terrible at understanding causation. But in almost every case, the cause was actually product/market fit.

Because, really, what else could it possibly be?""",

    "https://medium.com/@rjs/products-are-functions-ca697b13dda6": "404 - Page Not Found", 

    "https://www.svpg.com/best-vs-rest-faq/": """# Best vs. Rest FAQ

In my last article I discussed the two different product worlds that I straddle, and I heard from quite a few people from each of the two camps, as well as several that shared that they've worked in both. I thought it might be useful to share the most common follow-up questions and my responses:

Q: I want to learn more about the best companies – not just the techniques that you share in your writing, but more about their cultures and their broader views on product. How can I learn more?

A: The four large strong product companies I most commonly cite are Apple, Amazon, Google and Netflix. Many books and articles have been written about each, but of those that I've read (I have read quite a few but certainly not all of them), these are the ones that I think do the best job of sharing what's important.

There is an important caveat here. When an author writes a book, she is sharing what she considers most important and relevant. When I write a book or an article, I am doing the same thing. In my case, I've been heavily influenced by my discussions with current and former product people from these companies, and obviously I also bring a strong product bias. So, realize you are always getting a view on the company through a particular lens.

Apple is the most secretive commercial company I know. Most books that have been written about them are about their colorful co-founder, and much less about the inner workings. My favorite book on how the actual work of product is done at Apple is Creative Selection by former engineering lead Ken Kocienda. Ken worked on some of the company's most important products and technologies, during what I'd consider the peak innovation period for the company (so far).

Amazon is the least secretive, as their founder Jeff Bezos has been sharing truly valuable insights into product and leadership since the early days of the company. The new book Working Backwards by long-time Amazonians Colin Bryar and Bill Carr does the best job so far in highlighting the important aspects of how the company has created such a consistent machine for innovation.

Google is a tougher one because it's a very large and sprawling company where one team in one group can often work very different than another. But there are common principles and my favorite book (so far) is How Google Works by former CEO Eric Schmidt, and former head of product Jonathan Rosenberg.

By far my favorite book on Netflix is the newly released No Rules Rules by co-founder Reed Hastings along with Erin Meyer. Most of what's been written prior on Netflix is more origin story than innovation engine, and this book gives you a good look at a company that sets the empowerment dial to 10.

Q: I want to give my CEO some books on the value of empowerment as a general leadership strategy. Are there books like that?

A: There are so many. These are my top 10 favorites:

- Leaders Eat Last
- Startup Nation
- The Art of Action
- Culture Code
- Principles: Life and Work
- Creativity, Inc
- Legacy
- Extreme Ownership
- Team of Teams
- Turn The Ship Around

You might be wondering if there are so many good books about empowerment in general, why would we need to write the book EMPOWERED? The reason is that these books make the argument for empowerment, but none of them even try to show how to set up a product and technology organization that lives these principles.

Q: "Why are you spending so much effort trying to help old companies transform? The entire startup ecosystem we live in (and have benefited from) exists largely because these old companies have no real desire or ability to take care of their customers. If those companies knew how to work and innovate like Amazon, it would be infinitely harder for us to win over their customers."

A: This turned out to be the toughest question. I think there are several reasons:

First, I have friends at many of these companies, and if their company fails, their lives and careers will be impacted.

Second, I admit I am bothered when it's not a fair fight. If the company knows what they need to do, but chooses not to, then that's one thing, but in many cases their leaders are genuinely in the dark.

Finally, and most importantly, I think of the literally hundreds of thousands of product people – engineers, designers, product managers and others – where their talents are at best underutilized, and at worst, wasted. The untapped potential out there is massive. Could they leave and join a better company? Sometimes, but in most cases not easily."""
}

def main():
    """Update articles with batch 1 scraped content"""
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
            if "404" in scraped_content or "Page Not Found" in scraped_content:
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
    
    print(f"\n📊 Batch 1 Results:")
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