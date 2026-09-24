"""
Unit 2: deciding whether an answer is correct.

`run_eval.py` looks for this file automatically. If it's here and `judge`
works, the Run columns in your run log carry real pass/fail verdicts instead
of coming back blank.
"""


def judge(question: str, expects: str, answer: str, results) -> bool:
    if not expects:
        return False
    return expects.strip().lower() in (answer or "").lower()
