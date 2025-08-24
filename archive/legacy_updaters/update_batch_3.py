#!/usr/bin/env python3
import json
import re
from typing import Dict

def extract_main_image_from_content(content: str) -> Dict:
    """Extract main image from scraped content"""
    # Look for ProductTalk images
    producttalk_images = re.findall(r'https://www\.producttalk\.org/[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)', content)
    if producttalk_images:
        return {
            "url": producttalk_images[0][0] if isinstance(producttalk_images[0], tuple) else producttalk_images[0],
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
    # Look for BringTheDonut images
    donut_images = re.findall(r'https://www\.bringthedonuts\.com/[^)"\s\]]+\.(jpg|jpeg|png|webp|gif)', content)
    if donut_images:
        return {
            "url": donut_images[0],
            "caption": "",
            "width": 1200,
            "height": 630
        }
    
    # Look for Melissa Perri images
    melissa_images = re.findall(r'https://[^)"\s\]]*melissaperri[^)"\s\]]*\.(jpg|jpeg|png|webp|gif)', content, re.IGNORECASE)
    if melissa_images:
        return {
            "url": melissa_images[0],
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
        r'Make better product decisions', r'Get the latest from Product Talk',
        r'Join \d+[,\d]* product people', r'Never miss an article', r'Subscribe',
        r'Previous Post:', r'Next Post:', r'Comments', r'Write a Comment',
        r'Executive Coaching for Product Leaders', r'Learn more »',
        r'Get a product-minded executive coach', r'MOST POPULAR',
        r'Comments? \(\d*\)', r'Write a Comment...', r'EmailNameWebsite',
        r'Toggle photo metadata visibility', r'Toggle photo comments visibility',
        r'Loading Comments...', r'Error 404', r'Oops!',
        r'reCAPTCHA', r'Recaptcha requires verification'
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
        if any(word in line.lower() for word in ['subscribe', 'comments', 'previous post', 'next post', 'learn more']):
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

# Scraped contents from batch 3
scraped_contents = {
    "https://melissaperri.com/blog/2016/07/14/prioritization-shouldnt-be-hard": "404 - Page Not Found",
    
    "https://blackboxofpm.com/the-time-value-of-shipping-6308b8f90a6b": "404 - Page Not Found",
    
    "https://blackboxofpm.com/deadlines-d6925e1dce0a": "404 - Page Not Found",
    
    "https://www.producttalk.org/2016/03/introduction-to-product-discovery/": """# Introduction to Product Discovery

I continue to be surprised by how many product managers aren't familiar with dual-track development.

I don't care if you know the buzzwords or if you can define the difference between product discovery and product delivery.

But if you work in product management, you should know that a fundamental shift has been happening in our field for years. And it's time you start exploring that shift.

The Lean Startup came out in 2011. That's five years ago.

Design thinking predates that by many years. As does user research and customer development.

And yet, almost every day I meet product managers who spend little to no time talking to customers. They think experiments belong in science labs. And they still haven't prioritized instrumenting their products.

I understand that many organizations have barriers to adopting these practices. It's not easy for an individual product manager to enact change within their organization.

I get it. I help organizations through this shift every day. It's what I do for a living. And it's hard.

But every single product manager should be aware that this shift is happening in our industry. And regardless of what is happening at your company today, if you want to keep being a product manager tomorrow, you need to be investing in the skills that are required to do modern product discovery.

## Video: An Introduction to Product Discovery

To help build awareness and to move the conversation forward, I've created a 25-minute video that walks through an introduction to modern product discovery.

Even if you get it, even if you talk to customers every day or run a dozen A/B tests a week, I want to encourage you to watch it.

Some companies are starting to kick ass at this. This is the future of product management. Are you ready to keep up?

In this introduction to product discovery, you'll learn:

- What modern product discovery is (in a big-picture sense)
- How most people are deciding what to build—and the limitations of this model
- What some of the best product teams are doing differently—and how you can implement their methodology
- Which artifacts can be used to build a deep understanding of the customer's world that's shared across your team, promotes empathy, and helps everyone retain information
- How to uncover your own underlying assumptions—and how to test them

As product managers, our initial ideas fall short most of the time. It takes work to evolve ideas into something that will work. But if we aren't experimenting and measuring the impact of our product changes, we remain in the dark about our mediocre ideas.

Traditionally, product teams have followed the same methods, working under assumptions that have often led them astray. In this video, I'll outline those assumptions and uncover why they can lead to costly mistakes and wasted resources.

I'll also share how the most forward-thinking product teams are doing things differently. There are two dimensions to modern product discovery, and the video goes into specific examples of each of those dimensions as well as a few techniques to ensure that your team becomes equally proficient in both.

Throughout the video, I draw upon concepts from The Lean Startup, Change by Design, and The Four Steps to the Epiphany as well as what I've observed as a discovery coach and as product manager. I'll reveal some of the common pitfalls that prevent teams from fully adopting modern product discovery and how you can make sure to avoid them. And, of course, I'll share some best practices that I highly recommend following.""",

    "https://www.producttalk.org/2016/08/opportunity-solution-tree/": """# The Opportunity Solution Tree

I've found a visual aid that is profoundly changing the way teams work.

It's working so well that I feel compelled to write a book about it. But that's going to take time and I want you to have it today.

So I'm going to scratch the surface in this blog post.

I suspect you are going to have one of two reactions. You will either skim this post, conclude it's obvious and that you already do it, and miss the point entirely. Or you will be left wanting more.

For those in the first camp, I encourage you to slow down. To look for what's new here and to give it a try. I've been coaching product teams for three years on modern product discovery and this single change has had a bigger impact on how teams work than everything else I do with them combined.

For those of you in the latter camp who will be left wanting more, I'm writing as fast as I can. I hope to have the book ready by early 2017 and I'll be blogging bits and pieces along the way.

Let's get on with it. Please humor me, as this is going to take some setup.

It all started a few months ago…

## The Messy Challenge of Modern Product Discovery

Several teams within a week or two of each other started telling me that while they were learning a lot in our sessions together, they were struggling to see the big picture.

We would jump from reviewing interview guides one week to discussing experiment results the next.

Each piece in its own right was helpful, but the teams weren't learning how to string it together on their own. I always had to tell them what to do next.

My goal as a coach is to get teams doing continuous discovery on their own as quickly as possible. So I knew something had to change.

I kept asking myself, how do I decide what comes next? And more importantly, how do I teach this to teams?

I started by trying to be more explicit about what modern product discovery is. That led to this video.

But that didn't entirely solve the problem.

It's easy for teams to work along both dimensions of product discovery—working to understand their customer's context and iteratively testing their ideas—but that doesn't mean they know how to connect the two sets of activities.

Over time, I started to reframe the two dimensions as discovering opportunities and discovering solutions.

Good product discovery requires discovering opportunities as well as discovering solutions.

This helped as most teams can articulate how to connect the dots between opportunities and solutions. But they didn't necessarily do so in practice.

I still saw teams entertaining solutions that weren't connected to the opportunities they were finding through generative research.

Fortunately, around this time I was reading Peak: Secrets from the New Science of Expertise by Anders Ericsson.

Ericsson has spent his career studying what makes experts stand apart from novices and Peak summarizes his perspective on the research today.

It gave me a lot of food for thought about how we develop expertise in product discovery.

His chapter on the role of mental representations in expert performance is what led to my breakthrough.

## The Power of Mental Representations

Ericsson argues that better mental representations are what set experts apart from novices.

Better mental representations set experts apart from novices.

He defines a mental representation as a "mental structure that corresponds to an object, an idea, a collection of information, or anything else, concrete or abstract, that the brain is thinking about."

That might be a little too vague for those of us who aren't cognitive scientists. He further explains:

"… these representations are preexisting patterns of information—facts, images, rules, relationships, and so on—that are held in long-term memory and that can be used to respond quickly and effectively in certain types of situations."

It's this latter part of his definition that most intrigues me. If we develop better mental representations, we'll be able to respond more quickly and effectively.

Much of Ericsson's work compared novices to grandmaster chess players. In one study, he showed both novices and grandmasters a chessboard that represented a game midway through play.

To the novices the chessboard looked as if the board was set up at random. But to the grandmasters, they were able to understand what moves led to this position and were able to cycle through next moves and their potential outcomes. They were better able to predict which player might win the game.

In fact, as a result of studies like these, Ericsson concluded:

"… that the advantage better players had in predicting future events was related to their ability to envision more possible outcomes and quickly sift through them and come up with the most promising action."

The grandmasters relied on stronger mental representations of chess games to consider more possibilities.

Ericsson further explains:

"… the key benefit of mental representations lies in how they help us deal with information: understanding and interpreting it, holding it in memory, organizing it, analyzing it, and making decisions with it."

But it's not just grandmaster chess players who have this advantage.

"The superior organization of information is a theme that appears over and over again in the study of expert performance."

This raises the question, is there a superior way of organizing information about product discovery that allows us to move quickly and more effectively?

I believe there is.

## The Mental Representations of Expert Product Managers

I started to wonder if I relied on a mental representation to decide what to do next.

If I did, perhaps I could externalize it and use it to guide teams.

My theory was that over time, they would learn to adopt the same mental representation and become self-sufficient.

More importantly, I started to wonder if I could find evidence in the world of a shared mental representation used by many experts.

Perhaps this could be the key to teaching product discovery.

Are expert mental representations the key to teaching product discovery?

This line of inquiry reminded me of Bernie Roth. Bernie is a Professor of Engineering and the Academic Director at the d.school at Stanford University.

I met Bernie at a design event hosted by the Stanford Alumni Association. He led a session that stood out to me.

He asked attendees to identify something that they wanted in their life. He gave a few examples, a house, a better job, more leisure time.

He gave us a minute to write down our answers. Then he asked us another question. He said, "If you had whatever you wrote down today, what would that do for you?"

For example, if you had a house today or a better job today, why would you be better off?

This was a powerful question.

He explained why by extending his example. If you wrote down that you wanted a house, you might have answered the second question with something along the lines of, "If I had a house today, I would feel more grounded in my community."

How else might you feel grounded in your community?

He then used this next answer to ask an even more powerful question.

"How else might you feel more grounded in your community?"

This final question is powerful because it disrupts our fixation on a single solution—owning a house—and helps us to think expansively about other ways we might get the same benefit—feeling grounded in our community.

Bernie teaches a simple structure for expanding your options.

For example, we might become more active in our church community or with a social club. We might volunteer at our children's schools or start attending neighborhood events.

Bernie taught a very simple way to widen your lens, to avoid fixating on a single solution.

Learn a simple way to widen your lens, to avoid fixating on a single solution.

I had never seen reframing taught so simply and so effectively.

But there's more power behind this exercise. Through his teaching, Bernie is revealing his own mental representation for how he solves open-ended problems.

## Product Managers are Problem Solvers

Bernie isn't the only expert to expose this mental representation.

If we widen our own lens from the world of product management to the world of problem solving— remember, product managers are problem solvers—we see this mental representation show up again and again.

If you've been reading Product Talk since the beginning of the year, you might remember David Jonassen's work on problem solving.

Jonassen argues that ill-structured problems are problems that have many solutions. There are no right or wrong answers, only better or worse ones. The solver must start by defining the goal and constraints of the problem before exploring potential solutions.

I argued in this article that the hard problems that product managers face are ill-structured and borrowed from Jonassen's model for solving ill-structured problems.

The short of it is that the problem solver, in our case, the product manager (or even better, the product team), must start by framing the problem.

This is exactly what Bernie is doing with his powerful questions. He helped us uncover the implicit framing of the problem (feeling grounded in our community) behind our desired solution (buying a house).

By making the problem framing explicit, Bernie shows us how we can question it (reframing) and use it to generate alternative solutions (multitracking).

Make your problem framing explicit. So you can both question it and use it to generate more solutions.

Multitracking should sound familiar to long-time readers as well.

Chip and Dan Heath talk about the value of multitracking in their book Decisive—a summary of the research on decision making. I've written twelve blog posts about this book—you can find them here.

But Bernie's exercise is about more than multitracking. He's multitracking in a systematic way.

His first question, "What would you have if you had that?" creates a structure between "I want a house" and "I want to feel grounded in my community."

His second question, "How else can you feel grounded in your community?", expands that structure.

This systematic approach is important. Remember, John Dewey in How We Think, encourages us "to maintain the state of doubt and to carry on a systematic and protracted inquiry—these are the essentials of thinking."

Bernie's simple example is starting to give us a window into how expert problem solvers use framing to support multitracking in a systematic way.

And as Ericsson argued, they are relying on better mental representations to help them do so.

## 4 Common Gaps in Our Thinking Today

Let's start to translate all of this to the world of product management.

### Gap #1: We don't examine our ideas before investing in them.

Bernie asked us, "What do we want in our lives?" As product managers we ask, "What should we build next?"

In both cases, what follows is an idea. Maybe two or three, if we are lucky.

Let's use a product example to illustrate this. Imagine you work at Facebook and you are responsible for newsfeed stories.

You might answer the question, "What should we build next?" with an idea, "Let's add a dislike button."

Some of us rush off and build that first idea or two. That's akin to rushing off and buying a house before examining why we want one.

Gaps in our thinking #1: We don't examine our ideas before investing in them.

### Gap #2: We don't consider enough ideas.

Some of us might slow down and examine our thinking. We might ask, "Why do I think this idea is worth building?"

We often justify our favorite solution by arguing it drives a desired outcome.

We often start with a single idea and work backwards to consider our desired outcome.

Returning to our Facebook example, we might look at our idea and argue, building this idea will increase engagement on newsfeed stories.

In other words, the answer comes in the form of "My idea will drive some desired outcome."

It sounds good.

We don't consider enough ideas.

But we we often skip the step of asking (like Bernie teaches us to), "What else could we do to drive our desired outcome?"

We don't consider enough ideas.

We ignore the advice of Chip and Dan Heath where they advise us to avoid "whether or not" decisions (i.e. should we build this idea or not?) by multitracking. And we ignore the advice of John Dewey by not "maintaining the state of doubt" or carrying out a "systematic and protracted inquiry."

Gaps in our thinking #2: We don't consider enough ideas.

### Gap #3: We don't multitrack in a systematic way.

We don't multitrack in a systematic way.

By jumping straight to solutions, even when we do consider multiple options, we often compare solutions that shouldn't be compared against each other.

Many of us have had the experience where we find ourselves arguing over the merits of two different solutions only to later find that we were each framing the problem differently.

You might argue that highlighting past stories to share is a more compelling solution than adding a dislike button, whereas I prefer adding the dislike button.

We can argue all day, but we won't make any progress if we spend all of our time debating the merits of each solution.

Instead, we want to consider which problem each solution solves and instead make a decision about which problem leads to a more valuable opportunity.

Before debating the merits of different solutions, agree on a common way to frame the problem.

Take the time to discover opportunities before jumping to solutions.

For example, I might argue that adding a dislike button encourages people to engage with existing stories, whereas you might argue that adding a highlight stories to share feature encourages people to share more stories—a different type of engagement.

We can look at how well we engage people around existing content and how well we engage people to share new content and ask ourselves which of these opportunities is more valuable.

This helps us make a strategic decision about where to invest our time, before we debate the merits of our solutions.

We then only want to compare solutions that deliver on the same opportunities. Instead of debating the merits of each solution, we want to ask ourselves, "Of these solutions, which is most likely to deliver on the target opportunity?"

Only compare solutions that deliver on the same opportunity.

When we compare solutions that ladder up to different opportunities, it feels like we are multitracking because we are considering multiple solutions. But we aren't multitracking in a systematic way.

A systematic approach requires that we consider multiple solutions that deliver on the same opportunity.

Gaps in our thinking #3: We don't multitrack in a systematic way.

### Gap #4: Our solutions don't connect to an opportunity or our desired outcome at all.

Watch out for orphaned solutions.

The most egregious gap in our thinking is when we consider a solution that doesn't connect to an opportunity at all. We can't identify a problem that it solves. We just like the idea.

This sounds crazy, but we all do it.

Oftentimes, it's not a result of us just going off the rails. It happens in a step-by-step manner where each step seems reasonable.

I have a silly example that illustrates these types of errors.

Don't compare apples with oranges.

Imagine you are the captain of a ship crossing the Atlantic in the 1500s and your crew comes to you and tells you that several crewmembers have come down with scurvy.

You now have an opportunity to cure scurvy amongst your crew. So you start to generate ideas.

You suggest, "Citrus is supposed to cure scurvy. Let's give them oranges."

A crewmember responds, "Oranges could work. But I prefer grapefruit. Let's give them grapefruit."

To which another crewmember responds, "I don't want to clean up all those peels. Let's give them apples."

And the crew concludes, "Let's give them apples."

We end up with a solution that doesn't deliver on the opportunity, which means we don't deliver on our desired outcome—crossing the Atlantic safely.

Now each objection that took us from oranges to grapefruit to apples was reasonable. They were important constraints that should be considered. But they led to an outcome where we land on a solution that doesn't solve the target problem.

This happens all the time. I see it every week. Taking the time to externalize this visual structure will help you to catch these errors.

Gaps in our thinking #4: Our solutions don't connect to our opportunities or our desired outcome.

## The Opportunity Solution Tree

An opportunity solution tree visualizes what you are learning in discovery and the decisions you are making along the way.

In the previous examples, we are building out what I call an opportunity solution tree.

It's a simple way of visually representing how you plan to reach a desired outcome. It helps you to make your implicit assumptions explicit.

An opportunity solution tree is a simple visual that helps you reach a desired outcome.

We tend to think in solutions. We all do it.

The power of Bernie's questions is that they help us move from a solution (buying a house) to the implicit opportunity (feeling grounded in your community), through to generating new ideas.

This simple structure can be repeated over and over again, to explore how we might reach a desired outcome.

Bernie's questions aren't new. Reframing has been a part of our practice for as long as we've been designing complex solutions.

What is new is the simple visual that helps us externalize our thinking. That externalization helps us to examine our thinking, it allows others to critique our thinking, and it can guide us toward what to do next.

When we visually externalize our thinking, we can examine it and others can critique it.

It's what I've found has been missing in this new world of product discovery.

And it's radically changing the way teams work.

## Building the 4 Sections of Your Opportunity Solution Tree

Before we can start exploring how to use your opportunity solution tree to guide product discovery, we have to cover how to build your tree.

### Section #1: Good product discovery starts with a clear desired outcome.

That might sound easier than it is. I see many teams struggle to define what success looks like.

If your team uses OKRs, you might start with one of your Key Results.

If your team doesn't use OKRs, you can use any single metric that you want to improve—metrics like engagement, retention, revenue, customer satisfaction, NPS, etc.

Some teams focus on more than one goal or metric at a time. I find it easier to create separate trees for each, but technically you could include them both on the same tree.

If you do focus on more than one goal at a time, make it clear which is the priority. If you had to make trade-offs, which would win?

This advice definitely falls into the obvious camp, but it's harder than it looks. Aligning around a clear desired outcome is hard work. Don't skip over it. If you get the start wrong, the rest of the tree will be a waste of time.

Good product discovery starts with a clear desired outcome.

### Section #2: Opportunities should emerge from generative research.

As previously mentioned, most product teams jump from a desired outcome to generating solutions. But we don't want to do that.

We want to be continuously seeking opportunities in our market. Every day we learn more about customers, their needs, and their pain points.

We want to frame these needs as opportunities and capture them on our tree.

To get started you can capture what you think the opportunities are in your problem space. But you'll want to quickly refine these with generative research.

We've talked a lot about how we might each frame the problem, but if we want to build successful products, what matters most is how our customers frame their own problems. Generative research helps us to uncover that.

Opportunities should emerge from generative research.

### Section #3: Solutions can and should come from everywhere (as long as they are bounded by an opportunity).

We've all had the experience where we've had to manage an executive's pet idea. This is why we have the HiPPO acronym (Highest Paid Person's Opinion).

These experiences tend to make us shy to engage others in idea generation.

But there's plenty of research that shows everyone can and should contribute to idea generation.

Fortunately, the tree helps us do that in a structured way. Every solution should connect to an opportunity.

In other words, solutions should only be considered if they help us deliver on one of our target opportunities. If they don't connect to the tree, they should be considered a distraction.

Again, this sounds simple. But it's very challenging in practice.

Solutions can and should come from everywhere (as long as they are bounded by an opportunity).

### Section #4: Experiment to evaluate and evolve your solutions.

Experiments reflect the work that you are doing to test the riskiest assumptions behind your solutions—not your whole solution.

By giving experiments their own row on the tree, it encourages us to think about sets of experiments that will allow us to test a single solution. This helps us escape the trap of over relying on A/B tests to test the whole solution.

Experiment to evaluate and evolve your solutions.

## Using Your Opportunity Solution Tree to Guide Product Discovery

I want to be clear. I just skimmed over how to build your tree. A full answer will require a book. There's a lot to unpack here. But I want to cover enough to help illustrate why this tree helps.

Let's look at a few scenarios.

### Scenario #1: You've got a backlog full of ideas and you are struggling to prioritize them.

Too many ideas with no clear prioritization.

Many teams are here. So first, you aren't alone. However, your odds of driving meaningful product outcomes will be low.

Start by defining your desired outcome. What's the most important metric your team can impact? You want to pick an outcome that will drive the most value for your business right now.

Then start to enumerate the opportunities that might drive that outcome. Remember to stay in the problem space. If you can, do some generative research to frame the opportunities in the same way your customers would.

Finally, try to connect each of your solutions to those opportunities. If you have some solutions that don't connect, look for a missing opportunity or set the solution aside. It's a distraction for now.

And don't forget to use your new view of the problem space (the opportunities you identified) to generate new solutions.

### Scenario #2: You have a clear desired outcome, but are still struggling to prioritize the ideas in your backlog.

You have a desired outcome, but no strategy for how to reach it.

As we make the shift toward autonomous product teams, more of our work is being guided by a clear desired outcome. The recent popularity of OKRs is helping to accelerate this.

But this doesn't always mean we approach our work in a structured way. We still often find ourselves with too many ideas and no way to prioritize them.

You'll notice that the green rows are missing from this tree and this tells me that you need to spend time exploring the problem space. You need to do generative research to understand which opportunities exist.

Strategic decisions about which opportunities to pursue are what helps us prioritize solutions. We want to only consider solutions that deliver on our target opportunities. And within an opportunity, we want to prioritize based on how likely each solution will deliver on that opportunity.

### Scenario #3: You fixate on one opportunity, one solution, and one experiment at a time.

You fixate on a single solution.

One area where the tree can be immensely valuable is to help us see the big picture of how we are approaching our work. Both this and the following scenario are ones in which we aren't balancing the depth and breadth of our tree.

When our tree is too deep (at the cost of breadth) as we see here, we fixate on one opportunity, one solution, and one experiment. This is the opposite of multitracking.

If you find yourself in this situation, take some time to expand your tree horizontally at all levels. Do more generative research to identify more opportunities, engage people in idea generation to generate more solutions, and run several experiments to test the riskiest assumptions associated with your target solutions.

Remember, we want to avoid "whether or not" decisions. That requires that we have multiple options to consider at each decision point.

### Scenario: #4: You consider way too many opportunities, solutions, and experiments at once.

You consider too many options in each section.

However, don't take multitracking too far. It's easy to stay in the problem space for too long, trying to identify every opportunity. Idea generation is fun, but once we have some promising ideas, the return on the investment starts to peter out. We don't want to test every idea we have.

If we don't move vertically down our tree, we'll never ship a viable product. We have to balance horizontal expansion with vertical depth.

Our discovery has to lead to delivery.

Discovery has to lead to delivery.

## A Framework for Continuous Product Discovery

And finally, don't think about this as a linear process.

The goal isn't to first discover opportunities and then discover solutions. Instead, we want to be continuously doing both.

Every week you want to be doing some activities that support discovering and refining new opportunities and every week you want to be doing some activities that support discovering and refining solutions.

And, of course, every week you want to be delivering value to your customer.

Nobody said dual-track was easy. But it does lead to better products. And isn't that what we all want?

## Give It a Try

There is so much more I could write about this opportunity solution tree.

Next week, I'll write more about how to use the structure to communicate your work, to make better decisions, and to better collaborate with your team.

In the meantime, I encourage you to try using it.

Consider the following questions:

- Does your team have a clear desired outcome?
- Are you engaging in generative research to identify compelling opportunities in the market?
- Are you always entertaining new solutions?
- Are you running experiments every week?
- And most importantly, can you connect the dots between all these activities using this structure?

It's harder than it looks. Give it a shot and let me know how it goes.""",

    "https://www.producttalk.org/2021/05/continuous-discovery-habits/": """# Continuous Discovery Habits

I am so excited to announce Continuous Discovery Habits is finally here!

This book is designed to be a product trio's guide to a structured and sustainable approach to continuous discovery.

It's the culmination of my work over the past eight years helping hundreds of product teams adopt successful continuous discovery habits.

Continuous Discovery Habits (the book) is the culmination of my work over the past eight years helping hundreds of product teams adopt successful continuous discovery habits.

And now, I want to help you do the same.

The book will teach you how to start with a clear outcome, interview to discover opportunities, and assumption test to quickly evaluate solutions.

You'll learn how to use an opportunity solution tree to visualize your work, keeping your product trio aligned and your stakeholders engaged.

The book is both evidence-based (explore the footnotes if you like to nerd out on theory) and actionable. You'll get detailed exercises you can put into practice tomorrow.

Here's what people are saying about it:

"If you haven't had the good fortune to be coached by a strong leader or product coach, this book can help fill that gap and set you on the path to success." – Marty Cagan, Partner, Silicon Valley Product Group

"Teresa Torres shows how to truly—and continuously—include customers. This is a must-read for every CEO and product team out there." – Phil Terry, Founder, Collaborative Gain

"Teresa's work in product discovery is a constant and critical reminder that job number one for a product team is to understand who you are building for and what value you can create for them. Her methods inspire rigor similar to a workout coach—product discovery is a regular, consistent practice, that's measurable and impactful." – Jocelyn Mangan, CEO, HimForHer

"It's no secret that regularly engaging with customers helps you discover better opportunities to serve them—yet we all struggle to do it well. This book is an indispensable guide to making this critical activity a continuous habit." – Martin Eriksson, Co-Founder & Chairman, Mind the Product

It's available on Amazon ( Paperback & Kindle) around the world today and should start to show up in other bookstores over the next week or two.

In the coming months, I'll also be releasing an Audible version. There's no timeline on this yet, as I'm still researching my options. But if you prefer to listen to your books, know this is planned.

For those of you who want to place bulk orders (20+copies), you can do so here. For smaller order sizes, please buy on Amazon.

And if you are interested in having me come speak at your company or do an Ask Me Anything related to the book, you can learn more about those options here.

## This Book is Just the Beginning

In January, I shared that my outcome at Product Talk is to increase the number of product trios who adopt a continuous discovery cadence. This book is a big part of driving that outcome.

My outcome at Product Talk for 2021 is to increase the number of product trios who adopt a continuous discovery cadence. The Continuous Discovery Habits book is a big part of driving that outcome.

However, I know that a book is not enough.

Too many people read books and struggle to put the ideas into practice. It's often hard to connect the dots between the ideal way of working and what we see day to day in our own organizations.

Most product trios work in organizations that are either still obsessed with outputs or are just starting on their outcome journey.

Many product teams still lack durability over time—meaning teams get formed and reformed with every project, instead of having the luxury of working on the same product over time.

I still meet product managers every day who have never talked to a customer—or worse, aren't allowed to talk to customers.

We have a long way to go.

The book does include a chapter that will help you start to bridge the gap between how your company works today and the approach that is described in the book. But I know from experience many of you will need more support as you work to develop and hone your continuous discovery habits.

As a result, I'm excited to announce the Continuous Discovery Habits Membership Program.

We learn best in community. And this program is designed to help you connect with and learn from like-minded peers as you work to put the Continuous Discovery Habits content into practice.

This membership program includes:

- Biweekly membership calls where we'll tackle your most pressing discovery questions. These calls are hosted by me and are informal conversations about whatever is top of mind for participants.
- Monthly Fireside Chats and Ask Me Anythings with real product trios who are putting the continuous discovery habits into practice. These sessions will be recorded and made available to all current members.
- A virtual book club where we read and discuss books that help us become better continuous discovery practitioners.
- Access to our Worthy Reads library (over 300 of the best product resources from around the web) and a dedicated Slack channel to discuss daily finds.
- An exclusive Continuous Discovery Habits job listings channel where you can recruit like-minded peers and/or find your next gig.
- Focused challenges that will help you put the continuous discovery habits into practice (e.g. the 12-day challenge to automate your interview recruiting process).
- Exclusive Annual Subscriber Benefit: 15% discount on each of our Deep Dive courses.

We offer monthly and annual membership subscriptions. You should join us. You can do so here.

I'm excited to hear what you think of the book and I'm even more excited to help you put it into practice through our new membership program.

Happy reading!""",

    "https://www.bringthedonuts.com/essays/how-to-listen-to-customers.html": """# How to Listen to Customers

## How do you hone in on what users really need?

Quite by serendipity I've come across a few articles in the past week about listening to - and ignoring - users in the product development process. Here's a classic example from 2001 announcing the launch of the iPod - "No wireless. Less space than a nomad. Lame." There's some early market feedback worth ignoring.

At Yahoo!, I was constantly frustrated by the Slashdot crowd's seemingly innate ability to hate your product for not being Linux or Google. Spending too much time in the Slashdot echo chamber not only gives you a headache, it can screw up your priorities.

The other article comes from the Creating Passionate Users blog and is entitled Listening to users considered harmful? The CPU writers can be a bit treacly for my tastes, so read it with a grain of salt. But they're correct in stating that users will often ask for one thing and want a different thing entirely.

It's not that users are lying (usually), it's just that they don't know what they want when they don't know what's possible. Very few consumers in the early nineties asked for a handheld organizer that forced the user to learn a special alphabet, yet the Palm Pilot was a runaway success. And as the Slashdot example shows, very few hipsters in 2001 thought that an undersized, overpriced MP3 player was worth a second glance.

So how do you hone in on what users really need? You talk to people who represent a heterogeneous cross-section of your target population, consider their built-in biases and perspectives and triangulate from there. In my experience, I've found it helpful to talk to users who represent the leading, middle and trailing adoption populations in my market as well as influential observers.

Here's what to consider with each.

#### Influential Observers

Call them "influencers," "hipsters," or "mavens". These are the super-early adopters who have a deep perspective on your market and your product. They're often not target customers, but they have rich insights into how your product will be received.

Where they're good: keeping you from stepping in your own manure. Influencers have an intuitive handle on what other hipsters get excited about, and what they hate. They talk to lots of people, read a lot and try a lot of things. The most important asset they offer is preventing you from committing a serious faux pas that could kill your product. Like launching a web site in 2005 that only works in Internet Explorer. Or releasing a company blog that doesn't have comments enabled. They can also give you an early warning of competitive products or companies that might be relevant. And unlike most customers, they're usually brutally honest.

Watch out for: influencers like to run with the crowd so you need to know how to balance the feverish, often polarizing reception you'll get ("it rules!" or "it sucks!"). Learn how to filter "cool" from "useful," especially when it comes to technology and user interface. Beware of the influencer's boasted ability to channel the "average user". Don't believe it. Nobody who lives in Mountain View and spends their free time blogging about Ajax knows a whit about average users. None of us do.

#### Leading Adopters

You usually know who your leading adopters are. In many cases, they were the first customers you found. They're usually genuinely excited about your product and your company and eager to help make the product better. Listening carefully to your early adopters can serve as an early warning system for what the majority of users will want in the future. To paraphrase Wayne Gretzky - they help you skate to where the puck will be.

Where they're good: the problems they're having are problems everyone will have. When a power user describes a problem they're encountering in your product, you can bet a lot of other users will come across it at some point. Leading adopters also understand your product deeply, and can describe what they want in richer detail, using the terminology you're familiar with and the capabilities of your product as background.

Watch out for: early adopters are usually very excited about your product and very eager to help you succeed. That's great for your ego, but it can be very bad for your product development process. Many companies have been lured to their doom by a very small, well-meaning and vocal group of power users who fooled the company into thinking they were gaining real traction. Also, power users rarely describe a problem, they usually ask for a specific solution. Since they understand the product so well, they prefer to speak in features, which can mask the underlying problem. For example, an advanced IT user might ask for a preference setting that allows them to hide a feature in your product from their users. That might be an easy feature to ship, and you'd be tempted to do it. But if you dug deeper, you might learn that their asking for this because there's a serious usability problem with the feature in question, and hiding it is the best way they can think of to avoid being pestered by confused co-workers. In this case, you'd be better off fixing the underlying problem than delivering the feature your early adopter asked for.

#### Middle Adopters

You might be tempted to call these folks "average users" but there's no such thing. The majority of your users probably fall into this category, but be careful to lump them into a pile - they're far too diverse. The fact is, these folks are your most valuable asset from a product development perspective. They're also the ones paying the bills.

Where they're good: your product has been designed for them, so they're the best equipped to shape your roadmap. You get the most out of them when you get them talking about pain - what is painful about what they're doing today and what would help eliminate the pain? A patient rarely knows what prescription they need, but they usually know what hurts. Middle adopters need interactive dialog. They won't just start talking unaided like the influencers or the early adopters, so you need to bring them out with lots of open questions and "what ifs".

Watch out for: these users are often reluctant to say anything negative. You need to give them permission to be brutally honest. In my experience, they'll usually apologize to you for problems they're having with your product - "I am kind of dim" or "I must not have read the documentation closely enough". Rule - when a middle adopter user starts apologizing, it's your fault. Since these customers aren't as comfortable or familiar with technology, getting to the real problem can sometimes feel like an archaeological dig. But keep at it.

#### Late Adopters

Unless you have huge market share in a mature market, these people probably aren't your customers. You'll want to talk to them to get a sense of what's preventing people from using your product. Are they fearful or just skeptical? Late adopters are the sanity filter for your customer research.

Where they're good: they can help you appreciate the power of status quo. As product developers, we are great at convincing ourselves of the royal ineptitude of the incumbent solution and the absolute withering pain under which our soon-to-be-freed subjects stand to be liberated. Nothing like a conversation with a late adopter to throw cold water on that. Working in the wiki space, I'm sometimes startled to hear these people say things like - "you know, emailing around a bunch of Word documents doesn't bother me that much". But poke a bit and you'll gain an understanding of what they really care about - "I like emailing documents because I can control who sees them". (Ahh, control and security!).

Watch out for: be careful when they tell you what they want. They know what they like about what they have today, but they're not as good at articulating what they'll need tomorrow. And don't sweat yourself to death. Ultimately late adopters move when somebody else tells them to, or when something appears to be a foregone conclusion. The only way to influence them is to win the majority.

As you can imagine, many product developers make the mistake of only talking to leading adopters, or worse yet, influencers. Why? It's more fun. They love your product, they're passionate about it and they know how to talk to you in a language you understand. Plus, we product developers are usually early adopters ourselves, so they're kin. Don't fall into that trap. The only way to get a complete picture of what it will take to make your product successful is to talk to a wide cross-section of users, and triangulate from there.""",

    "https://melissaperri.com/blog/2016/05/05/finding-the-truth-behind-mvps": """# Finding the Truth Behind MVPs

## A Successful Start

I learned about Minimum Viable Products like 99% of other Product Managers - through The Lean Startup by Eric Ries. When I happened upon the book and Eric's method, I thought, "YES! This is what I've been searching for. This makes so much sense." Testing products before you build them? What a novel idea! I was excited. I was energized! I was now going to build things that mattered to my customers.

Frankly, this came at the perfect time for me. I was tired of building products that no one used. Watching and waiting for the numbers to go up in Google Analytics, only to be let down again. It was getting old. My team and I spent months building products we thought would be successful, only to be disappointed. When I had the chance to try the MVP approach on a new product, I jumped on it.

The CEO of our ecommerce company approached me with a new product idea that was going to increase engagement and sell more items. He wanted to implement a Twitter-like feed so that the celebrities, who sold products on our site, could also post about their lives. This idea was prime for testing. It was so ripe with assumptions: "Do our customers want to hear about what are celebrities are up to directly in our platform? Will this sell more items or increase retention?"

I went to the engineers and asked them how long it would take to fully implement this idea from scratch, the way our CEO was proposing. With rough estimates, I went back to our fearless leader and told him "This is going to cost us $75,000 to fully build, and we're not even sure our customers want it. I can prove in a week with $2,000 if this is going to move the needle." Just like that, I had buy in.

Within one week, we proved this was a terrible idea. A week after that we found a different solution that increased clickthrough rate threefold on our products. We also doubled conversion rate. The whole company was hooked, and we were allowed to keep experimenting. "Great," I thought, "everyone can see the value of this! It's a no brainer."

Eventually, I moved on to another job. I was excited about bringing the concept of MVPs to this team as well. Honestly, I was kind of shocked that everyone in that company wasn't using them already. Did they just not know about this wonderful witchcraft? I was so confident that everything would go exactly as it had in my previous company.

## "We Don't Do That Here"

When the words "Minimum Viable Product" left my mouth for the first time, the reaction in the room was quite different than I expected. You would have thought I recited every curse word in the English dictionary. Like I just busted out a Biggie Smalls song in the middle of the meeting, not bleeping out any of the colorful lines. They responded as if I had offended their ancestors. Finally the CMO broke the silence with, "We don't do that here. We don't ship terrible products."

Over the next few years I experienced this same reaction countless times.

I've learned that Minimum Viable Products are widely misunderstood. Some people are afraid to try building MVPs because of preconceived notions. Others use the word so much that it's lost all meaning. "We should MVP that!" has become a battle cry in product development that just means make it minimal, make it cheap, and make it fast.

How do people end up here? The story is almost always the same. Someone picked up The Lean Startup, had their mind blown, and said "We should do that here!" They saw a quick and cheap way to execute on a product without fully understanding what the purpose of an MVP was or how to make one well. In my particularly jaded company, a developer ended up creating a hack to test a new feature that broke every time someone went to use it. Customers were pissed. The company blamed it on MVPs as a whole, rather than sloppy development.

It's not the MVP's fault. The problems stem from misinterpretation of what an MVP is and from miscommunications along the way.

## What is an MVP?

My definition of a Minimum Viable Product is the smallest amount of effort you can do to learn. When I teach this in workshops, I'm usually met with disagreement. "MVPs are the smallest feature set you can build and sell! Not just an experiment."

So what is the truth? Is an MVP a product, a subset of a product, or just an experiment?

The Minimum Viable Product was first coined by Steve Blank and then made popular by Eric Ries in The Lean Startup. I went back to research how these two experts, and a few others, defined the term.

"The minimum viable product is that product which has just those features and no more that allows you to ship a product that early adopters see and, at least some of whom resonate with, pay you money for, and start to give you feedback on." - Eric Ries, 2009

"Minimum feature set ("minimum viable product") is a Customer Development tactic to reduce engineering waste and to get product in the hands of Earlyvangelists soonest." - Steve Blank, 2010

"A minimum viable product (MVP) is not always a smaller/cheaper version of your final product." - Steve Blank, 2013

"An MVP is not just a product with half of the features chopped out, or a way to get the product out the door a little earlier. In fact, the MVP doesn't have to be a product at all. And it's not something you build only once, and then consider the job done." - Yevgeniy Brikman, Y Combinator, 2016

Confusing, yes? The one thing that was clear to me through this research is that the definition of an MVP has evolved. In the beginning, we talked about this concept as something to validate startup ideas. All these products were searching for product-market fit. I learned about the Concierge Experiment and Wizard of Oz in those days, which helped shape my definition and understanding. As I continued to use these methods as a Product Manager in enterprises and other more mature companies, I had to customize both my definition and the practice of building Minimum Viable Products. What I've learned is that you need both - the concept of experimenting and building a minimum feature set to be successful.

While there's tons of dissent on the definition of an MVP, everyone pretty much agrees on the goal. The goal of an Minimum Viable Product is to rapidly learn what your customers want. You want to do this as quickly as possible so you can focus on building the right thing. So let's get rid of the buzzword and focus on that premise. Let's stop arguing about what an MVP is and start talking about what we need to learn as a company.

## How and When to Learn

When we start off building a new feature or product, there are a million questions to answer. "Is this solving the customer's problem? Does this problem really exist? What does the user expect to gain with the end result?" We have to find the answers to these questions before committing ourselves to building a solution.

This is why starting with a minimum feature set is dangerous. When you jump into building a version one of a new product or feature you forget to learn. Experimenting helps you discover your customer's problems and the appropriate solutions for them by answering these questions. It also doesn't end with just one experiment. You should have multiple follow-ups that keep answering questions. The more you answer before committing yourself to the final solution, the less uncertainty there is around whether users will want or use it.

Once you have proven that a user wants your product, it's time to investigate a minimum feature set. Now we can start to find a product that is marketable and sellable, but also addresses the user's needs that were uncovered through experimentation. Delivering this product to market as fast as possible is the ultimate goal, so you can get feedback from customers and iterate. But, you have to be careful to deliver a quality product, even if it's tiny. Broken products do not produce value for your customers, only headaches. Any version of a product that does not deliver value is useless.

How does this look in practice? In one SAAS company I was working at, we had to create a new feature that would help our customers forecast their goals. We were given input by the customer's sales team from their conversation with the customer. After reviewing the information, we knew we had to learn more.

We met with the customer to understand what they were looking for in this forecaster. Once we thought we had a good grasp of the needs, we built them a spreadsheet and dumped their current data into it. This took us less than a week. We presented the spreadsheet to the customer and let them use it for a week before getting their feedback. We didn't get it right the first time, or the second, or the third. But, on the fourth iteration, we were able to deliver exactly the results the customer was looking for. We did the same process with a few other customers to make sure this scaled.

While the spreadsheet was providing immediate value to some of our customers, we didn't have the resources to do it for all of them. So, we had to build a software solution. We started exploring the Minimum Feature Set, using the feedback we received on the spreadsheet. There were plenty of other bells and whistles the customers wanted, but we paired it back to the essentials in the first version. We spent a few weeks getting the first version to work and include the most important pieces. Then we turned it on for the clients with the spreadsheet to get their feedback. After iterating a few times, we began selling it to others.

This process is will help your company find problem-solution fit. If you are creating a new feature or a new business line that solves a different problem for your user, this method can help ensure you're building the right thing for your customer. But what if you have a mature product and are not starting from scratch?

## Experimenting in Enterprises

Many enterprises today are introduced to the Minimum Viable Product by consultancies who propose creating an entirely new product from scratch. This is may not be the best idea. When your company already has product-market fit, you have already built a product that customers are using. You do not need to rebuild your product, you need to improve it. The methods should to be adapted for this case.

Something that sets these two methods apart is the goal. When searching for product-market fit, you want the user to adopt and probably pay for your product. This is not always the goal when improving existing products. It could be to improve retention or increase engagement with certain parts of your product. Whatever you decide your goal is, it should be clear to the team and informing all their decisions.

Once the goal is clear, you again focus on learning. What do you need to learn before committing to a solution. Write out these hypotheses on what you think will move the needle, and then design a Product Experiment to test it. You don't have to create an entirely new product. Maybe you will find out a new product is necessary while experimenting, but that should not be the end goal.

A company I coached wanted to increase their conversion rate across the site. They already had a popular ecommerce subscription product with thousands of users. Traffic was coming in, but users were not converting as much as projected. Nothing had moved the needle when it came to offer testing. They dug into the sources of where great customers were coming from and found that many came through referrals. But, only a few people were actually sending referrals. Through user research we discovered two main reasons why: they didn't know they could actually send referrals, and they were not sure what the referral gave their friends.

The team decided to tackle the first problem with the hypothesis, "If we let users know clearly that they had referrals available, they would send them." The first experiment involved showing a pop up that encouraged users to send referrals when they next logged in to the site. Referrals sends went up 30%, leading to an increase in conversion rate! They did not have to implement a whole new program here; they just had to create ways to make it visible.

This team continued to dive into problems around conversion. They learned that the top three problems on the direct-to-site experience were:

1. Customers were not sure how the service worked.
2. Customers wanted to know what specific items came in the subscription.
3. Customers were not sure why the product was priced higher than competitors.

The next step to solving this problem was to see if they could deliver value and learn at the same time. They created the hypothesis, "If we give users the information they are searching for in the sign-up flow, they will convert more." They also wanted to learn which questions people would click on most to see which problem was the strongest. They planned a simple way to get people the information they needed while signing up: adding a few links into the sign-up flow, echoing the questions back to users. When the links were clicked, it showed a pop up explaining the answer to the question. At the end of the week of building and testing, they could see the experiment increased conversion rate closer to our original goal. They also learned that showing the information about what exactly came in the subscription was the most important thing. The team continued to learn what was preventing prospects from signing up, and systematically answered those questions through experimentation.

## Caution Ahead

One mistake companies make when dealing with Product Experiments is keeping them in play once you have learned. These features then break and cause problems for your users. You are designing to learn and move on, not to implement something that will last forever.

With the team above, they learned that the information they provided was helping prospects answer their questions, but not enough people were seeing that solution. After experimenting more, they learned that a more robust solution would be needed.

It was time to start planning a sustainable solution that incorporated the learning from the experiments. Moving away from Product Experiments to the next phase is not an excuse to stop measuring. This team was still releasing components in small batches, but those batches were complete with beautiful design and a more holistic vision. After every release, which happened biweekly, they would measure the effect it had on conversion and test it in front of customers. The feedback would help them iterate towards the product that would reach the conversion rate goal.

Chris Matts has eloquently named this the Minimum Viable Investment. He's also pointed out that you should not only be looking at improving your user facing products, but the infrastructure that helps you create those products quickly. The team above is also improving their site architecture to experiment faster while waiting for test results. I introduced the Product Kata to teams improving their products to help them find structure through Product Experiments and Minimum Viable Investments.

## Learning is the Goal

One of the scariest parts of this process for companies is releasing things that are not perfect. It's important to balance good design with fast design and good development with fast development. The best way to do this is getting UI designers and developers to pair together. After defining what the goal is for the iteration or experiment, sit down together and talk through ideas on how to execute. If we design in a slightly different way, is it just as useful to the user, but easier to build? Prototype together. Sketch together. Work side by side and talk about trade offs the whole time. This is how good teams move quickly and avoid rework.

By learning what the user wanted early, I've avoided countless hours of rework and throwing out features all together. This is why it's so important for teams to experiment, whether they are B2B or B2C. Give the product teams access to users. I've seen fear in companies that their employees will say or do things that will upset users. If you teach your product teams the right way to communicate and experiment, this will not happen. Train the teams in user research. Don't release experiments to everyone. Create a Feedback Group with a subset of users. Build infrastructure so you can turn on experiments and features just for smaller group. These users will guide you to create features that will fit their needs.

I dream of a day when I can walk into a company and mention "MVP" and not hear, "We don't do that here." While the definition of Minimum Viable Product may work us into a tizzy, the goal behind it is extremely valuable for product companies. If you're having trouble implementing these practices inside a company, try leaving out the buzzwords. Use terms like experimenting and focus on the premise. Learning what your users want before you build it is good product development. Make sure when you do invest in a feature or solution, it's the right one.""",

    "https://25iq.com/2017/02/18/twelve-things-about-product-market-fit/": "Error 404 - Page Not Found"
}

def main():
    """Update articles with batch 3 scraped content"""
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
            if ("404" in scraped_content or "Page Not Found" in scraped_content or 
                "Error 404" in scraped_content or "Oops!" in scraped_content):
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
    
    print(f"\n📊 Batch 3 Results:")
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