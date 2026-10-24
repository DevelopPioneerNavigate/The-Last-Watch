# THE LAST WATCH
### A North Atlantic War Novel | DPN Technology

**The Last Watch** is an original, long-form naval war story told in the first person by Commander Daniel Vale, commanding officer of the fictional USS *Northstar* (DDG-148).

In a future North Atlantic conflict, Vale's destroyer escorts civilian evacuees and vital supplies toward Iceland through submarine attacks, missile engagements, electronic interference, a catastrophic shipboard fire, and the moral decisions that come with command at sea.

> "The ocean does not decide who we are. Our actions do."

## Read the book

**[Download the published PDF](books/The_Last_Watch_Extended_Edition.pdf)**

The PDF is generated from the source manuscript by the [Publish book PDF](.github/workflows/publish-book.yml) workflow. If the link is temporarily unavailable, check the latest workflow run on the Actions tab for the downloadable PDF artifact.

## Book contents

- Prologue — Three Sounds
- 1. The Ocean Doesn't Care Who You Are
- 2. The Sound Beneath Us
- 3. The Freighter
- 4. Fire in the Sky
- 5. The Enemy Has a Name
- 6. Ghosts of the Fleet
- 7. The Storm of Steel
- 8. The Order to Fire
- 9. Fire Below the Waterline
- 10. The Men Who Go Below
- 11. The Night That Would Not End
- 12. The Lights of Iceland
- 13. The Empty Place at the Table
- Epilogue — What the Ocean Kept

Approximately **9,800 words**, suited for about **one hour of measured narration** (actual narration length varies with speaking pace).

## Repository organization

| Path | Purpose |
| --- | --- |
| [manuscript/part-01.md](manuscript/part-01.md) | Prologue and chapters 1–7 |
| [manuscript/part-02.md](manuscript/part-02.md) | Chapters 8–13 and epilogue |
| [scripts/build_book.py](scripts/build_book.py) | Creates the designed, searchable 6×9-inch book PDF |
| [.github/workflows/publish-book.yml](.github/workflows/publish-book.yml) | Continuous PDF publishing with integrity checks |
| [books/](books/) | Published edition, created by the workflow |

## Rebuild locally

Requires Python 3.12+ (3.10+ should also work) and ReportLab.

\`\`\`bash
python -m pip install "reportlab>=4,<5" "pypdf>=5,<7"
python scripts/build_book.py
\`\`\`

The built edition appears at \`books/The_Last_Watch_Extended_Edition.pdf\`.

On every update to the manuscript or the publishing script, GitHub Actions rebuilds and verifies the PDF, uploads it as a workflow artifact, and commits the revised edition back to the repository when the generated file has changed.

## Editorial roadmap

- [ ] Expand the shipboard engineering, helicopter, bridge and CIC subplots into additional full scenes
- [ ] Add a detailed map of Convoy LANTERN's fictional route and a naval terms glossary
- [ ] Commission original, licensed cover illustrations and a full paperback design
- [ ] Develop an audiobook narration script with pace, pauses, and character dialogue cues
- [ ] Perform a technical review of naval terminology without disclosing sensitive operational information
- [ ] Maintain character biographies, ship specifications, and a story timeline for future revisions
- [ ] Produce an EPUB edition and print-on-demand cover file

## Rights

**© 2026 DPN Technology. All rights reserved.** Source is publicly viewable for collaboration and version history, but it is **not** offered under an open-source or Creative Commons license. See [RIGHTS.md](RIGHTS.md).

This is **fiction**. All primary characters and naval engagements are invented. It is not an account of a real battle.
