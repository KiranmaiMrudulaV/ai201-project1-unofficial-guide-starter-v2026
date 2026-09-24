# The Unofficial Guide

**Kiranmai Mrudula Vardhiboyina** — corpus: `campus_life`

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

This is a retrieval-augmented question-answering system built on `campus_life`,
a corpus of 88 short, student-written posts about dorms, dining halls,
courses, and administrative policies at a fictional university. Ask it a
specific question — like how long the wait is at a particular dining hall,
what a course's workload looks like, or whether work-study income counts
against financial aid — and it retrieves the most relevant posts, answers
using only what's in them, and names the source file(s) it pulled from. If a
question falls outside what the corpus covers, it says so instead of
guessing.

## Chunking Strategy

**Chunk size:** 600 characters
**Overlap:** 80 characters

`campus_life` is 88 short, single-topic posts — mostly 1 to 3 short
paragraphs, ranging from about 178 to 549 characters when I checked with
`python app.py chunks -n 1`. The default 800-character fixed-window chunker
barely touched this corpus (88 documents in, 88 chunks out) because almost
nothing reaches 800 characters, but that was an accident of the number, not a
deliberate choice — the old chunker would still cut a longer document
mid-sentence with no regard for paragraph breaks.

I replaced it with a paragraph-aware chunker (`chunker.py::split_documents`):
it splits each document into paragraphs, then groups consecutive paragraphs
into a chunk up to 600 characters — chosen because it's comfortably above the
longest document I observed (549 characters), so every document still stays
as one complete chunk by design. Only a document that actually exceeded 600
characters would get split, and only at a paragraph boundary, never
mid-sentence. When a split does happen, the last 80 characters of the
previous chunk carry over so the next chunk isn't missing context.

Re-indexing with the new chunker still produced 88 chunks from 88 documents —
the same count as before, but now that's a real, measured decision (chunk
size chosen above the observed maximum document length) instead of a
coincidence of a generic default.

## Sample Chunks

`python app.py chunks -n 5` output, spread across the corpus.

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology

I lived here my sophomore year. Format is lecture three times a week with a weekly lab. Assessment: four unit tests and a cumulative final. Not curved.

Expect 9 to 11 hours a week, the heaviest first-year course by reputation.

The one piece of advice: the unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_hist_118_workload.txt#0` — produced by: `chunker.py::split_documents`

```
Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```

**Chunk 4** — source: `dining_pellew_dining_hall_followup.txt#0` — produced by: `chunker.py::split_documents`

```
Re: Pellew Dining Hall

Adding to what people have said about Pellew Dining Hall. The wait figure of 12 to 18 minutes at peak matches what I've seen. If you're trying to eat between classes, go before 11:45 and it's a different building entirely.

Also worth saying: the furthest hall from anywhere, next to the athletics centre. Nobody tells you this at orientation.
```

**Chunk 5** — source: `housing_innisfree_hall.txt#0` — produced by: `chunker.py::split_documents`

```
Innisfree Hall — what it's actually like

Transferred in last year, so take this with a grain of salt. Built 1991, renovated 2022. Rooms are doubles arranged as pairs sharing one bathroom between two rooms.

The good: the shared-bathroom-between-two-rooms arrangement is the best compromise on campus.

The bad: no air conditioning, which matters for the first three weeks of September.

Laundry costs $1.75 wash, $1.75 dry, app-based. On noise: moderate; the building is L-shaped and the short wing is much quieter.
```

## Sample Answer

**Question:** What's the wait time at Kestrel Commons during the lunch rush?

**Answer:**

```
The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00.
This information comes from the documents `dining_kestrel_commons.txt` and
`dining_kestrel_commons_followup.txt`.

Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt,
dining_kestrel_commons_followup.txt, dining_pellew_dining_hall_followup.txt,
dining_the_ridgeway_cafe_followup.txt
```

**My relevance cutoff:** 0.6 (the default — kept as-is, see reasoning below)

I ran my 5 in-corpus test questions and the 5 `OUT_OF_SCOPE` questions through
`python app.py retrieve` and recorded the best (lowest) distance for each.
There's a clean gap with no overlap: in-corpus questions top out at 0.375,
out-of-scope questions start at 0.825. A cutoff of 0.6 sits comfortably in the
middle of that gap, so I left it at the default rather than moving it.

