# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

**An unofficial freshman survival guide for the University of Texas at Austin** — the practical, lived-experience knowledge students pass to each other about housing, dining, studying, getting around, packing, and navigating campus.

A user asks something like *"Which dining hall is all-you-can-eat?"* or *"Where can I study late at night?"* and gets a grounded answer drawn from real student blogs, Her Campus articles, and unofficial guides. This knowledge is hard to find through official channels because the university's own pages (orientation.utexas.edu, housing.utexas.edu) tell you the *rules and logistics* but not the *insider tips* — that J2 is the buffet while Jester City Limits charges per dish, that the dorms are notoriously freezing, that Bennu Coffee is open 24 hours, or that a campus parking permit is jokingly called a "hunting license." That tacit knowledge lives only in what students write for each other, scattered across dozens of blogs and articles you can't query in plain language.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

All 10 sources are **unofficial** student/alumni guides — deliberately *not* the university's own pages, since the goal is the "real" knowledge. They cover distinct subtopics so the corpus answers a range of questions, with two topics (study spots, packing) intentionally double-covered to test retrieval on agreeing sources. Each file was cleaned of nav/ads and keeps a source header (site + URL + topic) for citation.

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | robinmorph — "A Freshman's Exhaustive Guide to UT Austin" | Student blog | `documents/01_freshman_exhaustive_guide.txt` · [link](https://robinmorph.wordpress.com/2019/09/02/a-freshmans-exhaustive-guide-to-ut-austin-2019-edition/) |
| 2 | Her Campus (Texas) — "A Comparison of the UT Austin Dorms" | Student publication | `documents/02_dorms_comparison.txt` · [link](https://www.hercampus.com/school/texas/comparison-ut-austin-dorms/) |
| 3 | Rambler ATX — "Ultimate Guide to UT Austin Meal Plans" | Off-campus housing blog | `documents/03_meal_plans.txt` · [link](https://www.rambleratx.com/resources/guide-ut-austin-meal-plans/) |
| 4 | Rambler ATX — "9 Best Study Spots Near UT Austin" | Off-campus housing blog | `documents/04_study_spots_campus.txt` · [link](https://www.rambleratx.com/resources/best-study-spots-ut-austin/) |
| 5 | Mount Bonnell / Longhorn Life — "10 Best Off-Campus Study Spots" | Off-campus housing blog | `documents/05_study_spots_offcampus.txt` · [link](https://www.mountbonnell.info/longhorn-life/10-best-places-to-study-off-campus-in-austin) |
| 6 | Tex Admissions — "Sensible Advice for Freshmen and Sophomores" | Admissions-consultant blog | `documents/06_admissions_advice.txt` · [link](https://www.texadmissions.com/blog/2025/7/4/advice-for-freshmen-and-sophomores-targeting-ut-austin) |
| 7 | Mount Bonnell / Longhorn Life — "6 Tips for Navigating UT Transportation" | Off-campus housing blog | `documents/07_transportation.txt` · [link](https://www.mountbonnell.info/longhorn-life/6-tips-for-navigating-ut-austins-transportation-options) |
| 8 | Society19 — "10 Things I Wish I Knew Before Orientation" | Student lifestyle site | `documents/08_orientation_tips.txt` · [link](https://www.society19.com/orientation-at-ut-austin/) |
| 9 | Humans of University — "UT at Austin Packing List" | Student site | `documents/09_packing_list.txt` · [link](https://humansofuniversity.com/university-of-texas-at-austin/ut-at-austin-packing-list-move-in-day/) |
| 10 | Her Campus (Texas) — "Your Ultimate Dorm Packing List" | Student publication | `documents/10_dorm_packing_essentials.txt` · [link](https://www.hercampus.com/school/texas/your-ultimate-dorm-packing-list/) |

*Collection note:* ~4 candidate sources (Prked, BurntXOrange, a 2019 alumni list) returned HTTP 403/404 to the fetcher and were dropped, and Reddit threads weren't directly fetchable — a real constraint of API-based collection.

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Approach: semantic chunking.** Each document body is split into sentence-like units (structural `=== headers ===` and list items kept whole; prose split into sentences). Every unit is embedded with the same model used for retrieval, and a chunk **boundary** is cut wherever the cosine distance between adjacent units exceeds the **90th percentile** of distances within that document — i.e., where the topic visibly shifts.

**Chunk size:** Variable by design, bounded by guardrails — **max ~180 words (~256 tokens)** because `all-MiniLM-L6-v2` truncates input past 256 tokens, and **min ~40 words** (smaller pieces merged into a neighbour). Actual sizes: min 50 / median 96 / max 172 words.

**Overlap:** None in the fixed-window sense — boundaries fall at natural topic shifts, so facts aren't cut mid-thought. Instead of lexical overlap, **each chunk is prepended with its source + topic header** (e.g. `[Source: Her Campus | Topic: Dorms]`) so a bare bullet still carries provenance and powers citation.

**Preprocessing before chunking:** split the `Key: value` source header from the body, `html.unescape()` entities, strip stray HTML tags, collapse blank-line runs. A refinement added after inspecting output: a section header always *starts* a new chunk so a `=== Bicycling ===` title is never stranded from its content; and guardrails run merge-first/split-last so the 180-word cap is a hard guarantee.

**Why these choices fit your documents:** The corpus is heterogeneous — long-form guides with many sub-topics (doc 01 spans resources → food → housing → jobs) mixed with lists of atomic facts (one dorm or study spot per bullet). A fixed window would cut a dorm's description in half; one-chunk-per-document would bury "J2 is the buffet" in a 2,000-word blob. Semantic chunking adapts the boundary to the content.

**Final chunk count:** **42** across 10 documents. (Just under the "50" rule of thumb, but a percentile sweep showed the corpus tops out near 45 — these are short blog posts, not long handbooks, and a median of ~96 words is already a healthy self-contained thought.)

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` — local, no API key, 384-dim vectors, fast on CPU. The same model embeds sentences during chunking, chunks at index time, and the query at search time, so everything shares one vector space. Chunks are stored in a local **ChromaDB** collection configured for **cosine** distance.

**Production tradeoff reflection:** If deployed for real students and cost weren't a constraint, I'd weigh:
- **Domain accuracy:** a larger model (OpenAI `text-embedding-3-large`, Voyage, Cohere) would likely retrieve better on slangy, abbreviation-heavy student writing ("J2", "the Drag", "PCL") — worth A/B-testing against MiniLM on the eval set before paying for it.
- **Context length:** MiniLM's 256-token cap forces small chunks; a long-context model (8k+ tokens) could embed a whole section as one vector, simplifying chunking, at higher cost/latency.
- **Latency & local vs. API:** local MiniLM has zero per-query cost, no network hop, and keeps data private — ideal for a student tool. An API model adds latency/cost but offloads compute and auto-upgrades. I'd keep embeddings local unless retrieval quality measurably needed the upgrade.
- **Multilingual:** not needed here (English-only), but international-student forums would call for a multilingual model.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction** (verbatim, from `generate.py`):
> You are The Unofficial Guide, a question-answering assistant for University of Texas at Austin students. Answer the question using ONLY the information in the context documents provided by the user. Rules:
> - Use only facts stated in the context. Do NOT use outside or prior knowledge.
> - Do NOT guess, extrapolate, or add general advice.
> - If the context does not contain enough information to answer, reply with EXACTLY this sentence and nothing else: "I don't have enough information on that."
> - Otherwise, answer concisely and cite the source filename(s) you used in parentheses.

**Structural grounding (not just the prompt):**
- The model runs at **temperature 0** and only ever sees the retrieved chunks, formatted as labeled blocks (`(source: <filename>)` + chunk text).
- A **relevance gate**: only chunks with cosine distance < 0.5 are passed as context. If *none* qualify, the system declines deterministically **without even calling the LLM** — this is what makes an uncovered question (e.g. appealing a parking ticket) impossible to answer from training knowledge.

**How source attribution is surfaced in the response:** Sources are built **programmatically** from the retrieved chunks' metadata (the unique source filenames of the relevant chunks, in rank order) — not left to the LLM to invent. They're returned with the answer and shown in the Gradio "Retrieved from" panel. When the system declines, the sources list is empty.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

Run with `python test_retrieval.py` (retrieval) and `python generate.py` (end-to-end).

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How to pay for a dining discount, and why avoid Jester City Limits? | Use Dine-In Dollars (~$3/meal discount); JCL charges per dish, use the J2 buffet one floor up | Said exactly that — Dine-In Dollars for the ~$3 discount; avoid JCL (per-dish), use J2 buffet. Cited `01_…guide.txt` | Relevant (top 0.231) | **Accurate** |
| 2 | How much is the Flex Meal Plan and what do you get? | $500/sem; $1,750 Dine In Dollars + $100 Bevo Pay per term | "$500 per semester … $1,750 Dine In Dollars and $100 Bevo Pay per term." Cited `03_meal_plans.txt` | Relevant (top 0.379) | **Accurate** |
| 3 | Where can I study late at night near campus? | Bennu Coffee (24h), PCL (~24/7), Lola Savannah (until 11pm) | Gave SUREWalk/late-night Lyft + listed campus libraries; noted "the context does not specify 24-hour libraries." Missed Bennu/PCL. Cited `01_…guide.txt` | Partially relevant (best chunk buried at #10) | **Partially accurate** |
| 4 | Are the dorms cold, and what should I pack? | Yes, notoriously freezing; bring a blanket/sweatshirt (+ jacket for over-cooled auditoriums) | "Yes, the UT dorms are cold. Pack warm clothing, such as an extra blanket or a sweatshirt." Cited `08_…tips.txt`, `10_…packing.txt` | Relevant (top 0.370) | **Accurate** (omits auditorium-jacket detail) |
| 5 | How do I appeal a parking ticket at UT Austin? | *Not in the corpus* — system should decline | "I don't have enough information on that." No sources. | Off-target by design (all > 0.63) | **Accurate** (correct refusal) |

**Summary:** 3 accurate, 1 partially accurate (Q3, analyzed below), 1 correct refusal (Q5, the planted out-of-scope case).

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Q3 — *"Where can I study late at night near campus?"*

**What the system returned:** A grounded but **partially-correct** answer about SUREWalk escorts and late-night Lyft rides, plus a list of campus libraries, with an honest caveat that "the context does not specify 24-hour libraries." It never surfaced the genuinely correct answers: **Bennu Coffee (open 24 hours, explicitly "ideal for late-night study")**, PCL ("open nearly 24/7"), or Lola Savannah (until 11pm).

**Root cause (tied to specific pipeline stages):** This is a *retrieval* failure with two compounding causes.
1. **Chunking dilution.** The best answer — "Bennu Coffee … open 24 hours … Ideal for late-night study sessions" — sits as item #1 inside `05_study_spots_offcampus.txt`'s 186-word, 8-cafe list chunk. Because semantic chunking kept the list together, that chunk's embedding is the *average* of eight cafes, so the strong "24 hours / late-night study" signal is blurred. It ranks **#10 (distance 0.579)** — outside the top-5.
2. **Query-term semantic collision.** "Late at night" best matches a chunk in `01_…guide.txt` that literally says "SUREWalk … 8pm-2am" and "Free Lyft rides … late at night" — *transport* services, not study spots — so that retrieves at the top (0.422).

Generation then did its job correctly: it answered only from the (wrong-but-retrieved) context and refused to invent Bennu. The failure is upstream — **bad chunks the LLM couldn't compensate for**, exactly as the project warns.

**What you would change to fix it:**
- **Chunk lists at the item level** (one cafe per chunk) so "Bennu — open 24 hours" gets its own embedding and ranks on its own merits.
- **Add hybrid keyword/BM25 search** so the co-occurrence of "study" + "late" boosts the study-spots list above the transport chunk (the Hybrid Search stretch feature).
- Or **increase top-k / add MMR diversity** so a second-choice document like `05_…` can surface.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

> *Personalize these in your own voice before submitting — they're your reflection.*

**One way the spec helped you during implementation:**  The most useful thing I wrote in planning was the note that all-MiniLM cuts off at 256 tokens. When I actually built the chunker I almost forgot about it, but because it was sitting right there in my spec I added the 180-word cap before I ran anything — so I never hit the silent-truncation bug I would've otherwise spent an hour debugging.

**One way your implementation diverged from the spec, and why:** My plan said 'pure semantic chunking' — split on meaning, full stop. But when I printed the chunks to eyeball them, one started with 'Cost-effective and eco-friendly' with no idea it was about biking — the === Bicycling === header had been chopped onto the previous chunk. That's when it clicked that my documents aren't just prose; they have structure the spec ignored. So I broke from the plan and made section headers always start a new chunk. The lesson: I couldn't have written that rule up front — I only saw the need once I looked at real output.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

> *Verify/personalize these against your own recollection before submitting.*

**Instance 1 — semantic chunking implementation**

- *What I gave the AI:* my **Chunking Strategy** and **Documents** sections from `planning.md` (semantic chunking, 90th-percentile cosine boundary, ~180-word cap, header-prepend) plus the `Key: value` header format my `.txt` files use.
- *What it produced:* `ingest.py`, `chunking.py`, and `build_chunks.py` — a loader and semantic chunker with a stats/inspection step.
- *What I changed or overrode:* I chose semantic chunking over the structure-aware approach it first recommended. After reading the printed chunks I directed two fixes I spotted — the stranded-section-header problem and a guardrail-ordering bug that produced a 209-word chunk — and verified the final numbers (42 chunks, none empty/oversized/undersized) myself rather than trusting the first run.

**Instance 2 — grounded generation**

- *What I gave the AI:* my **Anticipated Challenges** section (the grounding/hallucination risk on the parking-ticket query) and the requirement that every answer cite its source document(s).
- *What it produced:* `generate.py` with the strict grounding system prompt, the exact Writingdecline sentence, and programmatic source attribution from chunk metadata.
- *What I changed or overrode:* I had it add a **relevance gate** (skip the LLM and decline when no chunk is below the distance threshold) so the uncovered-question case can't hallucinate, instead of relying on the prompt alone — then tested the parking-ticket query end-to-end to confirm it declines with no sources.
