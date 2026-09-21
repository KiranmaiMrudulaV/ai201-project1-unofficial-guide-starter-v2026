# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
Two of my five questions (the Kestrel Commons wait time and The Atrium restock
time) need information pulled from two separate files — a post and its
followup — to be fully correct, not just one. That makes them riskier than the
other three, which each have their answer sitting in a single file. I'm
leaving room for one of those cross-file questions to come back incomplete.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
This isn't a retrieval-difficulty problem like criterion 1 — it's whether the
prompt template in `generate.py` reliably includes a source line whenever it
produces an answer at all. Naming a source is necessary to even check whether
that source is valid (criterion 5), so there's no acceptable case where an
answer appears with no source attached. That's why this one is 5 of 5 and not
4 of 5.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

---

## 4. Chunks read as complete thoughts

At least 5 of 5 sampled chunks read as a complete thought, with no sentence
cut off at the start or end.

**Why this target:**
My `campus_life` documents are short (about 317 characters on average) and
each one covers a single topic — the default chunker turned 88 documents into
88 chunks because almost nothing hit the 800-character cutoff. Given how short
and self-contained these posts already are, a chunker that respects
document/paragraph boundaries should be able to produce a clean split every
time, not just most of the time — so I'm not giving myself room for a broken
chunk.



---

## 5. Cited sources actually contain the answer

For all 5 of my 5 test questions, the cited source document actually contains
the answer — not just a file that's topically related to the question.

**Why this target:**
Criterion 2 only checks that *a* source gets named, not that it's the right
one, so this is the check that actually matters. I expect 5 of 5 to be
achievable because my `campus_life` documents are narrowly single-topic —
each file covers one specific thing (one dining hall, one course, one admin
policy) — so there's little overlapping content that could make a
wrong-but-plausible file get cited instead of the correct one.



---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
