# Cinematic Artwork Edition — Diesel / DPN Novels

This directory is the publishing contract for **The Last Watch** full-color, photo-illustrated edition. The user-approved artwork is in a downloadable, validated archive:

**The_Last_Watch_Cinematic_Plates.zip** (10 image assets, ~4.1 MB)

### Current repository state

- [x] Ten images mapped to exact scenes and cover in 'manifest.json'.
- [x] 'scripts/cinematic_art.py' verifies every SHA-256 digest and extracts the archive safely.
- [x] 'scripts/build_book.py' replaces the basic vector-only cover and inserts full-page cinematic images at matching narrative boundaries when the archive is present.
- [x] GitHub Actions rebuilds on artwork changes and verifies at least ten image-bearing PDF pages before publication.
- [ ] The **ZIP binary itself needs to be committed to this folder**. Until then GitHub retains the earlier vector-only edition, rather than claiming uncommitted artwork is included.

### Publish the prepared cinematic images in one upload

Open this folder on GitHub, select **Add file → Upload files**, select the supplied 'The_Last_Watch_Cinematic_Plates.zip', and commit it to 'main'.

**Do not extract or rename the ZIP.** The publisher looks for the exact path:

    artwork/cinematic/The_Last_Watch_Cinematic_Plates.zip

GitHub Actions will automatically:
1. Verify the archive's ten JPEGs against the committed SHA-256 manifest.
2. Insert a photo cover and nine full-color scenes at their matching narrative beats.
3. Preserve the manuscript wording, Diesel author credit, 6×9 trim, and table of contents.
4. Verify at least ten image-bearing pages and commit the updated PDF.
5. Reject missing or corrupted images instead of publishing a partially illustrated edition.

### Narrative placements

| Artwork | Placement |
|---|---|
| Stormy moonlit convoy | Full-color front cover |
| Caledonia rescue | The Distance Between Ships |
| CIC missile attack | The Twelve Tracks |
| Ramirez and the engine-room fire | The Door With No Handle |
| Reykjavík harbor | The Pier at Reykjavík |
| Liv's new home | The Green Roof |
| Raven One helicopter | Raven One's Empty Seat |
| HMS Cutlass after the strike | The Lieutenant's Bridge |
| Aurora children with paper boats | Beneath Aurora's Windows |
| Northstar defending against missiles | Before the Second Salvo |

These are dramatic interpretations of fictional events, not documentary images or technical reference drawings. Before commercial printing, proof every spread, check hull numbers and uniforms, and assess color-print suitability.

### Adding more images

Create a high-resolution JPG/PNG, add a unique file/anchor/title/caption/sha256 entry to 'manifest.json', and recreate the ZIP with every named file under the 'plates/' subfolder. Commit both the manifest and ZIP; the existing build automatically places the new image at its matching scene.
