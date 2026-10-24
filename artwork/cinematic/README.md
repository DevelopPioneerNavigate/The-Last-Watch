# Cinematic Artwork Edition — Diesel / DPN Novels

This directory is the publishing contract for **The Last Watch** full-color, photo-illustrated edition. The user-approved artwork is in a downloadable, validated archive:

**The_Last_Watch_Cinematic_Plates.zip** (10 image assets, ~4.1 MB)

### Current repository state

- [x] Eight cinematic JPEG files are **already committed directly**, using 'committed_manifest.json'. One is reused for the cover and first crossing, giving **nine full-color PDF image pages**.
- [x] The [published 471-page PDF](../../books/The_Last_Watch_Extended_Edition.pdf) contains these real embedded image assets.
- [x] The publisher validates their SHA-256 checksums and scene locations.
- [x] The optional expanded ZIP source contains **ten distinct high-quality images**, with an additional Raven One helicopter plate and Aurora refugee-lounge plate, ready to become the next version.
- [ ] The optional ZIP is not committed yet. Its absence **does not mean the current book is unillustrated**.

### Publish the prepared cinematic images in one upload

To switch to the expanded ten-image pack, open this folder on GitHub, select **Add file → Upload files**, select the supplied 'The_Last_Watch_Cinematic_Plates.zip', and commit it to 'main'.

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
