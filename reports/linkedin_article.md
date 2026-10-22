# Is Wigan really unsafe? I went looking for the numbers

*Suggested cover image: Chart 1 (trend over time)*

---

I've lost count of the times I've heard someone in Wigan say they don't feel safe walking through the town centre at certain times of day. Usually it's said in passing: a friend avoiding a particular street after dark, a parent who'd rather pick their teenager up than let them walk, someone at a bus stop shaking their head at the latest headline.

And the headlines keep coming. Scroll through local news or a community Facebook group and it's easy to come away thinking crime in Wigan is out of control.

So I wanted to know: **is that fear an exaggeration, or is it real?**

I'm a data analyst, so I did what I always do. I went to the data.

## The first surprise: the data wasn't there

The obvious place to look up crime in your area is police.uk. You type in a postcode and it shows crimes on a map.

I asked it for every crime in the Wigan borough, and it came back with about **10 a month**.

Wigan records thousands of crimes a month, so something was badly wrong. The handful that did come back were mostly railway crimes recorded by British Transport Police.

It turns out **Greater Manchester Police hasn't sent data to police.uk since July 2019.** GMP confirmed this in a Freedom of Information response this year, and said it has no timeline for restarting. So if you live anywhere in Greater Manchester and try to check crime on your street, you'll find almost nothing, and you could easily conclude crime is very low.

It isn't. The data just isn't public in the place most people would look.

## Finding a source that works

GMP does still report its crime figures to the Home Office, which publishes them for every council area in England and Wales, every quarter. You lose street-level detail, but you get a complete, official count for the whole borough, in the same format as everywhere else, so you can make fair comparisons.

Then I found a second problem. From late 2025, more and more GMP crimes stopped being linked to a borough at all. By spring 2026, **84% of crimes had no borough recorded.** Crime hadn't fallen; it just wasn't being assigned. The official notes don't mention it for Greater Manchester. So I worked with the last clean year, 2024/25, and estimated the rest.

*[Chart 6: the share of crimes with no borough recorded]*

## So, is Wigan's crime high?

The first answer looked like a yes. In 2024/25, Wigan recorded **91.9 crimes per 1,000 residents**, about **9% above the England and Wales average**.

But I didn't want to stop at the first number, because a raw comparison can mislead. So I kept asking "compared to what?"

**Compared with the rest of Greater Manchester**, Wigan has the **3rd lowest crime rate of the 10 boroughs**: 13% below the Greater Manchester average, and 9% below Bolton.

*[Chart 2: Greater Manchester ranking]*

**Compared with places like Wigan:** areas with more people on low incomes tend to have more recorded crime, and Wigan is in the more deprived third of England. So I compared Wigan only with England's 36 metropolitan boroughs, the large urban areas like Sefton, St Helens, Barnsley and Leeds, and allowed for deprivation. Wigan came out **only about 5% above what you'd expect, ranking 12th of 36**. Its crime rate is actually *below* the typical metropolitan borough.

*[Chart 4: crime vs deprivation, metropolitan boroughs]*

The biggest differences I found weren't between towns at all. They were between **police forces**. Boroughs in West Yorkshire sit well above the line; boroughs in Merseyside sit well below. Neighbouring places in different forces differ more than places within the same force. That suggests part of what we call "crime levels" is really about how thoroughly each force records crime.

## So is the fear exaggerated?

Honestly, it's more nuanced than either answer.

**Why the fear isn't baseless:** the crimes Wigan has *more* of than the national average are exactly the ones that make a street feel unsafe:
- violence against the person: **26% higher**
- public order offences: **48% higher**
- criminal damage: **24% higher**

Meanwhile, theft (**28% lower**) and robbery (**31% lower**) are well *below* average.

*[Chart 3: types of crime vs the national average]*

**Why the headlines may overstate it:**
- Wigan is close to typical for a large urban borough, and well below most of Greater Manchester.
- Its crime rate has **fallen 18% since 2021/22**, faster than the national average (4%).
- Part of the earlier rise wasn't more crime at all. In 2020, inspectors found GMP was failing to record about **1 in 5 crimes**. As recording improved, recorded crime went up.

**What I can't tell you:** whether Wigan town centre is unsafe at 11pm on a Friday. That's the specific question people are really asking, and **the public data can't answer it**, because street-level data for Greater Manchester hasn't been published since 2019. That gap matters. People are left to fill it with headlines and word of mouth.

## Can we predict what happens next?

I also built a forecasting model, and I tested it before trusting it. I trained it only on data up to March 2025, then asked it to predict 2025/26, a year it had never seen. It came within **3.4%** of the real total, closer than the published borough figures themselves.

*[Chart 5a: forecast vs reality]*

For Wigan, it expects crime to **ease slowly**: around **90.6 per 1,000 in 2026/27**. I've saved that forecast with today's date. When the next official figures come out in January 2027, I'll check it publicly, right or wrong.

## What I learnt

1. **Public data isn't always accessible data.** I found the same thing when I built a free food hygiene ratings tool for Wigan. Here, residents of one of England's largest police areas can't see street-level crime at all.
2. **"High" always needs "compared to what?"** The same borough can look above average, below average or typical depending on the comparison. Each fairer comparison told me something new.
3. **Feelings and statistics measure different things.** Feeling unsafe isn't irrational just because the borough average looks typical. Averages hide places and times, and the data that would show them isn't published.

The full report (methods, every table and every limitation) and all the code to reproduce it are free on GitHub. Anyone can rerun the analysis and check my working:

🔗 **[link to GitHub repo]**

I'd love to hear from you:
- If you live in Wigan, do these numbers match how it feels to you?
- If you work with police or council data, do you know why borough coding stopped in late 2025?

#Wigan #GreaterManchester #OpenData #DataAnalysis #DataForGood #CrimeData #Forecasting #Python
