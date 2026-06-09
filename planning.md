# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

**An unofficial freshman survival guide for the University of Texas at Austin** — the practical, lived-experience knowledge students pass to each other about housing, dining, studying, getting around, packing, and navigating campus.

This system makes student- and alumni-generated survival advice searchable and answerable: a user asks something like "Which dining hall is all-you-can-eat?" or "Where can I study late at night near campus?" and gets a grounded answer drawn from real student blogs, Her Campus articles, and unofficial guides. This knowledge is hard to find through official channels because the university's own pages (orientation.utexas.edu, housing.utexas.edu) tell you the *rules and logistics* but not the *insider tips* — that J2 is the buffet and Jester City Limits charges per dish, that the dorms are notoriously freezing, that Bennu Coffee is open 24 hours, or that a campus parking permit is jokingly called a "hunting license." That tacit knowledge lives only in what students write for each other, scattered across dozens of blogs, forum threads, and articles that you can't query in plain language.

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

All sources are **unofficial** student/alumni guides (blogs, Her Campus, lifestyle sites) — deliberately *not* the university's own pages, since the goal is the "real" knowledge rather than the official kind. Sources were chosen to cover distinct subtopics (general survival, dorms, dining, study spots, transportation, admissions, orientation, packing) so the corpus answers a range of questions. Some topics are intentionally covered by two sources (study spots, packing) so retrieval can be tested on agreeing-vs-conflicting sources. Each document was cleaned of navigation, ads, and sidebars during ingestion; a source header (site + URL + topic) is kept at the top of every file for citation.

| # | Source | Topic | URL or location |
|---|--------|-------|-----------------|
| 1 | robinmorph (student blog) — "A Freshman's Exhaustive Guide to UT Austin" | General survival (resources, food, housing, jobs, places) | documents/01_freshman_exhaustive_guide.txt — [link](https://robinmorph.wordpress.com/2019/09/02/a-freshmans-exhaustive-guide-to-ut-austin-2019-edition/) |
| 2 | Her Campus (Texas) — "A Comparison of the UT Austin Dorms" | Dorm comparison | documents/02_dorms_comparison.txt — [link](https://www.hercampus.com/school/texas/comparison-ut-austin-dorms/) |
| 3 | Rambler ATX — "Ultimate Guide to UT Austin Meal Plans" | Dining / meal plans | documents/03_meal_plans.txt — [link](https://www.rambleratx.com/resources/guide-ut-austin-meal-plans/) |
| 4 | Rambler ATX — "9 Best Study Spots Near UT Austin" | Study spots (on + off campus) | documents/04_study_spots_campus.txt — [link](https://www.rambleratx.com/resources/best-study-spots-ut-austin/) |
| 5 | Mount Bonnell / Longhorn Life — "10 Best Off-Campus Study Spots" | Off-campus study spots | documents/05_study_spots_offcampus.txt — [link](https://www.mountbonnell.info/longhorn-life/10-best-places-to-study-off-campus-in-austin) |
| 6 | Tex Admissions — "Sensible Advice for Freshmen and Sophomores" | Admissions / pre-college advice | documents/06_admissions_advice.txt — [link](https://www.texadmissions.com/blog/2025/7/4/advice-for-freshmen-and-sophomores-targeting-ut-austin) |
| 7 | Mount Bonnell / Longhorn Life — "6 Tips for Navigating UT Transportation" | Transportation / getting around | documents/07_transportation.txt — [link](https://www.mountbonnell.info/longhorn-life/6-tips-for-navigating-ut-austins-transportation-options) |
| 8 | Society19 — "10 Things I Wish I Knew Before Orientation" | Orientation / class registration | documents/08_orientation_tips.txt — [link](https://www.society19.com/orientation-at-ut-austin/) |
| 9 | Humans of University — "UT at Austin Packing List" | Dorm packing / move-in | documents/09_packing_list.txt — [link](https://humansofuniversity.com/university-of-texas-at-austin/ut-at-austin-packing-list-move-in-day/) |
| 10 | Her Campus (Texas) — "Your Ultimate Dorm Packing List" | Dorm packing essentials | documents/10_dorm_packing_essentials.txt — [link](https://www.hercampus.com/school/texas/your-ultimate-dorm-packing-list/) |

> Collection note: ~4 candidate sources (a 2019 alumni list, Prked guides, BurntXOrange) returned 403/404 to the fetcher and were dropped. Reddit threads were not directly fetchable. This is a real constraint of API-based collection worth recording for the README.

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | At the dining halls, how should I pay to get a discount, and why do students say to avoid Jester City Limits? | Use **Dine-In Dollars** rather than cash/credit for a UT discount of about **$3 per meal**. Jester City Limits charges **per dish**, so students recommend going one floor up to **J2**, the all-you-can-eat buffet, instead. *(doc 01)* |
| 2 | How much does the optional Flex Meal Plan cost and what do you get? | **$500 per semester.** It replaces the unlimited dining-hall meals with **$1,750 Dine In Dollars + $100 Bevo Pay per term**. *(doc 03)* |
| 3 | Where can I study late at night near campus? | Multiple sources: **Bennu Coffee** (open 24 hours, lots of outlets), **PCL / Perry-Castañeda Library** (open nearly 24/7, has a coffee shop), and **Lola Savannah** (open until 11pm); dorm study lounges are also an option. *(docs 01, 04, 05)* |
| 4 | Are the UT dorms cold, and what should I pack because of it? | Yes — the dorms are notoriously **freezing/over-air-conditioned** despite the Texas heat; students recommend bringing **an extra blanket or sweatshirt**, and a **jacket for the aggressively over-cooled auditoriums**. *(docs 08, 01)* |
| 5 | *(Deliberate failure case — answer absent but topically adjacent)* How do I appeal or contest a parking ticket at UT Austin? | **Not covered by the corpus.** The transportation document explains shuttles, R/S/C permits, biking rules, and rideshare — but nothing about contesting/appealing a citation. A correct system should say the documents don't contain this. The likely failure: the parking-permit chunk is highly similar to the query, so retrieval returns it and the LLM may hallucinate an appeals process from it. |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
