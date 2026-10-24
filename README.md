# THE LAST WATCH
### Expanded Illustrated Edition | Written by Diesel • DPN Novels

> "The ocean does not decide who we are. Our actions do."

**The Last Watch** is an original first-person naval war thriller told by Commander Daniel Vale, commanding officer of the fictional guided-missile destroyer USS Northstar (DDG-148).

When a future North Atlantic war breaks out, Vale's destroyer and the British frigate HMS Cutlass must shepherd four civilian ships through hostile submarines, missile strikes, compromised communications, freezing weather, a catastrophic engineering fire, and the moral cost of command.

## Read the expanded edition

### [Download the PDF book](books/The_Last_Watch_Extended_Edition.pdf)

**Current published build:**
- **26,734 words**
- **156 printed pages**
- **13 chapters + prologue + epilogue**
- **19 integrated scenes** featuring richer tactical, engineering, rescue, crew-life and aftermath sequences
- Approximately **2.8–3.3 hours** of narration, depending on speaking pace

The PDF is typeset at **6 × 9 inches**, with a naval-themed vector cover, **four original illustrated chapter plates**, running headers, page numbers and a table of contents.

If the PDF link is missing after a new commit, check the [Publish book PDF workflow](.github/workflows/publish-book.yml) and its downloadable artifact. GitHub Actions rebuilds and commits the verified PDF when the source changes.

## Publishing credit and illustrations

**The Last Watch** is **written by Diesel**, published under the **DPN Novels** name. The PDF title page, metadata, cover treatment and running headers reflect this credit.

The current GitHub PDF also includes **four original print-friendly vector chapter illustrations** (stormship, radar, machinery fire, and Iceland harbor). Separate cinematic concept illustrations generated during development are not yet embedded as raster assets in the GitHub edition; the vector plates are included in the reproducible book build.

## What's new in the expanded edition

The original story was approximately 9,800 words. This revision has grown to more than 26,000 words, with four new scenes in the latest writing pass and substantial new material throughout:

| Area | Expanded narrative |
|---|---|
| Before the battle | Convoy boarding in Norway, displaced families, crew relationships, letters home, galley life and the responsibility of command |
| Undersea threat | Passive sonar, ambiguity, Raven One's extended flight, helicopter risks and junior operator judgment |
| Caledonia's loss | Rescue dilemmas, missing cargo manifest, civilian captains, survivors and their families |
| Missile attacks | Combat-information-center workload, uncertainty and defensive strain |
| Electronic warfare | Fake orders, contradictory information and independent verification |
| HMS Cutlass | British damage-control response and cross-ship coordination |
| Offensive engagement | Vale's lawful decision process, restraint and moral burden |
| Engineering fire | Compartment isolation, rescue pressure, propulsion and casualties |
| Crew recovery | Corpsmen, food, letters, midwatch mentorship, grief and delayed effects of battle |
| Storm transit | Icing, ice awareness, merchant-ship limitations and exhaustion |
| Allied relief | Friendly voices, logistics and a convoy that starts to hope |
| Aftermath | Memorial preparation, inquiry, survivor letters, and Ramirez's family |

## Read and develop the manuscript

| Location | Contents |
|---|---|
| [Part I](manuscript/part-01.md) | Prologue, chapters 1–7 with scene references |
| [Part II](manuscript/part-02.md) | Chapters 8–13 and epilogue |
| [Expanded scenes](manuscript/scenes/) | Nineteen standalone insert scenes, integrated by the PDF builder |
| [Story Bible](STORY_BIBLE.md) | Crew biographies, vessels, continuity rules and chronological battle events |
| [PDF builder](scripts/build_book.py) | Book-layout generator and scene compiler |
| [Manuscript tests](tests/test_manuscript.py) | Checks scene inclusion, chronology and narrative integrity |
| [PDF publishing workflow](.github/workflows/publish-book.yml) | Tests, builds, validates and commits the PDF |
| [Publication rights](RIGHTS.md) | Copyright and reuse restrictions |

The original chapter material remains readable on GitHub, with scene directives showing where the additional prose is inserted. The PDF compiler resolves those references automatically so the finished book reads as one narrative.

## Build locally

Install Python 3.12+ and the dependencies:

~~~bash
python -m pip install "reportlab>=4,<5" "pypdf>=5,<7"
python -m unittest discover -s tests -v
python scripts/build_book.py
~~~

The finished book is written to: **books/The_Last_Watch_Extended_Edition.pdf**

Every manuscript or publisher change triggers GitHub Actions. The build must pass source-continuity tests and PDF checks, including a 100-page minimum, extractable text, key chapters/scenes, and 6 × 9 trim size, before the new PDF is published.

## Next editorial milestone: a complete full-length novel

This is a substantial expanded novella/short novel, **not yet an 80,000-word commercial-length manuscript**. The goal is to grow it into a polished full-length military novel in installments, not to fill pages artificially.

Remaining work includes:
1. Develop separate multi-chapter arcs around the earlier attacks, the enemy's larger campaign and fleet-level consequences.
2. Add more internal conflicts for Vale, Mara, Bell, Idris, Navarro and Brooks, with realistic outcomes.
3. Fully dramatize Aurora's civilian perspective through Vale's communications and observations while retaining his first-person viewpoint.
4. Resolve technical and timeline issues in a comprehensive line edit.
5. Produce a navigable EPUB and professionally proofread paperback and audiobook editions.

Use the [Story Bible](STORY_BIBLE.md) before revising canon.

## Ownership

**Written by Diesel. Published as DPN Novels. © 2026 DPN Technology. All rights reserved.** The public repository is not an open-source or Creative Commons license. See [RIGHTS.md](RIGHTS.md).

This is fiction. Its ships, commanders, engagements and war are invented; no endorsement by any military organization is implied.
