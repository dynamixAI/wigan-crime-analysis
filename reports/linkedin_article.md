# Is Wigan really unsafe? I went looking for the numbers

*Suggested cover image: Chart 1 (trend over time)*

---

I've lost count of the times I've heard someone in Wigan say they don't feel safe walking through the town centre at certain times of day. Usually it's said in passing: a friend avoiding a particular street after dark, a parent who'd rather pick their teenager up than let them walk home.

The local news doesn't ease those worries. A Wigan Today columnist put it bluntly in 2023: *"Wigan is a crime hotspot. It's unsafe."* [1] The same month, councillors raised concerns that daytime drinking and anti-social behaviour around the bus station were putting families off visiting the town centre [2].

Since then, the headlines have kept coming. In September 2025, two people were stabbed at Wigan bus station, and police brought in a dispersal order, pointing to a recent rise in youth anti-social behaviour [3]. In May 2026, four people were arrested after a disturbance on Market Street in which a man was injured, apparently by a knife [4]. Police now list violent crime, anti-social behaviour and the town centre's night-time economy among their 2026 priorities for central Wigan [5], and the council is consulting on renewing its town centre safety orders [6].

So I wanted to know: **is that fear an exaggeration, or is it real?**

I'm a data analyst, so I did what I always do. I went to the data.

## The first surprise: the data wasn't there

The obvious place to look up crime in your area is police.uk. You type in a postcode and it shows crimes on a map.

I asked it for every crime in the Wigan borough, and it came back with about **10 a month**.

Wigan records thousands of crimes a month, so something was badly wrong. The handful that did come back were mostly railway crimes recorded by British Transport Police.

It turns out **Greater Manchester Police hasn't sent data to police.uk since July 2019.** GMP confirmed this in a Freedom of Information response this year, and said it has no timeline for restarting [7]. So if you live anywhere in Greater Manchester and try to check crime on your street, you'll find almost nothing, and you could easily conclude crime is very low.

It isn't. The data just isn't public in the place most people would look.

## Finding a source that works

GMP does still report its crime figures to the Home Office, which publishes them for every council area in England and Wales, every quarter [8]. You lose street-level detail, but you get a complete, official count for the whole borough, in the same format as everywhere else, so you can make fair comparisons.

Then I found a second problem. From late 2025, more and more GMP crimes stopped being linked to a borough at all. By spring 2026, **84% of crimes had no borough recorded.** Crime hadn't fallen; it just wasn't being assigned. The official notes don't mention it for Greater Manchester. So I worked with the last clean year, 2024/25, and estimated the rest.

*[Chart 6: the share of crimes with no borough recorded]*

## The headline that explains the gap

In May 2026, Wigan Today reported that crime in Wigan had risen, and that the borough recorded the second-highest number of crimes in Greater Manchester, behind only Manchester [9].

That's accurate, and it sounds alarming. But it's a **count**. Wigan is also Greater Manchester's **second-largest borough** by population, with around 347,000 residents. More people means more crimes, even if each person is no more likely to be a victim.

That's why my analysis uses **crimes per 1,000 residents**. Measured that way, Wigan isn't second highest. It has the **3rd lowest** crime rate of Greater Manchester's 10 boroughs.

*[Chart 2: Greater Manchester ranking]*

This, I think, is a big part of why fear and data so often disagree. Both are reporting real things, but they're answering different questions.

## So, is Wigan's crime high?

In 2024/25, Wigan recorded **91.9 crimes per 1,000 residents**, about **9% above the England and Wales average**.

But I didn't want to stop at the first number, so I kept asking "compared to what?"

**Compared with the rest of Greater Manchester**, Wigan is 13% below the Greater Manchester average, and 9% below Bolton.

**Compared with places like Wigan:** areas with more people on low incomes tend to have more recorded crime, and Wigan is in the more deprived third of England. So I compared Wigan only with England's 36 metropolitan boroughs, the large urban areas like Sefton, St Helens, Barnsley and Leeds, and allowed for deprivation. Wigan came out **only about 5% above what you'd expect, ranking 12th of 36**. Its crime rate is actually *below* the typical metropolitan borough.

*[Chart 4: crime vs deprivation, metropolitan boroughs]*

The biggest differences I found weren't between towns at all. They were between **police forces**. Boroughs in West Yorkshire sit well above the line; boroughs in Merseyside sit well below. Neighbouring places in different forces differ more than places within the same force. That suggests part of what we call "crime levels" is really about how thoroughly each force records crime.

## So is the fear exaggerated?

Honestly, it's more nuanced than either answer.

**Why the fear isn't baseless:** the crimes Wigan has *more* of than the national average are exactly the ones that make a street feel unsafe:
- violence against the person: **26% higher**
- public order offences: **48% higher**
- criminal damage: **24% higher**

The incidents in the news [3][4] are real, and they're the kind that shape how a place feels far more than any average does.

*[Chart 3: types of crime vs the national average]*

