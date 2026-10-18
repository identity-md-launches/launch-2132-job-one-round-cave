# Citation Report

This is a small handoff layer for the existing Citation Ledger. It checks every
hash-pinned citation against the current local corpus, then emits only the
review queue: citation id, source, status, and whether the passage needs review.
It uses Python 3.9+ and the standard library, and delegates validation to the
workspace-local ledger without rewriting either input.

Try the inherited real historical ZTO-first example from the repository root:

```sh
python3 -B line-3/tools/citation-report/report.py demo
```

When tried, this reports the unchanged citation set and a zero-item review
queue. A changed source is reported as `needs_review: true`; this is a warning,
not a claim that the underlying source is true.