| Question | In corpus? | Best distance |
|---|---|---|
| Does work-study income count against financial aid the same way a regular campus job does? | Yes | 0.156 |
| How many hours a week does MATH 220 typically take, and is the workload even across the semester? | Yes | 0.316 |
| What's the wait time at Kestrel Commons during the lunch rush? | Yes | 0.197 |
| By what time does The Atrium get picked clean, and when does it restock? | Yes | 0.375 |
| Which floors in Aldridge Hall are enforced as quiet floors? | Yes | 0.302 |
| What is the capital of Mongolia? | No | 0.825 |
| How do I change the oil in a diesel engine? | No | 0.934 |
| Who won the 1994 World Cup? | No | 0.886 |
| What is the recommended dosage of ibuprofen for a headache? | No | 0.844 |
| How do I write a for loop in Rust? | No | 0.896 |

## How I Used AI

**1.** I asked Claude to help draft my 5 test questions after reading through
the `campus_life` document filenames. Its first pass proposed 5 questions
covering housing, quiet floors, printing quota, the campus shuttle, and one
dining hall. I didn't like that spread — I wanted more coverage of dining
halls, course workload, and financial aid specifically — so I asked it to
swap those topics in. It came back with a revised set (work-study vs.
financial aid, MATH 220 workload, two separate dining-hall questions, and
Aldridge Hall noise), which is what ended up in `questions.py`.

**2.** When drafting criterion 4 (about chunk quality), Claude walked me
through turning my vague instinct — "chunks shouldn't cut off before giving
the whole picture" — into a testable target. When it first asked me to pick
numbers, I went with a cautious "4 of 5" chunks reading as a complete
thought. After thinking about *why* — that my documents are short and
single-topic and a boundary-respecting chunker should split cleanly every
time — I changed it to a stricter 5 of 5, since I couldn't come up with a
real reason to expect a failure.