**Why the headlines may overstate it:**
- Wigan is close to typical for a large urban borough, and well below most of Greater Manchester.
- Its crime rate has **fallen 18% since 2021/22**, faster than the national average (4%). That matches what police reported in February 2026: residential burglary down 24% and personal robbery down 21% across Wigan and Leigh [10], with the local inspector saying officers were *"responding faster, solving more crimes"* [10]. Wigan Today reported a 5% fall in recorded crime over the same period [11].
- Part of the earlier rise wasn't more crime at all. In 2020, inspectors found GMP was failing to record about **1 in 5 crimes** [12]. As recording improved, recorded crime went up.
- After the May 2026 Market Street incident, police described it as *"an isolated incident"* [4]. Serious incidents get headlines; the steady, much more common reality usually doesn't.

**What I can't tell you:** whether Wigan town centre is unsafe at 11pm on a Friday. That's the specific question people are really asking, and **the public data can't answer it**, because street-level data for Greater Manchester hasn't been published since 2019 [7]. That gap matters. People are left to fill it with headlines and word of mouth.

## Can we predict what happens next?

I also built a forecasting model, and I tested it before trusting it. I trained it only on data up to March 2025, then asked it to predict 2025/26, a year it had never seen. It came within **3.4%** of the real total, closer than the published borough figures themselves.

*[Chart 5a: forecast vs reality]*

For Wigan, it expects crime to **ease slowly**: around **90.6 per 1,000 in 2026/27**. I've saved that forecast with today's date. When the next official figures come out in January 2027, I'll check it publicly, right or wrong.

## What I learnt

1. **Public data isn't always accessible data.** I found the same thing when I built a free food hygiene ratings tool for Wigan. Here, residents of one of England's largest police areas can't see street-level crime at all.
2. **Counts and rates tell different stories.** "Second-highest number of crimes" and "third-lowest crime rate" can both be true of the same place.
3. **Feelings and statistics measure different things.** Feeling unsafe isn't irrational just because the borough average looks typical. Averages hide places and times, and the data that would show them isn't published.

The full report (methods, every table and every limitation) and all the code to reproduce it are free on GitHub. Anyone can rerun the analysis and check my working:

🔗 **https://github.com/dynamixAI/wigan-crime-analysis**

I'd love to hear from you:
- If you live in Wigan, do these numbers match how it feels to you?
- If you work with police or council data, do you know why borough coding stopped in late 2025?

---

## References

[1] Marsden, L. (2023, 17 February). *Wigan isn't as safe as it used to be* [Opinion column]. Wigan Today. https://www.wigantoday.net/news/opinion/columnists/luke-marsden-wigan-isnt-as-safe-as-it-used-to-be-4028619

[2] Lythgoe, G. (2023, 4 February). *Wigan town centre no longer "Dodge City" but "undesirables" still causing concern*. Wigan Today. https://www.wigantoday.net/news/politics/council/wigan-town-centre-no-longer-dodge-city-but-undesirables-still-causing-concern-4013159

[3] Clarke, G. (2025, 11 September). *Wigan bus station stabbings: town centre dispersal order as police stamp down on crime*. Wigan Today. https://www.wigantoday.net/news/crime/wigan-bus-station-stabbings-town-centre-dispersal-order-as-police-stamp-down-on-crime-5313901

[4] Greater Manchester Police. (2026, 8 May). *Four arrested following disturbance in Wigan town centre*. https://www.gmp.police.uk/news/greater-manchester/news/news/2026/may/four-arrested-following-disturbance-in-wigan-town-centre/

[5] Greater Manchester Police. (2026). *Wigan Central: our priorities*. https://www.gmp.police.uk/area/your-area/greater-manchester/wigan/wigan-central/on-the-team/our-priorities

[6] Wigan Council. (2026, 30 June). *Have your say on town centre safety plans*. https://www.wigan.gov.uk/News/Articles/2026/June/Have-your-say-on-town-centre-safety-plans.aspx

[7] Greater Manchester Police. (2026). *FOI 26.016219: Historical street-level crime and stop and search data for 2023, 2024 and 2025*. https://www.gmp.police.uk/SysSiteAssets/foi-media/greater-manchester/disclosure-2026/april/foi-26.016219.i-historical-street-level-crime--stop-search-data-for-years-2023-2024--2025.pdf

[8] Home Office. (2026). *Police recorded crime and outcomes open data tables* (Community Safety Partnership tables, updated 22 October 2026). https://www.gov.uk/government/statistical-data-sets/police-recorded-crime-and-outcomes-open-data-tables

[9] Lees, J. (2026, 24 May). *New figures show more crimes reported to police in Wigan including shoplifting and drug offences*. Wigan Today. https://www.wigantoday.net/news/crime/new-figures-show-more-crimes-reported-to-police-in-wigan-including-shoplifting-and-drug-offences-8567438

[10] Greater Manchester Police. (2026, 20 February). *Neighbourhood crime down and more offenders brought to justice across Wigan district*. https://www.gmp.police.uk/news/greater-manchester/news/news/2026/february/neighbourhood-crime-down-and-more-offenders-brought-to-justice-across-wigan-district/

[11] Clarke, G. (2026, 20 February). *New figures show fewer crimes reported and more solved by police in Wigan*. Wigan Today. https://www.wigantoday.net/news/crime/new-figures-show-fewer-crimes-reported-and-more-solved-by-police-in-wigan-5604444

[12] Police Professional. (2020, 10 December). *GMP failing to record one in five of all reported crimes*. https://policeprofessional.com/?p=130825

#Wigan #GreaterManchester #OpenData #DataAnalysis #DataForGood #CrimeData #Forecasting #Python
