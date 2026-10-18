# Gathering 34 — The Checked Loop

Reviewed 2026-10-18. Read tools and documented usage before execution. All **50
available line suites / 678 tests** passed; **60 demos/trials** returned expected
exits, including deliberate conflicts and policy rejections. Citation Report has
no dedicated tests; its demo and an extra real-document probe ran. A passing
suite did not catch the defect below. Evidence: checks-34.json and
citation-report-probe-34.json. No line source or line record changed.

## Per line

| Line / one thing | What was tried and works | Broken or limited; cave-only or overlap |
| --- | --- | --- |
| **1: reviewable three-way text merging** | All 12 suites / 194 tests passed. Text/tree merge, packet rechecks, export, conflict finish, stage/resolution review, syntax/interface/binding review and Addition Audit ran. Addition Audit distinguishes a complete candidate from an omitted contribution; filesystem trials use disposable workspace scratch. | No failed check observed. Exact lines/multiplicity do not prove preserved meaning; the auditor shares merge logic. Python inventories do not model runtime scope/imports, and reads need stable UTF-8 trees. Useful beyond this cave and distinct from lines 2–4. |
| **2: Ethereum account/storage proofs against trusted roots** | All 14 suites / 190 tests passed. Account/code/proof-set/header/ancestry/diff/packing/policy tools, Balance Slot and Storage Fields ran. The real historical ZTO/IMD PoolManager fixture decoded sqrtPriceX96 `20794297345123442418062648917057`, tick `111407`, LP fee `12500`. | No failed check observed. These are historical raw fields, not a current quote. Balance Slot's example mapping slot zero is hypothetical: its demo returns `verified: false` and proves no balance/layout. Checkpoint authentication, finality and layout interpretation remain external. Useful beyond the cave; distinct from document citation. |
| **3: ranked offline search with exact citations** | All 13 available suites / 155 tests passed, plus Citation Report's demo. Search, freshness, receipts/bundles, corpus/query changes, guides, reading lists, phrases, reanchoring, context, ledger and diagnostics ran. An extra probe captures an inherited ZTO passage, prefixes a heading in scratch and correctly reports `relocated`, `needs_review: true`, review count 1. | **Fix needed: Citation Report emits an empty source for valid unchanged and relocated citations.** It reads `result.get("path", "")`, but Reanchor has no top-level path. Join checked entries to validated ledger entries by id and use `anchor.path`; fix report() and demo(), then add regression coverage. Reproduce with `python3 -B gathering/probe_citation_report34.py`. Protected line sources remain unchanged. Its CLI exits 0 even for a review queue: inspect `all_unchanged`/`review_count`. Hashes do not prove truth. Useful beyond the cave and distinct from authenticated Ethereum state. |
| **4: finite offline dependency resolution** | All 11 suites / 139 tests passed. Solver, conflict cores, exhaustive/core audits, repairs, lock plans/audits, viable releases, joint pins, explanations and Catalog Delta ran. The real metadata comparison reports chardet 4.0.0, idna 2.10 and requests 2.25.1 as added release labels. Joint Check distinguishes individual viability from joint incompatibility. | No failed check observed. Historical projections have different illustrative roots; comparison order is not chronology or an installation recommendation. Numeric catalogs exclude full package-manager semantics, platforms, artifacts and publisher trust; enumeration may be inconclusive. Useful beyond the cave and distinct from merging text. |

## Shared handoff

Added **Catalog Evidence**, shared/catalog-evidence/: Catalog Delta and its
resolver from line 4, Evidence Search from line 3, real inherited metadata
examples, ordinary local dependencies and SHA-256 provenance. Only Catalog
Delta's engine/example paths and boundary error label were adapted. It
regenerates a line-oriented comparison and returns exact ranked citations with
the full delta. Demo citation: `catalog-delta.md:9-13`, binding the Requests root
change and added releases to the report hash. Snapshot search deliberately keeps
`source_verified: false`; no live report file, chronology, compatibility or
truth is asserted.

Run: `python3 -B shared/catalog-evidence/evidence.py demo`

Seven focused checks passed for real citations, changed constraints,
recomputation, input immutability, deterministic order, label equivalence,
CLI hit/miss/error behavior, input rejection and provenance. Five shared suites
passed **99 tests** total, including inherited integrations. The inherited Claim
Bridge demo also verified 2 documents / 4 citations. Evidence:
shared-checks-34.json and catalog-evidence-demo-34.json. A copied standalone
folder was also exercised without the line directories.

Worker-selected integration decisions: report text format, default query
`requests idna`, snapshot search and copy layout. These are implementation
choices, not requester-supplied values. The shared README gives limits.

## Scope and coins

No goal is cave-only or repeats another line. To fit 21 Pepes, retain useful
bounds: stable bounded UTF-8 trees with explicit review (1), supported proofs
under externally authenticated roots (2), bounded lexical collections and byte
citations (3), finite numeric catalogs and explicit budgets (4). Universal
semantic merging, consensus validation, factual truth and complete package
ecosystems would exceed those scopes.

COINS.md: **none**. These tools work offline or read public evidence. ZTO first
and IMD second already supply real token/pool examples. None needs a new coin
or v4 hook. No coin order, launch or Sepolia deployment is warranted. Nothing
was signed, sent, paid, posted or deployed.

## Wall, records and gallery

The assigned Replicate image MCP used public black-forest-labs/flux-kontext-pro
after inspection of its current schema. One prediction succeeded. Its whole-wall
edit altered ancestry, so only its new loop's red mask was flattened onto unused
right-side rock. All other pixels come unchanged from gathering 33. Full wall
and JPEG were inspected; the loop is subdued at thumbnail scale. Exact prompt
and generation details: IMAGE_PROMPT-34.md.

- artifacts/gathering/wall-v14.png: **1254 × 1254 RGB PNG**, SHA-256
  `848380f63c56ad699dba11e67fda8f6ef01348f89936252041206b68271c0381`.
- artifacts/gathering/wall.png continues to it. **3,229** changed pixels inside
  `[1070,430,95,95]`, **zero** outside. Rock, cracks, colour, light, framing and
  ancestral marks remain unchanged outside the new pigment.
- dist/gathering/34.jpg: **512 × 512 JPEG**, **81,306 bytes**.
- dist/gathering/34.json: six required traits and the actual wall content hash.
- dist/goals.json matches all four unchanged GOAL.md files. dist/index.html
  embeds **165 records**, five walls newest first; all **100** inherited
  placeholders remain without JPEGs. This is not the first gathering.

Pepe's wide mouth and heavy-lidded eyes remain unchanged. No hands or handprints
were added; existing hands are concealed and unchanged. No letters, numbers,
logos, watermarks, borders or prohibited symbols were observed. No unmet visual
requirement identified; this is worker review, not independent visual approval.

The inline gallery check passed. Sandboxed Chromium passed at **320, 390 and
1440 px**: no horizontal overflow or page exceptions; click/Enter toggling,
section navigation, newest record and local JPEG decoding worked. HTTPS requests
for this new, not-yet-uploaded artifact returned `net::ERR_BLOCKED_BY_ORB`;
remote availability is not claimed. The local fallback worked. Console errors:
none. Browser evidence: gallery-browser-34.json. Screenshots stay in /tmp.

Reproduce from the repository root:

```sh
python3 -B gathering/check_round34.py
python3 -B gathering/check_shared_round34.py
python3 -B gathering/probe_citation_report34.py
python3 -B gathering/build_gallery.py
node gathering/check_gallery34.mjs
python3 -B gathering/check_deliverable_round34.py
```
