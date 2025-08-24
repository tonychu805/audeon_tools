#!/usr/bin/env python3
import json
from comprehensive_scraper import clean_content_for_audio, estimate_read_time

def update_articles():
    # Load articles
    file_path = '/Users/tonychu/Git Repository/audeon_tools/Content/articles/raw_metadata/articles_with_summaries.json'
    with open(file_path, 'r') as f:
        articles = json.load(f)

    # Scraped content for batch of 5 articles
    scraped_batch = {
        14: '''# The Time Value of Shipping

"Shipping as a Feature" gets a framework

Shipping is a Feature is a core principle for product managers. It proposes that you'll never be able to build a perfect product, so you need to learn how and when to ship your imperfect one, because customer use of the product is what really matters.

I've used this principle as a guide in my own endeavours as a PM, but I've always felt it lacked a tangible framework, both for managing and rationalizing the minimum viable product (MVP) to stakeholders.

The Time Value of Shipping is a framework to apply that principle. It borrows from a fundamental concept in Finance called the time value of money, which simply proposes the following:

One dollar today is worth more than one dollar tomorrow.

The reason is because prices rise with inflation over time, meaning your dollar will buy less stuff in the future.

## A quick example

A basketball costs $12 today. If you earned $1 a month you'd have $12 after a year, yet you still wouldn't be able to buy it because of inflation.

If inflation was 5%, that means the basketball would cost $12.60 (+5%) in one year, $13.23 in two, and so on.

You'd have to wait until your paycheque from month 13 to get on the court.

## The product analogy

1. Buying the basketball is when you ship to your customers, usually your MVP
2. The price of the basketball is your users' expectations of the product (at any given point in time)
3. You earn the sum of customer value that your team builds over time

Your job is to build enough value over time to afford the basketball. Graphing this reveals how most organizations view product value and MVP.

The major quality of this graph is that customer expectation is flat and static, implying that what your customer wants when you begin the project is what they want when you ship it. It's not hard to see how people can fall into this line of thinking…

"Through research, we know our users want x and y at minimum, so as soon as we have x and y and nothing more, we will ship."

That sounds perfectly rational, until you dig deeper into the effects of time on customer expectations.

# The Time Value of Shipping

Let's redraw that graph applying the effects of time, which I'll unpack below.

As with the time value of money, the time value of shipping is a simple idea: delivering customer value now is worth more than delivering value later.

If you choose to deliver value later, you need to account for inflation in user expectations, and your eventual product needs to be much better to compensate.

The differences in the trajectories of the customer expectation and value curves are clearly visible. The former grows exponentially over time, and the latter plateaus.

Customer value plateaus because a PM prioritizes the highest impact work, and thus the growth in value over time will naturally degrade.

Customer expectation growth accelerates because the longer a customer has to wait for their problem to be solved, the more time they have to switch to a substitute product. To make them stay, you need to deliver not just what they want now, but what they'll want in the future (when there will be an even greater abundance of choice).

A simple, 140-character-or-less way of thinking about the framework is: The scope of a minimum viable product grows the longer it takes to ship.

## What the graphs reveal

When applying the time value of shipping, MVP is still easily identifiable (in this case is at the tangent of the curves).

But when you start to tweak some of the conditions, the graph suggests some interesting ramifications of the framework.

First, as in the example above, there may only be one point in time (the tangent) where you can ship and satisfy users. As a PM, that's scary.

Second, If your team slips on it's schedule, this happens: The entire value curve has dropped, and it means you'll never be able to deliver enough value to customers to meet their expectations.

At that point, there are two courses of action:
- Abandon the project and move to one where you can meet customer expectations at a point in time, or
- Call on more resources to brute force your value curve back to an intersection point

This "gap of doom" is what underpins most product pivots, as companies realize they cannot innovate at the pace of that particular industry and move to where customer expectations are more attainable. As a PM, that's really scary.

Finally, you shouldn't always ship an MVP (i.e. shouldn't always ship at the first intersection of the curves). Instead, ship at the maximum spread between value and expectation.

This is counter intuitive to the gospel of MVP, but the time value of shipping suggests that sometimes holding off on a launch (even when it meets expectations) is the optimal thing to do.

How can this be, shouldn't you launch at the first intersection and iterate instead?

Well, if you believe in tipping points, holding off a launch is entirely rational. The best products don't just satisfy customer needs, they reap the rewards of virality that come with delighting users. This is accentuated by the network effects that come with launches, which have diminishing returns after the initial marketing push.

As a PM, that is the scariest.

## Just a start, another lens

There are a lot of interesting things I didn't cover (for brevity) - like how competitive forces influence the curves - which I'll save for another post if people find this interesting.

If the goal of the time value of shipping is a practical outcome for PMs, then this is a baby step. Graphing neat little curves in the real world is often a lost cause, with assumption built on assumption.

Instead, it's really about adding another lens to the complex, multi-variate decisions that PMs make everyday. Something in aggregate we call intuition.

So, the next time your planning the roadmap, don't only ask what the customer wants now, think about what they'll want by the time you ship it.''',
        
        15: '''# Deadlines

For as long as I've been working in tech I've heard this oscillating debate about the use of deadlines in projects, with particularly strong opinions from those against them:

"I don't believe in deadlines. They are bullshit created by (predominantly business) people who don't understand how hard it is to design and build great products. You cannot rush great design, software, etc."

I disagree, I believe in deadlines. Not because the date matters, but because they're a powerful way to influence the behaviour of a team.

At the time of this writing, our team at Shopify is busy preparing for Unite, our annual partner & developer conference. It's the final stretch of six months of work that started when we (internally) committed to launch a bunch of products at the conference.

Unite brings together thousands of people from our ecosystem, and on top of building the products themselves, our teams spend hundreds of hours preparing for presentations and workshops. It's very hard to pull off, and a big investment of company energy. The pace is frantic, the months are stressful, and the chaos is draining.

Yet, no one forced us to have it. We happily impose this deadline on ourselves because it makes us better, and in turn, makes our product better.

## Why deadlines work

Deadlines work because they force critical thinking by adding a constraint. When a deadline is set on a project, magical things happen.

1. Teams are forced to work backwards from launch — A deadline forces your team to confront what must exist at launch, and the by-product of that is a realistic list of all the work to be done.
2. Teams must prioritize ruthlessly— Since you have a list of what needs to get done and a fixed time to do it, teams are forced to decide how much time they're willing to allocate to each item.
3. Teams know if they're on pace — open ended projects mean you can never know if you're progressing too slow or fast. A deadline creates a benchmark.
4. Teams combat human nature — People aren't lazy but they don't default to urgency either. Parkinson's law explains this best, "work expands so as to fill the time available for its completion."
5. Teams are compelled to ship faster than they otherwise would have — most teams dream of their product in a perfect end-state, and sometimes that dream can create an inertia to ship. Deadlines combat this by providing an externality to help teams justify shipping an imperfect product.

## How to use Deadlines effectively

There are two types of deadlines: those that matter, and those that don't really matter at all.

The ones that matter tend to relate to either a short-lived opportunity, or a company's survival. The day your startup runs out of cash is a deadline you don't want to miss. You don't even need to think about using these types o deadlines, they will use you.

More interesting (and common), are deadlines that don't actually matter.

Missed an arbitrary launch date by 3 weeks? Stakeholders may moan, but does it really matter? Just delay the blog post, and save that tweet for later. You'll get roughly the same impact.

Even Shopify's Unite conference doesn't really matter. Would Shopify's outcome materially change if a team missed the conference launch date? Unlikely.

Which brings us to the interesting part about using deadlines effectively. The meaning of the date is often irrelevant to it's usefulness. You will get the behavioural benefits by just having a deadline for the sake of it.

## Using deadlines when the date doesn't (really) matter

As a leader of a team, using deadlines when the date is irrelevant is tricky, because in order to get the behavioural effects to work for your team, you have to genuinely care about the date or they will see right through you.

Am I suggesting you fake it? No, and I don't think you need to.

When runners are training, is there some universal force compelling them to care that today's time was better than yesterday's? No, runners aspire to hit the time for the sake of achieving it and for the pleasure in knowing they're growing.

This should be your mentality when you rally your team around a deadline. Make it a point of team pride to achieve it. Make everyone want to meet the deadline, if not for the impact it will have to customers, than for the sake of the challenge and for what it says about them.

## How to avoid using deadlines disastrously

Be wary of deadlines negatively influencing your decision making as you approach the ship-date.

If you don't think it could happen to you, imagine leading a team and beating the "we can do it!" drum everyday for seven months. In that situation, don't kid yourself — you are very emotionally vested in meeting the date. And that's exactly when you will act irrationally.

Here are a few reminders I give myself of as a deadline approaches:

1. Do not ship a shitty product for the sake of the deadline. The dumbest thing you can do with a deadline that had very few consequences if missed, is to create real consequences by shipping a half-baked product that hurts your company.
2. Never punish missed deadlines. If your team is working hard, there's nothing more you should ask of them. Remember, you already got the behavioural benefit by having the deadline at all. If you're a PM, stand up and accept 100% of the blame for missing the date to all stakeholders, publicly. It's the least you can do for a team that's been hauling ass, and it's the right thing to do.
3. Celebrate met deadlines. The deadline may have been artificial, but the focus and drive of the team to hit it was very real. It needs to be acknowledged, celebrated, and observed by other teams.

## No more debate

Deadlines work because constraints foster creativity and resourcefulness. There are countless examples of how deadlines pushed teams to do more than they thought they could. Think moon landing, think Tesla even though they miss every one.

Deadlines work even when dates are arbitrary, because they give a team a challenge and something to prove.

Deadlines work, but they must be used with care and in service of good products, not in priority to them.

Deadlines make product teams better, and that's why I believe in them.

Bonus — how to pick a date when there isn't an obvious one:

1. Register to present the new project at a public event
2. Pick a meaningful date that's relevant to your customer base. For example if you make education software, aim to launch the week students go back to school in September.
3. Schedule a demo to the CEO or board
4. Publicly promise customers a day it will launch (okay don't do this one)'''
    }

    # Update articles with scraped content
    updated_count = 0
    for track_id, content in scraped_batch.items():
        for article in articles:
            if article['track_id'] == track_id:
                cleaned_content = clean_content_for_audio(content)
                article['full_content'] = cleaned_content
                article['read_time'] = estimate_read_time(cleaned_content)
                
                updated_count += 1
                print(f'✅ Updated Track {track_id}: {article["title"]} ({article["read_time"]})')
                break

    print(f'\nTotal updated: {updated_count} articles')

    # Save updated articles
    with open(file_path, 'w') as f:
        json.dump(articles, f, indent=2, ensure_ascii=False)

    print('✅ All updates saved!')
    return updated_count

if __name__ == "__main__":
    update_articles()