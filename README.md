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

## Stretch Features

I'm adding two stretch features: **metadata filtering** and **conversational
memory**.

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

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
