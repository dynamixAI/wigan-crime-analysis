"""Builds the PDF report from the charts in reports/charts. Figures in the text and tables
were taken from the pipeline outputs of October 2026. Run: python reports/build_report.py"""
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)
from pathlib import Path

from PIL import Image as PILImage

FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
pdfmetrics.registerFont(TTFont("DV", FONT_DIR + "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DV-B", FONT_DIR + "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DV-I", FONT_DIR + "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DV-BI", FONT_DIR + "DejaVuSans-BoldOblique.ttf"))
from reportlab.pdfbase.pdfmetrics import registerFontFamily
registerFontFamily("DV", normal="DV", bold="DV-B", italic="DV-I", boldItalic="DV-BI")

INK = colors.HexColor("#0b0b0b")
SOFT = colors.HexColor("#52514e")
BLUE = colors.HexColor("#2a78d6")
PALE = colors.HexColor("#eaf2fc")
RULE = colors.HexColor("#d9d8d3")
SHADE = colors.HexColor("#f4f3f0")

HERE = Path(__file__).resolve().parent
CH = str(HERE / "charts") + "/"
REPO = "https://github.com/dynamixAI/wigan-crime-analysis"

S = {
    "title": ParagraphStyle("title", fontName="DV-B", fontSize=24, leading=30, textColor=INK, spaceAfter=10),
    "subtitle": ParagraphStyle("subtitle", fontName="DV", fontSize=13, leading=18, textColor=SOFT, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="DV-B", fontSize=16, leading=21, textColor=INK, spaceBefore=6, spaceAfter=8),
    "h2": ParagraphStyle("h2", fontName="DV-B", fontSize=12, leading=16, textColor=INK, spaceBefore=8, spaceAfter=5),
    "body": ParagraphStyle("body", fontName="DV", fontSize=9.6, leading=14.2, textColor=INK, spaceAfter=6,
                           alignment=TA_LEFT),
    "bullet": ParagraphStyle("bullet", fontName="DV", fontSize=9.6, leading=14.2, textColor=INK, leftIndent=12,
                             bulletIndent=2, spaceAfter=3),
    "caption": ParagraphStyle("caption", fontName="DV-I", fontSize=8.2, leading=11, textColor=SOFT, spaceAfter=10),
    "cell": ParagraphStyle("cell", fontName="DV", fontSize=8.2, leading=10.5, textColor=INK),
    "cellb": ParagraphStyle("cellb", fontName="DV-B", fontSize=8.2, leading=10.5, textColor=INK),
    "box": ParagraphStyle("box", fontName="DV", fontSize=9.6, leading=14.2, textColor=INK),
    "small": ParagraphStyle("small", fontName="DV", fontSize=8.2, leading=11.5, textColor=SOFT, spaceAfter=3),
}

S["h1"].keepWithNext = 1
S["h2"].keepWithNext = 1
story = []


def P(text, style="body"):
    story.append(Paragraph(text, S[style]))


def bullets(items):
    for t in items:
        story.append(Paragraph(t, S["bullet"], bulletText="•"))
    story.append(Spacer(1, 4))


def pull_heading():
    # Keep a heading on the same page as the chart or table that follows it
    if story and isinstance(story[-1], Paragraph) and story[-1].style.name in ("h1", "h2"):
        return [story.pop()]
    return []


def chart(name, caption, width=170):
    w, h = PILImage.open(CH + name).size
    img = Image(CH + name, width=width * mm, height=width * mm * h / w)
    story.append(KeepTogether(pull_heading() + [img, Spacer(1, 3), Paragraph(caption, S["caption"])]))


def table(rows, widths, highlight=None, caption=None, bold_last=False, align_right_from=1):
    data = []
    for r_i, row in enumerate(rows):
        style = "cellb" if r_i == 0 or (bold_last and r_i == len(rows) - 1) else "cell"
        data.append([Paragraph(str(c), S[style]) for c in row])
    t = Table(data, colWidths=[w * mm for w in widths], repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), SHADE),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, INK),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, RULE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ]
    if highlight:
        for r in highlight:
            ts.append(("BACKGROUND", (0, r), (-1, r), PALE))
    t.setStyle(TableStyle(ts))
    parts = pull_heading() + [t]
    if caption:
        parts += [Spacer(1, 3), Paragraph(caption, S["caption"])]
    else:
        parts.append(Spacer(1, 8))
    story.append(KeepTogether(parts))


def callout(text):
    t = Table([[Paragraph(text, S["box"])]], colWidths=[170 * mm])
    t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("LINEBEFORE", (0, 0), (0, -1), 3, BLUE),
                           ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                           ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    story.append(t)
    story.append(Spacer(1, 10))


