# Five things public crime data taught me about doing analysis properly

*Suggested cover image: Chart 4 (crime vs deprivation, metropolitan boroughs)*

---

On Tuesday I shared what I found when I asked whether Wigan's crime is really as high as people feel it is. This article is about something different: **how I got there**, and the mistakes and lessons along the way.

If you work with data, I suspect at least one of these will feel familiar.

## 1. Code that runs isn't the same as code that's right

My first attempt was a notebook built on the police.uk API. It had hotspot maps, monthly trends and borough comparisons, and the charts looked convincing.

It was wrong in three ways:

- **Every crime was counted three times.** I only noticed because every single count was divisible by 3, with no exceptions. Real data is never that tidy.
- **It only covered a small area.** Each API query returns crimes within a mile of one point, not a whole borough.
- **Inside Greater Manchester, it was mostly railway crime.** Greater Manchester Police hasn't published to police.uk since July 2019, so what came back were British Transport Police records. My "hotspots" were train stations.

Nothing crashed. No warnings. The code ran perfectly.

**What I do now:** before any analysis, I check the totals against a figure I already trust. Wigan records thousands of crimes a month; my API query returned about 10. That one check would have caught all three problems on day one.

## 2. Check the data's history, not just its contents

Once I switched to the Home Office's official borough figures, I found another problem. From late 2025, more and more Greater Manchester crimes stopped being assigned to a borough: from 0.7% in 2024/25 to **84% by spring 2026**.

GMP's total crime stayed steady. But every borough's published figure fell, so a naive chart would have shown crime collapsing across Greater Manchester. The release notes mentioned the same problem for two other forces, but not this one.

*[Chart 6: the share of crimes with no borough recorded]*

I also found that GMP had been put into special measures in 2020, after inspectors found it was failing to record **1 in 5 crimes**. So part of the "rise" in 2021–23 was better recording, not more crime.

**What I do now:** I ask *who collected this data, how, and has that changed?* A change in how data is recorded can look exactly like a change in the real world. I also set a rule before looking at results: a year only counts as reliable if less than 2% of crimes are unassigned.

## 3. "High" always needs "compared to what?"

My headline number was that Wigan's crime rate is **9% above the national average**. Each time I made the comparison fairer, the answer changed:

| Comparison | Wigan vs expected |
|---|---|
| National average | **+9%** |
| Allowing for deprivation, all English areas | **+13%** |
| Only England's 36 big urban (metropolitan) boroughs | **+5%**, 12th of 36 |

The middle step surprised me. Controlling for deprivation made Wigan look *worse*. That's because the comparison included rural districts, which have low crime simply because they're rural. Only when I compared Wigan with places like it did the picture settle: **close to typical for a large urban borough**.

*[Chart 4: crime vs deprivation, metropolitan boroughs]*

And then a twist: the biggest differences between places followed **police force boundaries**. Neighbouring boroughs in different forces differed more than boroughs within the same force. Part of what we call "crime levels" is really about how each force records crime.

**What I do now:** I write down the fairest comparison *before* looking at results, and I treat the first comparison as a starting point, not an answer.

## 4. Test a forecast on data it has never seen

I wanted to forecast Wigan's crime. With only 16 quarters of clean data, I had to be careful.

- **I didn't use machine learning.** I considered gradient-boosted trees, but with so few data points they'd memorise noise. Tree models also can't predict values below what they've seen, which matters when crime is falling.
- **I set a baseline first.** "Same as last year" is surprisingly hard to beat. Any cleverer model had to prove itself against it.
- **I tested from several starting points,** not just one year. A single test year gave a 5% error; rolling tests gave a more honest 6%.
- **I tested on a year the model never saw.** Trained only on data to March 2025, the model predicted 2025/26 to within **3.4%**. That was closer than the published figures, which were 6% short because of the unassigned crimes.

*[Chart 5a: forecast vs reality]*

I also caught myself making a subtle mistake. After seeing the 2025/26 results, I had the idea of averaging two models, and it performed better. But because the idea came *from* looking at that year, that year was no longer a fair test. So I report the original model as the main result, and I've disclosed the change.

**What I do now:** I separate the data I make decisions with from the data I test on, including decisions I make in my head.

## 5. Make it possible for someone to prove you wrong

The final step was making everything reproducible:

- **One command reruns the whole analysis,** from downloading the raw data to every chart.
- **The data files are fingerprinted** (with checksums), so if a source is revised later, anyone can tell.
- **The fitted models are saved,** with a record of exactly how they were built.
- **My next forecast is public and dated.** For July–September 2026, I've predicted GMP will record **79,841 crimes**. The figures come out in January. If I'm wrong, everyone will see it.

That last one is uncomfortable, but it's the point. An analysis that can't be checked is just an opinion with charts.

## What I'd tell any analyst working with public data

1. Check totals against something you already trust, before anything else.
2. Find out how the data is collected, and whether that has changed.
3. Decide what a fair comparison is before you see the results.
4. Test models on data they haven't seen, and beat a simple baseline first.
5. Publish your code, and make your predictions checkable.

The full report, code and saved models are free on GitHub (link in the comments). If you spot something I've missed, I'd genuinely like to know.

**What's the most convincing wrong result you've ever caught?** 👇

#DataAnalysis #DataScience #DataQuality #Forecasting #Python #OpenData
