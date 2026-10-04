# Revision Review: `book-revision` branch

A notebook-by-notebook log of this revision, so you can review the changes in context. Each notebook was changed in its own commit, and `git log --oneline main..book-revision -- <notebook>` shows its commit. To see a notebook's diff rendered (rather than as JSON): `uv run nbdiff-web main -- <notebook>`.

Rules followed throughout:
- No activity answer cells were filled. Activity notebooks got scaffolding fixes only (links, data paths).
- Existing content was never deleted except for leftover cells, which are noted. Questionable content is flagged below with ⚑ for your decision.
- Every changed notebook executes headless (`uv run python scripts/check_book.py <nb>`). Empirical claims in new prose were checked against rendered figures.

## Open decisions (⚑)

| # | Where | Question |
|---|---|---|
| 1 | matplotlib_tutorial, spatial_resolution, color_quantization, predictive_coding, imfilter_highpass_demo, color_clustering, spatial_ops, block_viewing_demo | These end in "Suggested Activity / Extensions / Further Efforts" sections, some of which read like earlier copilot output (especially block_viewing_demo's 5-item list and spatial_ops' "Potential Extensions"). Keep, trim, or remove? I left them unchanged. |
| 2 | Enhancement/enhance_transfer | The "Log Correction in Lab Space" section is a header with an empty cell. Is it meant as demo content (I can write it) or as an activity (leave it)? Left as-is. |
| 3 | Entropy/entropy_intro | Are the empty Decoding / Reconstructing / In Color sections activities? Assumed yes and left empty. |
| 4 | TOC | I kept "Spatial Operations" (spatial_ops: unsharp masking, gradients, Laplacian) under **Coordinate Systems**, where your original TOC put it, but its content fits **Spatial Filtering** better. Move it? |
| 5 | Phase 4 | When publishing, should notebooks that need datasets or a GPU be executed in CI, committed with outputs, or rendered without outputs? |

## Repo-wide commits

| Change | Notes |
|---|---|
| `.claude/CLAUDE.md` | Rewritten for this repo: layout, notebook conventions, the no-solutions rule, workflow. |
| Infrastructure | Added `scikit-learn` and `opencv-python-headless`, which were used but undeclared, plus dev tools. **`vis_utils` imported `cv2` at the top, so about 38 notebooks failed on import without opencv**; it's now imported lazily inside `loadvideo`. Fixed the call to undefined `makeRandomBasis` in `wavelet_utils`. New `dip_utils/data_paths.py` (`DIP_DATA` root, default `~/data`). New `scripts/check_book.py`. README now describes uv and lists datasets. Removed placeholder `main.py`. |
| Doc links | Versioned matplotlib 3.x / scipy 0.16 / python 3.7 / old torchvision doc URLs now point at current docs. |
| Relative links | Fixed 9 broken relative links (wrong `./` roots, `vis_utils.py:NNN` line refs, a stray backtick). The checker now validates every relative link and image `src`. |
| TOC | Every notebook is linked (was 19 of 60). Added a "Using this Book" cell. Topics without a notebook are marked *(coming soon)*. Fixed the duplicate Huffman link. |

Baseline before changes: 54/60 notebooks executed. Failures: entropy_intro (bug), play_mnist_correlate (expected; unanswered activity), torch_info (CUDA OOM on a 4 GB GPU), and yale_explore, yale_conv, pca_reconstructFaces (hardcoded `/home/dip365` paths).

## Per-notebook changes

### NumpyAndVisualization
| Notebook | What changed |
|---|---|
| numpy_tutorial | Doc links only. |
| matplotlib_tutorial | Doc and relative links only. ⚑1 |
| interactive_vis | New **Interactive Image Display** section: a brightness slider that uses the `VBox` + `imshow().set_data` pattern found throughout the book, with a walkthrough (clipping, saturation, `set_clim`) and close/`plt.ion()` hygiene. |
| probability_gauss_uniform | Doc links only. |
| viewing_video | Explains the (frames × H × W × 3) array and how `makeVideo` animates. Shows sample frames. New **Neighboring Frames Are Nearly the Same** section (frame differences, histogram, temporal coherence → predictive coding). |

### SensingSamplingQuantization
| Notebook | What changed |
|---|---|
| spatial_resolution | None. ⚑1 |
| color_quantization | Doc links only. ⚑1 |
| heightmap_demo | Motivates image-as-terrain (plateaus, valleys, cliffs → filtering and edges). Explains that `plot_surface` silently samples down to 50×50, which ties back to spatial resolution. New **Smoothing the Terrain** preview. Updated mplot3d links. |
| spatial_res_gif_maker | `writer='imagemagick'` changed to `'pillow'`, so it doesn't depend on a system ImageMagick. |
| playing_with_images | **Activity**: fixed broken links only. |

### Color
| Notebook | What changed |
|---|---|
| color_intro | New **Chromaticity** section (rg normalization, chromaticity image, pixel scatter in the rg triangle, pointer to CIE xy). The title promised chromaticity, but it wasn't covered before. Fixed a broken link and a typo. |
| color_HSV | Explains the saturation demo and hue as an angle. New **How the conversion works** (V/S/H formulas, numeric check that V = max). Reading the H/S/V channels, including why hue is noise where saturation is low. Explains `changeHue`'s wrap-around. The activity at the end is untouched. |
| color_YCbCr | Motivation (luma vs chroma, JPEG/video). New **The Conversion** (BT.601 matrix in LaTeX, checked on primaries). Reading the channels. New **Chroma Subsampling** demo (discarding 63/64 of the chroma is nearly invisible; the same for Y is not) → 4:2:0 and JPEG. Replaced a dead Wikimedia thumbnail link. Added `plt.ion()` after the slider demo so later figures display. |
| color_Lab | The biggest addition (61 → about 1,100 words). Opponent process and nonlinearity motivation. Reading the channels with ranges. New **Perceptual Uniformity** section (two pairs equally far apart in RGB that differ in ΔE76/ΔE00, with the formula and JND). New **Illuminants and the White Point** section (D65/D50/A, XYZ white points, white-balance demo on bellagio). |
| playing_with_color | **Activity**: untouched. |