def page(canvas, doc):
    canvas.saveState()
    canvas.setFont("DV", 7.5)
    canvas.setFillColor(SOFT)
    if doc.page > 1:
        canvas.drawString(20 * mm, 287 * mm, "Is Wigan's crime high? Recorded crime analysis and forecast")
        canvas.drawRightString(190 * mm, 287 * mm, "Pius Ajamma · October 2026")
        canvas.setStrokeColor(RULE)
        canvas.line(20 * mm, 285 * mm, 190 * mm, 285 * mm)
    canvas.drawRightString(190 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


# =============================================================================
# Title page
# =============================================================================
story.append(Spacer(1, 45 * mm))
P("Is Wigan's crime high?", "title")
P("An analysis of police recorded crime in the Wigan borough, 2020/21 to 2025/26, "
  "with tests against deprivation and forecasts to 2030/31", "subtitle")
story.append(Spacer(1, 10 * mm))
P("<b>Pius Ajamma</b><br/>MSc Data Science<br/>October 2026", "body")
story.append(Spacer(1, 8 * mm))
P(f"Code, data pipeline and saved models: <font color='#2a78d6'>{REPO}</font>", "small")
P("Data: Home Office police recorded crime (Community Safety Partnership open data tables, release of "
  "22 October 2026); ONS mid-year population estimates; English Indices of Deprivation 2025. "
  "Contains public sector information licensed under the Open Government Licence v3.0.", "small")
story.append(Spacer(1, 20 * mm))
callout("<b>In one sentence:</b> Wigan's recorded crime rate is about 9% above the England and Wales average, "
        "but that is largely what you would expect for a large urban borough with its level of deprivation. "
        "Among England's 36 metropolitan boroughs it is close to typical, it is the third lowest of "
        "Greater Manchester's ten boroughs, and it has been falling faster than the national rate.")
story.append(PageBreak())

# =============================================================================
# Executive summary
# =============================================================================
P("Executive summary", "h1")
P("This report asks a simple question that turns out to need careful handling: <b>is crime in Wigan high?</b> "
  "A raw comparison with the national average says yes. Each fairer comparison, controlling for deprivation "
  "and then for the kind of place Wigan is, shrinks that gap. The answer the evidence supports is that "
  "Wigan is close to typical for a place like it.")
P("Key findings", "h2")
bullets([
    "<b>Level.</b> In 2024/25, the latest year with reliable borough figures, Wigan recorded 91.9 crimes per "
    "1,000 residents (excluding fraud): 9% above England and Wales (84.6), 13% below the Greater Manchester "
    "average (106.2) and 9% below Bolton (101.1). Wigan ranks 8th of Greater Manchester's 10 boroughs, the "
    "3rd lowest.",
    "<b>Trend.</b> Wigan's rate fell 18% from its 2021/22 peak (112.1) to 2024/25, against a 4% fall nationally. "
    "Part of the earlier rise reflects Greater Manchester Police (GMP) improving how it records crime after a "
    "2020 inspection.",
    "<b>Type.</b> Wigan has more violence (+26%), public order offences (+48%) and criminal damage (+24%) than "
    "the national average, and less theft (−28%) and robbery (−31%). Violence and public order are the "
    "categories most affected by police recording practice.",
    "<b>Compared like with like.</b> Against areas with similar income deprivation, Wigan looks 8–13% higher than "
    "expected. But against England's 36 metropolitan boroughs only, the gap falls to +5% (12th of 36), and "
    "Wigan's raw rate is below the metropolitan median (98.3). The largest differences between places follow "
    "police force boundaries.",
    "<b>A data gap.</b> GMP has not supplied street-level crime data to police.uk since July 2019. In addition, "
    "the share of GMP crimes with no borough recorded rose from 0.7% in 2024/25 to 84% by April–June 2026, so official borough "
    "figures from 2025/26 onwards are understated. The release notes do not mention this for Greater Manchester.",
    "<b>Forecast.</b> A Holt-Winters model trained only on data to March 2025 predicted GMP's 2025/26 total to "
    "within 3.4%, closer than the published borough figures (6.0% short). For Wigan, the central forecast is "
    "90.6 crimes per 1,000 in 2026/27 (range 88–93) and 88.4 in 2027/28 (82–95). Beyond two years, results are "
    "presented as scenarios only.",
])
table([
    ["Measure (crimes per 1,000, excl. fraud)", "Wigan", "Comparison", "Difference"],
    ["2024/25 vs England and Wales", "91.9", "84.6", "+9%"],
    ["2024/25 vs Greater Manchester", "91.9", "106.2", "−13%"],
    ["2024/25 vs Bolton (control borough)", "91.9", "101.1", "−9%"],
    ["vs expected for its income deprivation (all English areas)", "92.5", "85.8", "+8%"],
    ["vs expected, 36 metropolitan boroughs only", "92.5", "88.0", "+5%"],
    ["2025/26 estimate vs England and Wales", "89.5–90.7", "82.9", "+8–9%"],
    ["Forecast 2026/27 (range)", "90.6 (88–93)", "–", "–"],
], [78, 28, 32, 32], caption="Table 1. Headline figures. The 2024/25 deprivation comparison uses Wigan's rate after "
                             "sharing out GMP's 0.7% unassigned crimes (92.5).")
story.append(PageBreak())

# =============================================================================
# 1. Questions and approach
# =============================================================================
P("1. Introduction", "h1")
P("1.1 The public debate", "h2")
P("Residents often say they feel unsafe in parts of Wigan town centre at certain times, and that view is "
  "reflected in local coverage. A Wigan Today columnist wrote in 2023 that <i>\"Wigan is a crime hotspot. It's "
  "unsafe.\"</i> [1] The same month, councillors raised concerns that daytime drinking and anti-social behaviour "
  "around the bus station were deterring families from the town centre [2]. More recent incidents have kept the "
  "issue in the news: two people were stabbed at Wigan bus station in September 2025, after which police issued "
  "a dispersal order. Police said: <i>\"Anti-social behaviour and violence have no place in our town "
  "centre.\"</i> [3] In May 2026, a man was injured, apparently by a knife, during a disturbance on Market "
  "Street [4]. Police list violent crime, anti-social behaviour and the town centre night-time economy among "
  "their 2026 priorities for central Wigan [5], and Wigan Council is consulting on renewing its town centre "
  "public space protection orders [6].")
P("Published figures point in different directions. In February 2026, Wigan Today reported a 5% fall in "
  "recorded crime in the year to September 2025 [11], and GMP reported that residential burglary fell 24% and "
  "personal robbery 21% across Wigan and Leigh in 2025, with its local inspector stating that officers were "
  "<i>\"responding faster, solving more crimes\"</i> [10]. Three months later, Wigan Today reported a rise in "
  "recorded crime and noted that Wigan recorded the second-highest number of crimes in Greater Manchester [9]. "
  "Reports like these usually describe counts over short periods. This analysis uses rates per resident over "
  "six years, and compares them fairly.")
P("1.2 Questions and approach", "h2")
P("This analysis tests whether recorded crime supports the view that Wigan has a high crime rate, using only "
  "public data so that anyone can check it. It answers four questions:")
bullets([
    "<b>Q1.</b> How does Wigan's recorded crime rate compare with its neighbours, Greater Manchester and the "
    "national average, and how is it changing?",
    "<b>Q2.</b> Which types of crime drive any difference?",
    "<b>Q3.</b> Is any difference explained by the kind of place Wigan is: its deprivation and its urban character?",
    "<b>Q4.</b> What is likely to happen next, and how far ahead can that be forecast honestly?",
])
P("Two principles run through the method. First, <b>compare rates, not counts</b>: every comparison uses crimes "
  "per 1,000 residents, because larger places always have more crimes. Second, <b>test the conclusion, "
  "not just the data</b>: each finding was challenged with a fairer comparison, and the report shows how the "
  "answer changed at each step.")
P("1.3 What this analysis cannot do", "h2")
P("The data is borough-level and quarterly. It cannot say anything about specific streets, the town centre, or "
  "particular times of day, because GMP does not publish street-level data (section 2.1). Recorded crime also "
  "differs from crime that actually happens: it depends on what people report and how police record it. The "
  "report is careful to separate these.")

# =============================================================================
# 2. Data
# =============================================================================
P("2. Data", "h1")
P("2.1 Why the obvious source could not be used", "h2")
P("The usual source for local crime analysis is police.uk, which publishes street-level crimes through an open "
  "API. An initial analysis used it, and produced misleading results for two reasons:")
bullets([
    "<b>GMP stopped supplying police.uk in July 2019.</b> In a 2026 Freedom of Information response (ref. "
    "26.016219) [7], GMP confirmed it \"hasn't provided data to police.uk since July 2019\" and has no timeline to "
    "resume. Querying the API for the whole Wigan boundary returned only 5–17 crimes a month, against several "
    "thousand actually recorded. Of the 381 records returned over three years, 96 were British Transport Police "
    "railway crimes.",
    "<b>An earlier notebook built on the API contained errors that were invisible without this context:</b> every "
    "record appeared three times (all counts were divisible by three), the data came from a 1-mile radius around "
    "a single point rather than the whole borough, and inside Greater Manchester it was mostly railway crime.",
])
P("This is worth stating because anyone checking Wigan's crime on police.uk today would find almost nothing, "
  "and could wrongly conclude crime is very low.")

P("2.2 Crime data used", "h2")
P("The analysis uses the Home Office <i>Police recorded crime Community Safety Partnership open data tables</i> "
  "(year ending March 2021 to year ending June 2026; updated 22 October 2026) [8]. These are the same figures the "
  "ONS uses in its official <i>Crime in England and Wales</i> statistics. Every police force, including GMP, must "
  "report them to the Home Office.")
table([
    ["Property", "Detail", "Why it matters"],
    ["Coverage", "Every Community Safety Partnership (CSP) in England and Wales", "All comparison areas come from one consistent source"],
    ["Geography", "CSP, which matches the local authority (Wigan CSP = Wigan borough)", "Borough-level rates can be matched to population"],
    ["Time", "Quarterly, by financial year (April–March)", "Seasonality can be modelled"],
    ["Detail", "Offence group, subgroup and 144 offence types", "Crime mix can be compared"],
    ["Format", "Long format: one row per area, quarter and offence type", "Already tidy; 1.24 million rows in total"],
    ["Licence", "Open Government Licence v3.0", "Free to reuse and publish"],
], [28, 76, 66])
P("The release was converted from ODS to one CSV per financial year with LibreOffice (about three minutes), "
  "which is much faster and lighter than reading a 50 MB spreadsheet directly in pandas.", "small")

P("2.3 Definitions", "h2")
bullets([
    "<b>Fraud is excluded.</b> Since 2011–2013, fraud has been recorded centrally by Action Fraud rather than local "
    "police, so it is largely missing at local level and would distort borough comparisons [19].",
    "<b>Anti-social behaviour is not included.</b> It is not a notifiable crime and is not in these tables.",
    "<b>Greater Manchester</b> means the whole of GMP's recorded crime, including crimes with no borough "
    "recorded and Manchester Airport, so that it is never understated.",
])

P("2.4 Population and deprivation", "h2")
P("<b>Population:</b> ONS mid-year population estimates from Nomis (dataset NM_2002_1) [18], mid-2020 to mid-2025, "
  "for the 10 Greater Manchester boroughs and England and Wales, and mid-2024 for all 296 English local "
  "authorities. The mid-year estimate for year N (30 June) falls inside financial year N/N+1, so mid-2024 "
  "population is used for 2024/25 crime.")
P("<b>Deprivation:</b> English Indices of Deprivation 2025 (File 10, version 2, the corrected release) [17]. The "
  "analysis uses the <b>income domain</b>, the share of residents on low incomes, not the overall Index of "
  "Multiple Deprivation. The overall index includes a <i>crime</i> domain, so using it to explain crime would be "
  "circular. The index covers England only.")

P("2.5 Data quality checks", "h2")
P("Before any modelling, the data was checked for the problems that most often break analyses of this kind.")
table([
    ["Check", "Result", "Action"],
    ["Counts that are not numbers", "0 of 1,243,788 rows", "None needed"],
    ["Negative counts (row level)", "1 row", "None: explained in the release notes (cancelled or transferred crimes); disappears on aggregation"],
    ["Missing borough-quarters, 2021/22–2024/25", "160 of 160 present", "None: no gaps to fill"],
    ["Zero or negative borough-quarters", "0", "None"],
    ["Outliers", "Each borough within about ±15% of its own average", "None: normal seasonal and yearly variation"],
    ["Crimes with no borough recorded", "0.3–0.7% to 2024/25; then rising sharply", "See section 3"],
], [52, 50, 68])


# =============================================================================
# 3. Unassigned crimes
# =============================================================================
P("3. A data problem: crimes with no borough", "h1")
P("When GMP records a crime it is normally tagged with the borough where it happened. Crimes without a "
  "location appear under a catch-all area, <i>Unassigned Greater Manchester</i>. This was routinely below 1% "
  "of GMP's crime. From the second half of 2025 it rose sharply.")
chart("06_unassigned.png", "Figure 1. Share of GMP recorded crime with no borough recorded, by year and then by quarter.")
table([
    ["Period", "GMP total (excl. fraud)", "Unassigned", "Share"],
    ["2020/21", "273,382", "946", "0.3%"], ["2021/22", "351,488", "943", "0.3%"],
    ["2022/23", "371,708", "1,405", "0.4%"], ["2023/24", "342,139", "1,413", "0.4%"],
    ["2024/25", "318,627", "2,287", "0.7%"], ["2025/26", "311,748", "18,499", "5.9%"],
    ["2026/27 Q1 (Apr–Jun 2026)", "81,052", "67,773", "83.6%"],
], [62, 40, 34, 34], highlight=[6, 7], caption="Table 2. GMP crimes with no borough recorded.")
P("GMP's total stayed steady at about 81,000 crimes a quarter, so <b>crime did not fall: crimes stopped being "
  "linked to a borough</b>. Every borough's published figure shrinks, by different amounts (in January–March "
  "2026, Wigan lost 19% and Bolton 8%), so rankings for that period are also distorted. The release notes "
  "describe similar problems in Kent and Humberside, but not Greater Manchester. The cause is not known; a "
  "change in GMP's systems or location coding is plausible but unconfirmed.")
P("How it was handled", "h2")
bullets([
    "<b>Reliability rule:</b> a year is used for borough comparison only if no more than 2% of GMP's crimes are "
    "unassigned. This makes <b>2024/25 the latest reliable year</b>.",
    "<b>2025/26 estimate:</b> unassigned crimes were shared out to each borough in proportion to its recorded "
    "crimes, and labelled as an estimate. An independent forecast (section 6) was used to check it.",
    "<b>2026/27 Q1</b> was excluded from all borough-level analysis.",
])


# =============================================================================
# 4. Findings
# =============================================================================
P("4. How Wigan compares", "h1")
P("4.1 Trend over time", "h2")
chart("01_trend.png", "Figure 2. Recorded crimes per 1,000 residents. 2025/26 values for Wigan and Bolton are estimates.")
table([
    ["Area", "2020/21", "2021/22", "2022/23", "2023/24", "2024/25", "2025/26"],
    ["Wigan", "88.7", "112.1", "110.6", "103.2", "91.9", "90.7*"],
    ["Bolton", "96.6", "122.3", "120.7", "109.2", "101.1", "99.2*"],
    ["Greater Manchester", "95.7", "122.5", "127.4", "115.6", "106.2", "103.3"],
    ["England and Wales", "77.1", "88.5", "91.4", "87.1", "84.6", "82.9"],
], [44, 21, 21, 21, 21, 21, 21], highlight=[1],
    caption="Table 3. Crimes per 1,000 residents, excluding fraud. *Estimate with unassigned crimes shared out "
            "(published figures 85.3 and 93.3 are understated).")
P("Wigan stays below Greater Manchester and Bolton throughout. Its rate fell 18% from the 2021/22 peak to "
  "2024/25, compared with 4% nationally, and its gap above the national rate narrowed from 21% (2022/23) to 9% "
  "(2024/25).")
P("This is consistent with independent reports. GMP reported falls in residential burglary (24%) and personal "
  "robbery (21%) across Wigan and Leigh in 2025 [10], and Wigan Today reported a 5% fall in recorded crime in the "
  "year to September 2025 [11]. A later report of a small rise in the year to December 2025 [9] covers the period "
  "when crimes began to go unassigned (section 3), so short-term movements in published borough figures from "
  "late 2025 should be read with caution.")

P("4.2 Recording practice in Greater Manchester: an important caveat", "h2")
P("In December 2020, HM Inspectorate of Constabulary (HMICFRS) reported that GMP had failed to record an "
  "estimated <b>80,100 crimes</b> in the year to June 2020: about one in five reported crimes and one in four "
  "violent crimes (GMP recorded 77.7% of reported crime) [12]. Under-recording was worst for violent crime, including "
  "domestic abuse, harassment, stalking and coercive control. GMP was placed in special measures in December "
  "2020 [13] and removed in October 2022, when inspectors found it compliant with national crime recording "
  "standards, recording about 30,500 crimes a month [14][15]. A December 2023 inspection rated no area inadequate [16].")
callout("<b>Implication:</b> part of the rise in recorded crime across Greater Manchester between 2020/21 and "
        "2022/23, especially in violence and public order offences, is likely to reflect better recording rather "
        "than more crime. Covid-19 lockdowns also lowered crime nationally in 2020/21. Comparisons from 2022/23 "
        "onwards are the most reliable. As a cross-check, this analysis finds GMP recorded 371,708 crimes "
        "(excluding fraud) in 2022/23, about 31,000 a month, consistent with the inspectorate's figure.")

P("4.3 Greater Manchester ranking", "h2")
chart("02_gm_ranking.png", "Figure 3. Greater Manchester boroughs, 2024/25.", width=150)
table([
    ["Rank", "Borough", "Crimes", "Per 1,000 (2024/25)", "2025/26 estimate"],
    ["1", "Manchester", "85,842", "145.8", "142.6"], ["2", "Oldham", "27,245", "108.7", "105.7"],
    ["3", "Rochdale", "25,455", "108.4", "103.9"], ["4", "Salford", "30,450", "103.7", "104.0"],
    ["5", "Bolton", "31,243", "101.1", "99.2"], ["6", "Tameside", "23,492", "98.3", "96.1"],
    ["7", "Bury", "18,572", "93.7", "91.7"], ["8", "Wigan", "31,624", "91.9", "90.7"],
    ["9", "Stockport", "23,079", "76.4", "74.0"], ["10", "Trafford", "17,730", "74.0", "75.5"],
], [16, 40, 30, 42, 42], highlight=[8],
    caption="Table 4. Rank is by 2024/25 rate (1 = highest). The 2025/26 estimate shares out unassigned crimes; "
            "Wigan stays 8th.")

P("Counts and rates can tell different stories. Wigan Today reported in May 2026 that Wigan recorded the "
  "second-highest number of crimes in Greater Manchester [9]. That is correct as a count, but Wigan is also "
  "Greater Manchester's second-largest borough, with about 347,000 residents in mid-2025 [18]. Per resident, it "
  "has the third-lowest rate of the ten boroughs. This difference between counts and rates is a likely reason "
  "why public perception and recorded crime rates can disagree.")
P("4.4 Types of crime", "h2")
chart("03_offence_types.png", "Figure 4. Wigan compared with England and Wales by offence group, 2024/25.", width=150)
table([
    ["Offence group", "Wigan", "Bolton", "Greater Manchester", "England and Wales", "Wigan vs E&amp;W"],
    ["Violence against the person", "39.3", "42.6", "41.6", "31.1", "1.26×"],
    ["Theft offences", "20.3", "24.8", "28.4", "28.2", "0.72×"],
    ["Public order offences", "10.5", "11.5", "12.0", "7.1", "1.48×"],
    ["Criminal damage and arson", "9.2", "8.3", "8.8", "7.4", "1.24×"],
    ["Drug offences", "3.7", "4.3", "5.2", "3.3", "1.12×"],
    ["Sexual offences", "3.4", "3.7", "4.0", "3.4", "1.00×"],
    ["Miscellaneous crimes against society", "3.3", "3.1", "3.1", "2.0", "1.65×"],
    ["Possession of weapons", "1.2", "1.5", "1.6", "0.9", "1.33×"],
    ["Robbery", "0.9", "1.4", "1.5", "1.3", "0.69×"],
], [52, 18, 18, 28, 28, 26], caption="Table 5. Crimes per 1,000 residents by offence group, 2024/25.")
P("Wigan is above the national rate for violence, public order and criminal damage, and well below it for theft "
  "and robbery. It is below the Greater Manchester average in almost every group; the exceptions are criminal "
  "damage (9.2 vs 8.8) and miscellaneous crimes (3.3 vs 3.1). Because violence and public order are the "
  "categories most sensitive to recording practice, the differences from the national rate should be read "
  "alongside section 4.2.")


# =============================================================================
# 5. Deprivation
# =============================================================================
P("5. Is Wigan high for a place like it?", "h1")
P("A reviewer's strongest objection to section 4 is: <i>Wigan is more deprived than England as a whole, and "
  "deprivation goes with higher crime, so being above average may be expected.</i> Wigan ranks 102nd of 296 "
  "English areas on income deprivation (23.9% of residents on low incomes) and 78th on the overall index, "
  "placing it in the more deprived third. This section tests the objection in three steps.")
P("Method", "h2")
bullets([
    "Crime (2024/25), population (mid-2024) and income deprivation were joined for every English local authority. "
    "Names were standardised to match, and districts that merged since the crime file was set up (for example "
    "Aylesbury Vale and others into Buckinghamshire) were combined.",
    "Forces with more than 5% of crime unassigned were excluded (Kent 35.1%, Humberside 12.0%). For other forces, "
    "unassigned crime was shared out within the force. A looser rule than section 3 is acceptable here because "
    "rates across England range from about 40 to over 150 per 1,000, so a correction of a few percent barely "
    "moves any area.",
    "250 of 296 areas were analysed (City of London and the Isles of Scilly were dropped for tiny populations). "
    "Areas not matched are mainly in Kent and Humberside, and some multi-district crime areas in Devon, "
    "Worcestershire and Suffolk.",
    "An ordinary least squares line of crime rate on income deprivation gives each area's <b>expected</b> rate. "
    "The gap between actual and expected shows whether an area has more or less crime than its deprivation "
    "predicts.",
])
P("Results: how the answer changed with each fairer comparison", "h2")
table([
    ["Step", "Comparison", "Wigan expected", "Wigan actual", "Gap"],
    ["1", "Raw: England and Wales average", "84.6", "91.9", "+9%"],
    ["2a", "All 250 English areas, line through all", "85.8", "92.5", "+7.7%"],
    ["2b", "All areas, without the 10 highest-rate areas (city centres)", "82.0", "92.5", "+12.8%"],
    ["2c", "15 areas most similar on income deprivation (median)", "82.7", "92.5", "+11.9%"],
    ["3", "36 metropolitan boroughs only (core cities excluded from the line)", "88.0", "92.5", "+5.1%"],
], [12, 86, 26, 24, 22], highlight=[5],
    caption="Table 6. Step 2b: R<super>2</super> = 0.62, 2.4 more crimes per 1,000 for each extra 1% on low incomes. "
            "Step 3: R<super>2</super> = 0.33, slope 1.5.")
P("Controlling for deprivation alone does not explain Wigan's gap; it makes it slightly larger (step 2). Removing "
  "city centres, where visitors and commuters inflate per-resident rates, improved the fit sharply "
  "(R<super>2</super> from 0.35 to 0.62). But many of Wigan's deprivation \"peers\" are rural or small-town "
  "districts (Fenland, Bolsover, the Isle of Wight, Rossendale), which have low crime simply because they are "
  "rural. Restricting the comparison to the 36 metropolitan boroughs, large urban areas like Wigan, reduces the "
  "gap to +5%.")
chart("04_deprivation.png", "Figure 5. Crime against income deprivation for England's 36 metropolitan boroughs, 2024/25.")
P("Among metropolitan boroughs, Wigan ranks 12th of 36 on the gap from expected, and its raw rate (92.5) is below "
  "the metropolitan median (98.3). The spread runs from Manchester (+36%) and Leeds (+35%) to Knowsley (−21%) and "
  "Wirral (−25%), so +5% is well within normal variation.")
P("Police force effects", "h2")
P("The biggest differences line up with police force boundaries rather than individual places. After allowing for "
  "deprivation, the median area in each force ranges from +27% (Avon and Somerset) and +26% (West Yorkshire) to "
  "−24% (West Mercia) and −26% (Norfolk). GMP's median is +7.6%. Neighbouring boroughs in different forces "
  "differ more than boroughs in the same force: West and South Yorkshire boroughs sit mostly above the line, "
  "Merseyside and West Midlands boroughs mostly below, and most GMP boroughs sit between 0% and +6% in the "
  "metropolitan comparison. This is consistent with differences in how forces record crime, or with genuine regional "
  "differences; the data cannot separate the two.")
table([
    ["Force (median vs expected)", "Gap", "Force", "Gap"],
    ["Avon and Somerset", "+26.8%", "Leicestershire", "+3.2%"],
    ["West Yorkshire", "+25.9%", "Northamptonshire", "+2.3%"],
    ["Cleveland", "+18.7%", "Lincolnshire", "−15.8%"],
    ["Devon and Cornwall", "+14.4%", "Bedfordshire", "−16.4%"],
    ["South Yorkshire", "+11.4%", "Wiltshire", "−17.2%"],
    ["<b>Greater Manchester</b>", "<b>+7.6%</b>", "West Mercia", "−24.2%"],
    ["Durham / Essex", "+6.7% / +6.4%", "Norfolk", "−26.1%"],
], [55, 30, 55, 30], caption="Table 7. Median gap from the deprivation-expected rate by force (line without the 10 "
                             "highest-rate areas). Top ten and bottom five forces shown.")
callout("<b>Answer to Q3:</b> Wigan's crime rate is above the national average mainly because it is a large urban "
        "borough with above-average deprivation. Compared with similar urban boroughs it is close to typical: about "
        "5% above what its deprivation predicts and below the median raw rate.")


# =============================================================================
# 6. Forecasting
# =============================================================================
P("6. Forecasting", "h1")
P("6.1 Approach and why", "h2")
bullets([
    "<b>Short series, simple models.</b> Each borough has 16 clean quarters (2021/22–2024/25). Models with many "
    "parameters, such as gradient-boosted trees or neural networks, would memorise so few points. Tree-based "
    "models also cannot predict values below those seen in training, which matters when crime is falling. With "
    "short seasonal series, exponential smoothing (Holt-Winters) is the standard, well-tested choice "
    "(Hyndman and Athanasopoulos, <i>Forecasting: Principles and Practice</i>) [20].",
    "<b>A baseline to beat.</b> Seasonal naive (each quarter equals the same quarter last year) is included so any "
    "gain from a cleverer model is measured, not assumed.",
    "<b>Time-ordered splits only.</b> A random train/test split would put future quarters into training (data "
    "leakage). All tests train on earlier quarters and predict later ones; the code checks this automatically.",
    "<b>2020/21 excluded</b> from training: it combines Covid lockdowns with GMP's under-recording period. Older "
    "data (2015/16–2019/20) was deliberately not used for the same reason.",
    "<b>No scaling.</b> Each model sees one borough's series on its own, and the models used give identical "
    "forecasts with or without rescaling. The normalisation that matters, per 1,000 residents, is applied after "
    "forecasting.",
])
P("6.2 Choosing a model", "h2")
P("A single back-test (train 2021/22–2023/24, predict 2024/25) compared three simple models by mean absolute "
  "percentage error (MAPE):")
table([
    ["Borough", "Seasonal naive", "Trend + season (linear)", "Holt-Winters (damped, additive)"],
    ["Bolton", "6.6", "3.5", "2.2"], ["Bury", "8.4", "6.9", "7.1"], ["Manchester", "9.9", "13.8", "1.6"],
    ["Oldham", "5.0", "4.8", "2.7"], ["Rochdale", "2.5", "1.7", "4.0"], ["Salford", "7.1", "13.2", "3.0"],
    ["Stockport", "10.3", "12.7", "3.2"], ["Tameside", "5.7", "4.1", "3.6"], ["Trafford", "4.2", "3.5", "18.1"],
    ["Wigan", "10.9", "9.0", "4.3"], ["Average", "7.1", "7.3", "5.0"],
], [40, 38, 46, 46], highlight=[10], bold_last=True,
    caption="Table 8. Back-test error (MAPE, %) predicting 2024/25. The linear trend failed for boroughs whose "
            "crime rose then fell (Manchester, Salford, Stockport).")
P("A single test year can flatter or punish a model by chance (note Trafford's 18.1%). Six Holt-Winters designs "
  "were therefore compared with <b>rolling-origin cross-validation</b>: forecasts from six successive starting "
  "points (training ending 2023/24 Q2 through 2024/25 Q3), giving 18 predictions per borough, with no data after "
  "March 2025.")
table([
    ["Design", "Average", "Median", "Worst borough", "Boroughs won"],
    ["HW damped trend, multiplicative season", "6.0", "6.4", "10.1", "2"],
    ["HW damped trend, additive season", "6.2", "6.4", "9.9", "2"],
    ["HW no trend, additive season", "6.3", "6.2", "8.7", "1"],
    ["HW no trend, multiplicative season", "6.4", "6.5", "8.7", "1"],
    ["HW trend, multiplicative season", "6.5", "7.0", "12.0", "3"],
    ["HW trend, additive season", "7.4", "7.8", "11.8", "0"],
    ["Seasonal naive (baseline)", "7.8", "7.3", "10.6", "1"],
], [70, 22, 22, 30, 26], highlight=[1],
    caption="Table 9. Rolling-origin cross-validation (MAPE, %). Every Holt-Winters design beat the baseline; the "
            "top four are within 0.4 points of each other. The single back-test (5.0%) was optimistic; about 6% is "
            "the realistic error.")
P("The damped multiplicative design was selected (6.0% average; 6.4% for Wigan). Multiplicative seasonality "
  "means each quarter is a percentage above or below normal, so seasonal swings shrink in proportion as crime "
  "falls. Damping makes the trend fade instead of continuing indefinitely. In the single back-test, Wigan's damped "
  "model learned smoothing parameters of about 0.54 (level and trend), 0.00 (season, meaning a stable seasonal "
  "pattern) and 0.87 (damping).")
P("Ensemble", "h2")
P("Averaging forecasts from different models is one of the most reliable findings in forecasting research, "
  "including the M4 competition (Makridakis et al., 2020) [21]. The damped model assumes the recent fall continues "
  "and fades; the no-trend model assumes crime stays level. Weights from 0 to 1 were tested on the same "
  "cross-validation, on a fine grid (steps of 0.05) with unrounded errors.")
table([
    ["Weight on damped model", "0.00", "0.25", "0.50", "0.55", "0.75", "1.00"],
    ["Average error (%)", "6.36", "5.84", "5.55", "5.54", "5.68", "6.02"],
], [52, 19, 19, 20, 20, 20, 20], caption="Table 10. The combination beats either model alone. The optimum (0.55) was "
                                         "used; it is 0.01 points better than an equal mix, consistent with the \"forecast combination puzzle\" that tuned "
                                         "weights rarely beat equal ones by much [22].")
P("On the 2024/25 back-test the single model and the ensemble tied (5.1% each), but the ensemble cut the worst "
  "borough error by a third (Trafford 18.4% to 12.4%). The single model leaned low (−0.8%) and the ensemble high "
  "(+1.6%) in a year when crime fell; the reverse was true in 2025/26 when crime levelled off. Because the "
  "direction of the next change is unknown, the ensemble is used for forward forecasts.")
callout("<b>Disclosure.</b> The ensemble was added after observing that the original model under-predicted when "
        "crime levelled off in 2025/26. Its cross-validation score uses only data to March 2025, but because the "
        "idea came from viewing later data, its 2025/26 performance is not treated as an independent test. The "
        "single damped model, chosen before 2025/26 was examined, is the primary out-of-sample result.")

P("6.3 Out-of-sample test: 2025/26", "h2")
P("The selected model was trained on 2021/22–2024/25 and forecast 2025/26 without seeing it. Borough figures "
  "for 2025/26 are understated (section 3), but GMP's force total is complete, because unassigned crimes are still "
  "counted. That makes the force total a fair test.")
chart("05a_forecast_test.png", "Figure 6. GMP borough crime by quarter: actual (complete), forecast, and published borough figures.")
table([
    ["2025/26", "Actual (complete)", "Forecast", "Error", "Published boroughs", "Error"],
    ["Q1 (Apr–Jun)", "81,321", "78,102", "−4.0%", "80,073", "−1.5%"],
    ["Q2 (Jul–Sep)", "79,839", "76,857", "−3.7%", "78,003", "−2.3%"],
    ["Q3 (Oct–Dec)", "75,758", "73,880", "−2.5%", "71,808", "−5.2%"],
    ["Q4 (Jan–Mar)", "73,517", "71,117", "−3.3%", "62,052", "−15.6%"],
    ["Year", "310,435", "299,956", "−3.4%", "291,936", "−6.0%"],
], [30, 30, 26, 22, 34, 22], bold_last=True,
    caption="Table 11. Single damped model trained to March 2025. Actual excludes Manchester Airport. The ensemble's "
            "error for the year was −2.3%.")
P("The forecast stayed within the cross-validation error, with a steady under-prediction rather than drift: "
  "crime fell, but less than the 2024/25 trend implied. For April–September 2025, when few crimes were "
  "unassigned, borough forecasts averaged 3.0% error (Wigan −0.9%).")
table([
    ["Wigan 2025/26", "Crimes", "Per 1,000", "vs England and Wales (82.9)"],
    ["Published (understated)", "29,611", "85.3", "1.03×"],
    ["Single model forecast", "30,487", "87.8", "1.06×"],
    ["Ensemble forecast", "31,072", "89.5", "1.08×"],
    ["Unassigned crimes shared out", "31,487", "90.7", "1.09×"],
], [60, 30, 30, 50], caption="Table 12. Two independent methods, one using 2025/26 data and one not, agree that "
                             "Wigan's 2025/26 rate was about 6–9% above England and Wales, as in 2024/25.")

P("6.4 How far ahead can this be trusted?", "h2")
P("A two-year test at force level (train 2021/22–2023/24, predict 2024/25 and 2025/26) measured how error grows:")
table([
    ["", "Year 1 error", "Year 2 error", "Direction"],
    ["Holt-Winters (damped, multiplicative)", "3.0%", "7.2%", "Under-predicted every quarter"],
    ["Seasonal naive", "7.2%", "9.5%", "–"],
], [62, 30, 30, 48], caption="Table 13. Error more than doubles in year 2. A simulated 90% interval covered all 8 "
                             "quarters but was too wide to be useful (about ±24% and ±68%), so measured errors are used instead.")
table([
    ["Horizon", "Verdict", "How it is presented"],
    ["1 year (2026/27)", "Reliable", "Forecast ±3%"],
    ["2 years (2027/28)", "Usable", "Forecast ±7%"],
    ["3–5 years (to 2030/31)", "Not a prediction", "Scenarios: trend continues vs levels off; band widened ~4 points a year (indicative)"],
], [40, 34, 96])

P("6.5 Forward forecast", "h2")
P("Forward forecasts use GMP's force total, which is complete up to June 2026 (21 quarters), then take Wigan's "
  "share. Wigan's share of borough crime has been stable at 10.0–10.6% (10.57%, 10.04%, 10.34%, 10.05% in "
  "2021/22–2024/25); the mean of the last two years, 10.20%, is used. Rates assume Wigan's population keeps "
  "growing at its 2020–2025 average of 1.15% a year.")
chart("05b_forward.png", "Figure 7. Wigan: actual, 2025/26 estimate, and forecast to 2030/31.")
table([
    ["Year", "Type", "GMP total", "Wigan crimes", "Wigan per 1,000", "Range (per 1,000)"],
    ["2026/27", "Forecast", "311,829", "31,791", "90.6", "87.8–93.3 (±3%)"],
    ["2027/28", "Forecast", "307,865", "31,389", "88.4", "82.2–94.6 (±7%)"],
    ["2028/29", "Scenario", "304,215", "31,017", "86.4", "Scenarios 84.2–88.9"],
    ["2029/30", "Scenario", "300,854", "30,672", "84.4", "Scenarios 81.6–87.9"],
    ["2030/31", "Scenario", "297,761", "30,357", "82.6", "Scenarios 79.1–86.9"],
], [20, 22, 28, 28, 30, 42], caption="Table 14. Ensemble forecast (55% damped, 45% no trend). Scenario ranges show "
                                     "the gap between the two assumptions, not full uncertainty, which is at least as wide as year 2.")
P("Two cautions. Counts barely fall (about 1% a year); much of the falling <i>rate</i> comes from the assumed "
  "population growth. And 82.6 in 2030/31 should not be compared with today's national rate, because the "
  "national rate will also change and has not been forecast.")
P("6.6 A prospective test", "h2")
P("The forecast was saved on 22 October 2026, before the next release. The January 2027 Home Office release will "
  "add July–September 2026. <b>The forecast for GMP's total that quarter is 79,841</b> (expected within about "
  "±3%, roughly 77,400–82,200). This is a test nobody has seen the answer to, and the result will be published "
  "alongside this report. If the Home Office later reassigns the unassigned crimes, Wigan's true 2025/26 figure "
  "will also become a direct test of the estimates in Table 12.")


# =============================================================================
# 7. Limitations
# =============================================================================
P("7. Limitations", "h1")
table([
    ["Limitation", "Effect", "How it was handled"],
    ["Recorded crime is not actual crime", "Depends on reporting and police recording", "Same-force comparisons favoured; recording caveat stated; cross-force differences treated with caution"],
    ["No street-level or time-of-day data for GMP", "Cannot assess the town centre or night-time", "Stated as out of scope; borough level only"],
    ["Unassigned crimes from late 2025", "2025/26 borough figures understated", "2024/25 used for comparison; 2025/26 estimated two ways"],
    ["Sharing out unassigned crimes assumes they resemble assigned ones", "Estimates could be biased if not", "Not yet tested (offence mix of unassigned crimes could be compared)"],
    ["GMP recording changes 2020–2022", "Inflates the 2021–23 rise", "Shaded on charts; comparisons from 2022/23 preferred"],
    ["Short series (16–21 quarters)", "Wide uncertainty; overlapping test windows", "Simple models; baseline; rolling CV; measured error bands"],
    ["Choices made after viewing results", "Optimistic evaluation of the ensemble", "Disclosed; single model kept as primary result"],
    ["Wigan forecast uses a fixed share", "Share variation (±3%) not in the band", "Share shown to be stable; noted"],
    ["Population growth assumed", "Affects future rates", "Stated; counts shown alongside rates"],
    ["Deprivation comparison excludes Kent, Humberside and some districts", "Mostly rural, less deprived areas missing", "Metropolitan comparison unaffected"],
    ["Fraud and anti-social behaviour excluded", "Not a complete picture of harm", "Standard practice; stated in definitions"],
], [52, 50, 68])

# =============================================================================
# 8. Conclusions
# =============================================================================
P("8. Conclusions", "h1")
bullets([
    "<b>Q1.</b> Wigan's recorded crime rate (91.9 per 1,000 in 2024/25) is above the national average, below "
    "the Greater Manchester average, the 3rd lowest of the ten boroughs, and has fallen faster than the national "
    "rate since 2021/22.",
    "<b>Q2.</b> The difference from the national rate comes from violence, public order and criminal damage. "
    "Theft and robbery are well below average. These are also the categories most affected by GMP's recording "
    "improvements.",
    "<b>Q3.</b> Compared with similar urban, similarly deprived boroughs, Wigan is close to typical (+5%, 12th of "
    "36). The largest differences between places follow police force boundaries.",
    "<b>Q4.</b> A model trained before 2025/26 predicted GMP's total to within 3.4%. Wigan's rate is expected to "
    "ease slowly: about 90.6 in 2026/27 and 88.4 in 2027/28. Beyond two years only scenarios are justified.",
])
P("Two data problems were found along the way: GMP's absence from police.uk since 2019, and the collapse of "
  "borough coding in late 2025. Both limit what residents can find out about crime where they live. Raising the "
  "second with the Home Office crime statistics team, or through a Freedom of Information request to GMP, would "
  "help establish its cause.")

# =============================================================================
# 9. Reproducibility and sources
# =============================================================================
P("9. Reproducibility", "h1")
P(f"All code is published at <font color='#2a78d6'>{REPO}</font>. One command (<font name='DV'>./run_pipeline.sh</font>) "
  "downloads the pinned sources, converts them, and reruns every stage: data preparation, rates and rankings, the "
  "deprivation comparison, model selection, the 2025/26 test, the forward forecast and all charts. The download "
  "stage records a SHA-256 checksum of each file, so you can tell if a source has since been revised. The fitted "
  "forecasting models are saved, with a model card listing their parameters, training data, ensemble weight and "
  "the next check due. A test runs the whole pipeline on synthetic data with the same file layouts.")
P("Note: ONS population estimates and Home Office tables are revised over time, so rerunning later may give "
  "slightly different figures. The checksums show whether that is the cause.", "small")

P("References", "h1")
REFS = [
    "Marsden, L. (2023, 17 February). <i>Wigan isn't as safe as it used to be</i> [opinion column]. Wigan Today. "
    "wigantoday.net/news/opinion/columnists/luke-marsden-wigan-isnt-as-safe-as-it-used-to-be-4028619",
    "Lythgoe, G. (2023, 4 February). <i>Wigan town centre no longer \"Dodge City\" but \"undesirables\" still "
    "causing concern</i>. Wigan Today. wigantoday.net/news/politics/council/wigan-town-centre-no-longer-dodge-city-"
    "but-undesirables-still-causing-concern-4013159",
    "Clarke, G. (2025, 11 September). <i>Wigan bus station stabbings: town centre dispersal order as police stamp "
    "down on crime</i>. Wigan Today. wigantoday.net/news/crime/wigan-bus-station-stabbings-town-centre-dispersal-"
    "order-as-police-stamp-down-on-crime-5313901",
    "Greater Manchester Police (2026, 8 May). <i>Four arrested following disturbance in Wigan town centre</i>. "
    "gmp.police.uk/news/greater-manchester/news/news/2026/may/four-arrested-following-disturbance-in-wigan-town-centre",
    "Greater Manchester Police (2026). <i>Wigan Central: our priorities</i>. "
    "gmp.police.uk/area/your-area/greater-manchester/wigan/wigan-central/on-the-team/our-priorities",
    "Wigan Council (2026, 30 June). <i>Have your say on town centre safety plans</i>. "
    "wigan.gov.uk/News/Articles/2026/June/Have-your-say-on-town-centre-safety-plans.aspx",
    "Greater Manchester Police (2026). <i>FOI 26.016219: Historical street-level crime and stop and search data "
    "for 2023, 2024 and 2025</i>. gmp.police.uk (FOI disclosure log, April 2026)",
    "Home Office (2026). <i>Police recorded crime and outcomes open data tables: Community Safety Partnership, year "
    "ending March 2021 to year ending June 2026</i> (updated 22 October 2026). "
    "gov.uk/government/statistical-data-sets/police-recorded-crime-and-outcomes-open-data-tables",
    "Lees, J. (2026, 24 May). <i>New figures show more crimes reported to police in Wigan including shoplifting "
    "and drug offences</i>. Wigan Today. wigantoday.net/news/crime/new-figures-show-more-crimes-reported-to-police-"
    "in-wigan-including-shoplifting-and-drug-offences-8567438",
    "Greater Manchester Police (2026, 20 February). <i>Neighbourhood crime down and more offenders brought to "
    "justice across Wigan district</i>. gmp.police.uk/news/greater-manchester/news/news/2026/february/"
    "neighbourhood-crime-down-and-more-offenders-brought-to-justice-across-wigan-district",
    "Clarke, G. (2026, 20 February). <i>New figures show fewer crimes reported and more solved by police in "
    "Wigan</i>. Wigan Today. wigantoday.net/news/crime/new-figures-show-fewer-crimes-reported-and-more-solved-by-"
    "police-in-wigan-5604444",
    "Police Professional (2020, 10 December). <i>GMP failing to record one in five of all reported crimes</i>. "
    "policeprofessional.com/?p=130825",
    "Police Professional (2020, December). <i>Greater Manchester Police to be placed in special measures</i>. "
    "policeprofessional.com/news/greater-manchester-police-to-be-placed-in-special-measures",
    "Police Professional (2022, 28 October). <i>Greater Manchester Police removed from special measures</i>. "
    "policeprofessional.com/?p=136785",
    "HM Inspectorate of Constabulary and Fire &amp; Rescue Services. <i>Greater Manchester Police removed from "
    "enhanced monitoring</i>. hmicfrs.justiceinspectorates.gov.uk/news/news-feed/greater-manchester-police-removed-"
    "from-enhanced-monitoring",
    "Guernsey Press (2023, 1 December). <i>Significant improvements by Greater Manchester Police, inspection "
    "finds</i>. guernseypress.com/news/uk-news/2023/12/01/significant-improvements-by-greater-manchester-police-"
    "inspection-finds",
    "Ministry of Housing, Communities and Local Government (2025). <i>English Indices of Deprivation 2025</i>, "
    "File 10 (v2). gov.uk/government/statistics/english-indices-of-deprivation-2025",
    "Office for National Statistics. <i>Mid-year population estimates</i> (Nomis dataset NM_2002_1). nomisweb.co.uk",
    "Office for National Statistics. <i>User guide to crime statistics for England and Wales</i>. ons.gov.uk",
    "Hyndman, R.J. and Athanasopoulos, G. (2021). <i>Forecasting: Principles and Practice</i>, 3rd edition. "
    "OTexts. otexts.com/fpp3",
    "Makridakis, S., Spiliotis, E. and Assimakopoulos, V. (2020). The M4 Competition: 100,000 time series and 61 "
    "forecasting methods. <i>International Journal of Forecasting</i>, 36(1), 54–74.",
    "Smith, J. and Wallis, K.F. (2009). A simple explanation of the forecast combination puzzle. <i>Oxford "
    "Bulletin of Economics and Statistics</i>, 71(3), 331–355.",
]
ref_style = ParagraphStyle("ref", parent=S["bullet"], leftIndent=24, bulletIndent=0, fontSize=8.6, leading=12.4)
for i, r in enumerate(REFS, 1):
    story.append(Paragraph(r, ref_style, bulletText=f"[{i}]"))
story.append(Spacer(1, 8))

P("Glossary", "h2")
table([
    ["Term", "Meaning"],
    ["CSP", "Community Safety Partnership; the area crime is published for, usually the same as the council area"],
    ["Per 1,000", "Crimes divided by residents, times 1,000; allows areas of different sizes to be compared"],
    ["Unassigned", "Crimes GMP recorded without a borough"],
    ["MAPE", "Mean absolute percentage error: on average, how far forecasts missed, in %"],
    ["Holt-Winters", "Exponential smoothing that tracks level, trend and seasonality, weighting recent data more"],
    ["Damped trend", "A trend that fades over time instead of continuing forever"],
    ["Rolling-origin CV", "Testing a forecast from several successive starting points, never using later data to predict earlier"],
    ["Ensemble", "A weighted average of forecasts from more than one model"],
    ["R<super>2</super>", "Share of the differences between areas explained by the line (0 to 1)"],
], [34, 136])

doc = SimpleDocTemplate(str(HERE / "Wigan_Crime_Report_2026.pdf"), pagesize=A4,
                        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=16 * mm,
                        title="Is Wigan's crime high?", author="Pius Ajamma",
                        subject="Wigan recorded crime analysis and forecast, October 2026")
doc.build(story, onFirstPage=page, onLaterPages=page)
print("built")
