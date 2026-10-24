# THE LAST WATCH — FULL-LENGTH EDITORIAL PASS
**Writer:** Diesel · **Imprint:** DPN Novels
**Status:** Full-length manuscript milestone achieved; professional edit still pending

## Verified production baseline

- 76,146 words in the current validated build; 58 integrated scenes, 13 numbered chapters, prologue and epilogue
- Print-style PDF is 463 pages at 6 × 9 in, using 15 original vector chapter plates
- Authorship credit and text extraction are checked in the GitHub Actions publisher
- Source-of-truth: `manuscript/part-01.md`, `manuscript/part-02.md`, and `manuscript/scenes/*.md`
- Read the latest PDF at `books/The_Last_Watch_Extended_Edition.pdf`

## Completed continuity corrections

- [x] Ethan's decision to study civilian emergency-power engineering is preserved in the five-years-later epilogue
- [x] The missing USS Hawthorne captain, Matthew Hayes, receives confirmed status in the arrival chapters
- [x] The handoff into Ramirez's 1116 radio call no longer repeats the whole exchange
- [x] The Ramirez memorial preparation scene is placed after the November 20 dockside visits
- [x] Surviving LANTERN merchant count stays three out of four, with Caledonia lost
- [x] The outcome of ambiguous contacts remains explicitly unconfirmed; no unsupported victory claim

## Editorial queue before a public first edition

1. **Full timeline audit.** Cross-check every stated clock time in all 58 scenes against the chapter headings and the story bible. In particular check the transition between the first missile attack, Hawthorne reports, Sigrid's rescue, the second salvo, and the next day's relief.
2. **Repeat-beat reduction.** Identify repeated descriptions of uncertainty, exhaustion, coffee, the same crew members' guilt, and similar command dialogue; keep each scene's genuinely new dramatic or logistical contribution and tighten duplicated exposition.
3. **Character-specific voices.** Differentiate Vale, Mara Chen, Hassan Idris, Naomi Bell, Elena Ramirez, Eileen Ward, Peter Lindholm, Sofia Reed, and Edward Mallory by diction, motives and rhythms rather than relying on speech tags.
4. **Naval plausibility review.** Scrutinize damage-control boundaries, tactical-information delay, aircraft flying weather, merchant maneuvers, convoy escorts and command authorities for broad internal plausibility. Avoid turning the fictional combat scenes into detailed modern targeting instructions.
5. **Casualty and recovery ledger.** Reconcile Ramirez, Rios, Ochoa, Price, 19 Caledonia survivors, named missing mariners, rescued Kestrel sailors, Cutlass casualties and Hawthorne casualties. Preserve uncertainty where no definitive record exists.
6. **Pacing / chapter architecture.** Review the 13 large chapters as an overall dramatic structure. Consider whether multiple scenes should be condensed or chapter breakpoints redistributed before typesetting the first edition.
7. **Final illustrations.** Reconcile the cinematic color artwork pack with book canon before adding it to GitHub; ensure no wrong hull identifiers or uniforms. Current GitHub PDF contains reproducible vector illustrations, not that color art.
8. **Publication proof.** Inspect front/back matter, copyright/imprint text, cover, running heads, widows/orphans, page-turns, illustration placement, print bleed and file size. Do not claim print-ready status based on extraction tests alone.

## Next proposed literary work

Continue improving the **existing** story rather than stretching word count artificially. If further scenes are written, each should advance an unresolved relationship, decision or consequence and be inserted chronologically. Full prose and layout review are separate gates from achieving 75,000 words.

## Quality gates

- `python -m unittest discover -s tests -v`
- `python scripts/build_book.py`
- PDF size, searchable-text, trim and author checks in `.github/workflows/publish-book.yml`
- A human visual proof of representative spreads and cover before print distribution