**3.** In Unit 2, after all 5 criteria came back MET with no misses, I asked
Claude to help me figure out which one to name as "too easy" rather than
just guessing. It compared all 5 against each other and argued specifically
for criterion 3, using my own words against it: my `criteria.md` reasoning
for that criterion said I was leaving room for a miss "in case a future
out-of-scope question... lands closer to the boundary than the five I
tested" — but my actual 5 `OUT_OF_SCOPE` questions were nowhere near that
boundary. It then proposed 5 concrete boundary-adjacent questions (things
that sound plausible for `campus_life` but aren't covered) to actually test
that gap. Running them found a real weakness I hadn't noticed — 3 of the 5
got past the gate and only the generation prompt caught them. I didn't
change anything about its suggested questions; I asked it to run them
because I wanted to see whether the argument held up against real data, and
it did.

## Stretch Features

I'm adding three stretch features: **metadata filtering**, **conversational
memory**, and **a second embedding model**.

### Metadata filtering

Every `campus_life` filename follows a consistent `topic_restofname.txt`
pattern (`admin_...`, `course_...`, `dining_...`, `housing_...`, etc.), so I
derive a `category` from the filename prefix at index time
(`store.py::category_of`) and store it as Chroma metadata on every chunk.
`search()` takes an optional `category` argument and passes it through as a
`where` clause; the CLI exposes it as `--category` on both `retrieve` and
`ask`.

**Same query, with and without the filter:**

`python app.py retrieve "What costs money here that people don't expect?"`

```
1   0.6984     admin_printing_quota.txt
2   0.7043     housing_calder_annexe.txt
3   0.7752     housing_fenwick_court.txt
4   0.7865     housing_aldridge_hall.txt
5   0.7972     money_textbooks.txt
```

`python app.py retrieve "What costs money here that people don't expect?" --category housing`

```
1   0.7043     housing_calder_annexe.txt
2   0.7752     housing_fenwick_court.txt
3   0.7865     housing_aldridge_hall.txt
4   0.8030     housing_old_brewhouse.txt
5   0.8033     housing_innisfree_hall.txt
```

**What changed:** unfiltered, the top result is `admin_printing_quota.txt`
and `money_textbooks.txt` also makes the top 5. Filtered to `housing`, both
of those drop out entirely and the list fills back out with the next-closest
housing documents instead — the filter is genuinely restricting the search
space, not just re-sorting the same five results.

### Conversational memory

The interactive `ask` loop (`python app.py ask` with no question argument)
now tracks the previous turn's question and answer. Two things use it: the
retrieval query becomes `f"{previous_question} {question}"` (so a follow-up
that doesn't repeat the topic can still retrieve the right chunks), and
`generate.py::build_prompt` prepends the previous Q&A to the model's prompt
as context, while the grounding instruction still requires the actual answer
to come from the retrieved documents, not from the prior answer's text.

**Two-turn exchange, same session:**

```
> What's the wait time at Kestrel Commons during the lunch rush?
  (best distance 0.197, cutoff 0.6)

The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00.
This information comes from the documents `dining_kestrel_commons.txt` and
`dining_kestrel_commons_followup.txt`.

> What are the hours on weekends?
  (best distance 0.250, cutoff 0.6)

The hours on weekends for Kestrel Commons are 9:00am to 8:00pm. This comes
from the document `dining_kestrel_commons.txt`.
```

The second question never says "Kestrel Commons" — on its own it would be
retrieval-ambiguous (every dining hall has weekend hours). The answer is
correct only because the retrieval query and the prompt both carried the
first turn's context forward.

### A second embedding model

I installed `sentence-transformers` and swapped `EMBEDDING_MODEL` in
`config.py` from the bundled `all-MiniLM-L6-v2` (384 dimensions) to
`all-mpnet-base-v2` (768 dimensions, generally a stronger sentence-embedding
model), indexed it into a separate `--variant mpnet` so the original index
stays untouched, then ran the same 10 questions from Milestone 4 against
both.

| Question | In corpus? | MiniLM distance | mpnet distance | Moved |
|---|---|---|---|---|
| Work-study vs financial aid | Yes | 0.156 | 0.111 | closer |
| MATH 220 workload | Yes | 0.316 | 0.306 | closer (slightly) |
| Kestrel Commons wait time | Yes | 0.197 | 0.202 | farther (slightly) |
| The Atrium restock time | Yes | 0.375 | 0.451 | farther |
| Aldridge Hall quiet floors | Yes | 0.302 | 0.185 | closer |
| Capital of Mongolia | No | 0.825 | 0.813 | closer (slightly) |
| Diesel oil change | No | 0.934 | 0.816 | closer |
| 1994 World Cup | No | 0.886 | 0.913 | farther |
| Ibuprofen dosage | No | 0.844 | 0.852 | farther (slightly) |
| Rust for-loop | No | 0.896 | 0.792 | closer |

**What moved:** mpnet pulled several out-of-scope questions closer to 0
(diesel oil change: 0.934 → 0.816; Rust for-loop: 0.896 → 0.792) — it seems
to spread distances less aggressively overall than MiniLM does on this
corpus. It also pushed one in-corpus question farther away (The Atrium:
0.375 → 0.451). Net effect: the in-corpus/out-of-scope gap narrowed from
[0.375, 0.825] (width 0.450) under MiniLM to [0.451, 0.792] (width 0.341)
under mpnet. My existing threshold of 0.6 still happens to sit inside the
narrower gap, so I didn't have to move it for this specific set of 10
questions — but the margin for error is smaller, and a corpus where mpnet's
gap doesn't happen to straddle 0.6 would need a real re-measurement, not an
assumption that the same cutoff carries over.

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

Produced by `python run_eval.py --label before` (`results/run_2026-09-23_1936.md`,
the scored run — two earlier attempts in `results/` predate a working
`scorer.py` and are unscored), plus `python app.py chunks -n 5` for
criterion 4, which isn't exercised by `run_eval.py` at all. Criteria 3 and 4
are each measured in one deterministic pass rather than three — the gate is
a comparison against a fixed number, and the chunker produces the same
chunks every time — so the same number goes in all three run columns for
those two.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Cited sources actually contain the answer | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

**Real output, one per criterion:**

**Criterion 1** — `store.py::search`, retrieval for "What's the wait time at Kestrel Commons during the lunch rush?":
```
Best distance: 0.1967 (passed the gate)
Sources retrieved: dining_halden_hall_followup.txt, dining_kestrel_commons.txt,
dining_kestrel_commons_followup.txt, dining_pellew_dining_hall_followup.txt,
dining_the_ridgeway_cafe_followup.txt
```
Opened `dining_kestrel_commons.txt` directly and confirmed "20 to 25 minutes"
is written there — the top retrieved chunk genuinely contains the answer.

**Criterion 2** — `generate.py::answer_from_chunks`, answer for the same question:
```
The wait time at Kestrel Commons is 20 to 25 minutes between 12:15 and 1:00.
This information comes from the documents `dining_kestrel_commons.txt` and
`dining_kestrel_commons_followup.txt`.
```
Source named explicitly, every run.

**Criterion 3** — `run_eval.py::check_out_of_scope` + `gate.py::check`:
```
What is the capital of Mongolia? | 0.825 | refused
How do I change the oil in a diesel engine? | 0.934 | refused
Who won the 1994 World Cup? | 0.886 | refused
What is the recommended dosage of ibuprofen for a headache? | 0.844 | refused
How do I write a for loop in Rust? | 0.896 | refused
```
5 of 5 refused, cutoff 0.6.

**Criterion 4** — `chunker.py::split_documents`, from `python app.py chunks -n 5`:
```
Chunk 3 | source: course_hist_118_workload.txt#0 | produced by: chunker.py::split_documents

Workload for HIST 118 Modern World History

People keep asking so: a lot of reading, about 120 pages a week, but no problem sets. That's real time, not optimistic time.

It's front-loaded — the first month is heavier than the rest, partly because you're learning the format.
```
Reads as a complete thought — no sentence cut off at either end. Same for
the other 4 sampled chunks.

**Criterion 5** — for "How many hours a week does MATH 220 typically take,
and is the workload even across the semester?":
```
MATH 220 typically takes 6 to 8 hours a week, and the workload is
front-loaded, meaning the first month is heavier than the rest (source:
`course_math_220_workload.txt` and `course_math_220.txt`).
```
Opened `course_math_220_workload.txt` and confirmed both "6 to 8 hours" and
"front-loaded" are genuinely written there, not just topically adjacent.

## Verdicts

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | Opened the actual source file for each of my 5 questions and confirmed the fact was genuinely present in the top retrieved chunk. 5/5, stable across all 3 runs since retrieval is deterministic — clears the 4/5 target. |
| 2 | Every answer names a source | MET | Read all 15 answer instances (5 questions × 3 runs) in the run log; every one names an explicit filename. 5/5 every run. |
| 3 | Gate stops out-of-corpus questions | MET | All 5 `OUT_OF_SCOPE` questions were refused (best distances 0.825–0.934, all above the 0.6 cutoff). 5/5 clears the 4/5 target. |
| 4 | Chunks read as complete thoughts | MET | Sampled 5 chunks via `app.py chunks -n 5` and read each one myself — none started or ended mid-sentence. 5/5. |
| 5 | Cited sources actually contain the answer | MET | For each of my 5 questions, opened the specific file(s) the answer cited and confirmed the fact was actually there, not just a plausible-sounding file. 5/5. |

No misses. All 5 targets held on every run, not just most of them — I
checked each one by hand against the actual source documents rather than
trusting the retrieved/cited filenames at face value.

## Diagnoses

No criterion was missed. All 5 held on all 3 runs. Rather than manufacture a
failure that didn't happen, here's an honest read of which target was too
easy, and a harder test that actually finds a real weakness.

**Criterion 3 was the safest target, and I can show why rather than just
assert it.** In `criteria.md`, my stated reason for allowing 1 of 5 misses
was: "I'm leaving room for 1 of 5 in case a future out-of-scope question I
haven't tried lands closer to the boundary than the five I tested." My
actual 5 `OUT_OF_SCOPE` questions (capital of Mongolia, diesel oil changes,
1994 World Cup, ibuprofen dosage, Rust for-loops) are about as far from
campus life as a question can get — nothing close to the boundary I said I
was worried about. So I built and ran a harder test: 5 questions that sound
plausible for `campus_life` but aren't actually covered by any of the 88
documents —

1. "What GPA do I need to make the Dean's list?" — distance 0.564
2. "Is there a shuttle to the airport?" — distance 0.643
3. "Can I get a refund on unused meal swipes?" — distance 0.543
4. "Do any professors offer extra credit at the end of the semester?" — distance 0.531
5. "Is there a bike-share program on campus?" — distance 0.694

**The mechanism, precisely:** with `THRESHOLD = 0.6`, the gate (`gate.py::check`)
only refused 2 of these 5 (0.643 and 0.694) — the other 3 (0.564, 0.543,
0.531) are all under the cutoff, so `gate.py` let them through to the model.
The reason this didn't produce a wrong answer to the user is that the
*second* layer of defense caught it — `generate.py`'s `GROUNDING_INSTRUCTION`
correctly made the model say "I don't have enough information" for all 3,
even with irrelevant chunks in front of it. So end-to-end the user experience
was fine, but the gate itself — which is literally what criterion 3 names —
only did its job 2 of 5 times on this harder test, not 5 of 5. It was riding
on the prompt layer as a safety net rather than actually separating covered
from uncovered questions on its own.

**Tighter target:** at least 4 of 5 boundary-adjacent (plausible but
uncovered) questions refused *by the gate itself*, not by the combined
system. Measured as above, the current system gets 2 of 5 — a miss against
this tighter bar, even though it's a MET against the original criterion 3 as
written.

## The Improvement

**What I changed:** Tuned the relevance gate — lowered `THRESHOLD` in
`config.py` from `0.6` to `0.45`. Nothing else changed: same chunker, same
top-k, same prompt, same embedding model.

**Why I picked it:** Directly follows from the Diagnoses section above. The
mechanism I found was specific to the gate: at 0.6, `gate.py::check` let 3 of
5 boundary-adjacent questions through to the model (distances 0.531–0.564),
relying on the prompt layer to catch what the gate should have caught
itself. My real in-corpus questions never exceed 0.375, so there was room to
lower the cutoff without risking a false refusal — 0.45 sits in the gap
between 0.375 (my highest real distance) and 0.531 (my lowest
boundary-adjacent false-positive), instead of tuning something in the
chunker or prompt that the diagnosis never actually implicated.

### Run Log — After

Produced by `python run_eval.py --label after`
(`results/run_2026-09-23_2053_after.md`), `THRESHOLD = 0.45`, everything
else unchanged from the before run.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 5 of 5 | 5/5 | 5/5 | 5/5 | MET (unaffected — chunker untouched) |
| 5. Cited sources actually contain the answer | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

**Real output, before vs. after, on the 5 boundary-adjacent questions (the
actual target of this fix):**

| Boundary-adjacent question | Distance | Gate @ 0.6 (before) | Gate @ 0.45 (after) |
|---|---|---|---|
| What GPA do I need to make the Dean's list? | 0.564 | let through | **refused** |
| Is there a shuttle to the airport? | 0.643 | refused | refused |
| Can I get a refund on unused meal swipes? | 0.543 | let through | **refused** |
| Do any professors offer extra credit at the end of the semester? | 0.531 | let through | **refused** |
| Is there a bike-share program on campus? | 0.694 | refused | refused |

Gate-only refusal rate on this harder test went from **2 of 5 → 5 of 5**.

**Did it help?** Yes, and I can show it two ways. First, none of the
original 5 criteria regressed — all 5 are still MET, with identical
distances to the before run (`store.py::search` is deterministic; only the
gate's cutoff comparison changed, not retrieval itself). Second, the
specific weakness the diagnosis named is fixed: the gate itself now refuses
all 5 boundary-adjacent questions, instead of needing the prompt layer to
catch 3 of them. The tighter target from Milestone 3 — "4 of 5
boundary-adjacent questions refused by the gate itself" — now reads 5 of 5,
clearing even that stricter bar.

## Second Improvement (Stretch)

**Declaring this before building it, per the stretch rules:** I'm adding a
second measured improvement — hybrid search (BM25 + semantic, via reciprocal
rank fusion) — even though the first improvement already fully closed the
gap it targeted. To do this honestly rather than just tuning something
without a reason, I first expanded the boundary-adjacent test from 5
questions to 12 (one per topic category — admin, course, dining, housing,
money, health, study, orientation, transit), to see whether a real weakness
existed to justify a second fix. All 12 were already refused by the
threshold-tuned gate, but one was fragile: "Is there a fee for booking a
study room?" passed at 0.453, only 0.003 above the 0.45 cutoff — close
enough that a slightly different phrasing could tip it the wrong way. Hybrid
search is aimed at that fragility, not at a confirmed failure.

**What I changed:** Added a `hybrid` option to `store.py::search`
(`_hybrid_rerank`). It pulls a larger semantic candidate pool (20 chunks
instead of 5), reranks them with BM25 keyword-overlap scores using
reciprocal rank fusion, and returns the fused top-k. The distances reported
are still the real cosine distances from Chroma, so the 0.45 threshold stays
comparable. `rank-bm25` was already in `requirements.txt` for this exact
purpose.

**Run Log — After (hybrid):** produced by
`python run_eval.py --label after_hybrid --hybrid`
(`results/run_2026-09-23_2137_after_hybrid.md`), `THRESHOLD = 0.45`,
`hybrid=True`, everything else unchanged.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Chunks read as complete thoughts | 5 of 5 | 5/5 | 5/5 | 5/5 | MET (unaffected — chunker untouched) |
| 5. Cited sources actually contain the answer | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

**The 12-question boundary-adjacent test, semantic-only vs. hybrid:**

| Boundary-adjacent question | Semantic-only | Hybrid | Moved |
|---|---|---|---|
| Dean's list GPA | 0.564 | 0.591 | safer |
| Shuttle to the airport | 0.643 | 0.643 | unchanged |
| Meal swipe refund | 0.543 | 0.543 | unchanged |
| Extra credit | 0.531 | 0.531 | unchanged |
| Bike-share program | 0.694 | 0.694 | unchanged |
| Free flu shots | 0.763 | 0.763 | unchanged |
| **Study room fee (the fragile one)** | **0.453** | **0.453** | **unchanged** |
| Transfer buddy program | 0.710 | 0.737 | safer |
| International students working off campus | 0.472 | 0.472 | unchanged |
| Retaking a final exam | 0.476 | 0.476 | unchanged |
| Dining hall delivery | 0.509 | 0.509 | unchanged |
| Single room as a sophomore | 0.459 | 0.459 | unchanged |

**Did it help?** A little, but not decisively — and I want to say that
plainly rather than round it up. All 12 boundary-adjacent questions and all
5 original criteria still hold with hybrid on, so nothing regressed. 2 of 12
margins genuinely improved (moved further from the 0.45 cutoff). But the one
case I actually built this fix to help — the 0.453 study-room-fee
question — didn't move at all, because BM25 reranking only changes the
*order* of an already-retrieved candidate pool; it doesn't lower the
underlying cosine distance of the closest wrong match, which is what the
gate threshold actually compares against. If I wanted to fix that specific
fragile case, tuning the threshold slightly lower, or improving chunking
around `study_group_rooms.txt` so it embeds less closely to "fee" questions,
would be more direct next steps than reranking.

## What's Still Broken

Nothing is currently missing against the official 5 criteria in
`criteria.md`, and the tighter target I named in Milestone 3 is now also
cleared (5 of 5 boundary-adjacent questions refused by the gate). But "not
currently broken" isn't the same as "fully verified," and I want to be
honest about the gaps in my own testing rather than imply this is bulletproof.

- **Only 5 boundary-adjacent questions were tested**, and I picked them
  myself in one pass. They happened to span admin, transit, dining, and
  housing topics, but I didn't systematically probe every category the
  corpus covers (e.g. courses, money, health, orientation) for its own
  boundary case. There could be a false-positive pattern in a category I
  didn't think to test.
- **All 5 of my original test questions are single-fact lookups** (a number,
  a time, a floor). I haven't tested a question that genuinely requires
  synthesizing 3+ chunks, or a paraphrased version of the same question
  worded very differently, which could stress retrieval and generation in
  ways my current set doesn't.
- **Sample sizes are small everywhere** — "5 of 5" on 5 questions is a
  thinner claim than "50 of 50" would be. A single unlucky question could
  flip a criterion from MET to MISSED next time I test.

What I'd do next: write one boundary-adjacent question per topic category
(7-8 total, not 5 picked ad hoc) and re-run this same test, since that's the
exact gap the current test has. I stopped here because the assignment scope
is one measured improvement, and this one already closed a real, demonstrated
gap without any regressions — chasing a second improvement without a second
diagnosed weakness would be tuning without a reason, which is exactly what
the process this unit is designed to avoid.

## What I'd Do Differently

If I were writing these 5 criteria for the first time again, knowing what I
know now:

**Criterion 3** is the one I'd write differently. The original version ("4
of 5 out-of-corpus questions refused") doesn't say *how* out-of-corpus —
and it turns out that distinction matters a lot. I'd write it from the start
as two-tiered: "4 of 5 *obviously* unrelated questions refused, **and** 4 of
5 *boundary-adjacent* (plausible-sounding but uncovered) questions refused
by the gate itself." Writing it that way in Unit 1 would have forced me to
build the harder test before I had any results to be influenced by, instead
of discovering the gap only after finding my system passed the easier
version too comfortably.

**Criteria 1 and 5** I'd leave as-is in wording, but I'd increase the sample
from 5 questions to something larger (8-10) if I were setting them up again
— not because the wording was wrong, but because 5-of-5 on 5 questions is a
weaker signal than the same ratio on a larger set, and I only really
understood that gap once I was staring at how easily every one of my
targets got cleared.

Criteria 2 and 4 I wouldn't change — 2 is a prompt-formatting guarantee that
doesn't need a harder test, and 4's target is validated by a chunking
strategy I deliberately built to make it near-guaranteed, which is a
legitimate design choice rather than a safe target.

     Milestone 5. -->
