# Revision Review: `book-revision` branch

A notebook-by-notebook log of this revision, so you can review the changes in context. It covers two rounds: round 1 (the per-notebook revision and the open questions it raised) and round 2 (2026-10-06), which carries out your answers to those questions, including the six new notebooks. The tag `revision-draft-2` marks the end of round 2. Each notebook was changed in its own commit, and `git log --oneline main..book-revision -- <notebook>` shows its commits (the [commit index](#commit-index) at the bottom lists them). To see a notebook's diff rendered rather than as JSON: `uv run nbdiff-web main -- <notebook>`.

Rules followed throughout:
- **No activity answer cells were filled.** Activity notebooks got scaffolding fixes only (links, data paths). Where a planned demo would have answered an activity prompt, I skipped it (see ⚑6).
- Existing content was never deleted except for leftover cells (stray empty cells, self-export `nbconvert` lines, an addressed note-to-self), each noted below. Questionable content is flagged ⚑ for your decision.
- Every notebook executes headless (`uv run python scripts/check_book.py`). Numbers and visual claims in the new prose were checked against rendered figures and actual outputs, and corrected where they didn't hold.
- Prose is drafted in your voice for you to edit freely.
- Round 2: every reader task uses one of two consistent forms (see [Reader-task format](#reader-task-format)), and their guidance never gives an answer away.

## Round 2: your decisions, and what I did

| # | Your decision | What I did |
|---|---|---|
| 1 | Keep the Suggested Activity / Further Efforts sections (they stand in for problem sets); clean up the copilot-y wording; make them consistent. | All are now **🧠 Further Efforts**, or **🔨 Your Turn** where they ask for one specific task. Trimmed duplicates and vague items, added a *Guidance:* line to each problem, and corrected a few claims (below). Summaries in spatial_ops and mnist_linear rewritten to match what the notebooks actually show. The "(thanks Claude)" notes went with the rewrite (⚑11). |
| 2 | Log correction in Lab is for the reader to try; format it consistently. | enhance_transfer: now **🔨 Your Turn: Log Correction in Lab Space**, with Task and Guidance (the L range, `arr_info` at each step, how to compare). |
| 3 | entropy_intro's empty sections are reader work; make consistent, with an icon and more guidance for standalone readers. | Three **🔨 Your Turn** sections (Decoding, Reconstructing, In Color). The guidance names the prefix-free property without saying how to use it, and warns that `load_huffable_image` converts to gray. Same treatment for every other in-notebook prompt: color_quantization, enhance_histeq, block_viewing_demo (two), basis_decomp_64pix, generic_filter_demo, fft_blur_sharpen. |
| 4 | Move spatial_ops to Spatial Filtering. | TOC: it now opens the Spatial Filtering chapter (filters_explore3D builds on it). Coordinate Systems is coord_ops plus the new geometric_transforms. |
| 5 | Phase 4: commit dataset/GPU notebooks with outputs (never the datasets). | Recorded for Phase 4. This conflicts with the clear-outputs rule, so Phase 4 needs a deliberate mechanism (⚑14). |
| 6 | Don't give the activity away; try an alternative demo plus activity. | generic_filter_demo: new demo of a **local standard deviation** filter (busyness map), then the same filter rebuilt from two `uniform_filter`s and point operations, 200–300× faster in my runs, with identical output. Your min/median prompt is now **🔨 Your Turn: Other Neighborhood Functions**, followed by a new **🔨 Your Turn: Salt-and-Pepper Noise** that lets students discover the median for themselves. |
| 7 | Keep the high-accuracy logits version; leave the sigmoid commented with a note and a link. | yale_conv: `forward` keeps only `# output = torch.sigmoid(x)  # Don't: see "A cautionary tale" above.` The markdown explains the ≈7% probability cap and the 2.7 loss floor, and links PyTorch's CrossEntropyLoss docs and CS231n's softmax notes. |
| 8 | Keep the boilerplate in mnist_linear, hide it in the others, and explain where it went (as with `arr_info`). | New `dip_utils/torch_utils.py` (`train`, `test`, with a `loss_fn` argument; they return losses for plotting). mnist_linear keeps the loops inline and says they'll move. mnist_conv and yale_conv import them, with a paragraph pointing back. The Namespace cells stay (they're the per-notebook settings) and point to mnist_linear for the explanation. |
| 9 | Keep the test set consistent; keep the explanation; comment what to remove. | yale_conv: comment at the `ColorJitter` line saying what to delete (or how to load twice) for a consistent test set. |
| 10 | Draft the six proposed notebooks and put them in the TOC. | Done; see [Phase 3](#phase-3-new-notebooks). |

<a id='reader-task-format'></a>
### Reader-task format

Documented in `.claude/CLAUDE.md` and explained to readers in the TOC's "Using this Book":

- **🔨 Your Turn: <task>**: an in-flow task. A sentence of motivation, **Task** (what to produce, and how to tell it worked), **Guidance** (functions and docs to use, pitfalls, how to check), then an empty code cell. Later cells never depend on the answer.
- **🧠 Further Efforts**: the end-of-notebook problem set. Numbered problems with bold titles, each with a *Guidance:* line.
- Whole-notebook exercises are marked 🔨 in the TOC. Inside the `play_*` notebooks I changed nothing (⚑15).

## Still open (round 2)

| # | Where | Question |
|---|---|---|
| 11 | Several notebooks | The "(thanks Claude)" / "(thanks in part to Claude)" notes went away when I rewrote those sections. Want an attribution line kept somewhere (each section, or once in the TOC's note on AI)? |
| 12 | BlockTransform/reconstruction_comparison | The Haar (part 2), DCT and JPEG exercises all have students build the blockwise transform, keep, reconstruct, reassemble pipeline. So this notebook never reconstructs an image: it uses Parseval's theorem to get exact PSNRs from the dropped coefficients' energy, on blocks flattened to 64-vectors with Kronecker-product bases. Likewise haar_wavelets works on the whole image with global thresholding, not per block. OK, or too cautious? |
| 13 | dip_utils | `uv run ruff check dip_utils scripts` (the CLAUDE.md lint command) reports 22 pre-existing issues in huff_utils, huffnode, matrix_utils, vis_utils and wavelet_utils. Fix them in a separate commit? (The new torch_utils is clean.) |
| 14 | Phase 4 | How to square "commit with outputs" (⚑5) with "clear outputs before committing". Options: a short list of notebooks exempt from clearing; or the CI build executes everything except the dataset/GPU notebooks, whose executed copies live in a separate folder or branch. |
| 15 | Activity notebooks | The `play_*` notebooks keep their own headers (only marked 🔨 in the TOC), since I only touch scaffolding there. Want their prompt headers converted to the 🔨 format too? |
| 16 | NeuralNets/yale_conv | `random_split` runs before `torch.manual_seed`, so the split, and the accuracy (93–96% in my runs), changes every run. The text now says so. Seed the split for reproducibility? |

## Round 1: open decisions (⚑), now resolved above

| # | Where | Question |
|---|---|---|
| 1 | matplotlib_tutorial, spatial_resolution, color_quantization, predictive_coding, imfilter_highpass_demo, color_clustering, spatial_ops, block_viewing_demo, mnist_linear | These end in "Suggested Activity / Extensions / Further Efforts / Summary" sections, several marked "(thanks Claude)" and some reading like copilot output (especially block_viewing_demo's 5-item list and spatial_ops' "Potential Extensions"). Keep, trim, or remove? Left unchanged. |
| 2 | Enhancement/enhance_transfer | The "Log Correction in Lab Space" section is a header with an empty cell. Demo content I should write, or an intentional activity? Left as-is. |
| 3 | Entropy/entropy_intro | Are the empty Decoding / Reconstructing / In Color sections activities? Assumed yes and left empty. |
| 4 | TOC | "Spatial Operations" (spatial_ops: unsharp masking, gradients, Laplacian) stays under **Coordinate Systems**, as in your original TOC, but its content fits **Spatial Filtering** better. Move it? |
| 5 | Phase 4 | For the published site, should notebooks that need datasets or a GPU be executed in CI, committed with outputs, or rendered without outputs? |
| 6 | SpatialFiltering/generic_filter_demo | The plan included a median-filter/salt-and-pepper demo, but the notebook ends by asking students to try min/median and explain the difference. I skipped the demo so it doesn't give that away. Want it anyway? |
| 7 | NeuralNets/yale_conv | **Behavior change.** The network ended in `torch.sigmoid` before `F.cross_entropy`, which applies its own softmax. With 38 classes that caps the correct-class probability near 7%, so the loss can't fall below about 2.7 and gradients are weak. It now returns raw logits (the sigmoid line is kept, commented). It still reaches about 96% test accuracy. OK to keep? |
| 8 | NeuralNets/mnist_linear, mnist_conv, yale_conv | The train/test/`Namespace` boilerplate is repeated across the three. I kept it inline because it teaches; it could move to `dip_utils/torch_utils.py`. |
| 9 | NeuralNets/yale_conv | The test split shares the training set's random `ColorJitter`, so test images are re-jittered each epoch. I explained this in the notebook but didn't restructure the data loading. Restructure? |
| 10 | Phase 3 | The new-notebook outlines below need your go-ahead before I draft them. |

## Bugs fixed along the way

| Where | Bug |
|---|---|
| dip_utils/vis_utils | `import cv2` with opencv not declared as a dependency broke the import in about 38 notebooks; added `opencv-python-headless`. |
| dip_utils/wavelet_utils | `make_random_basis` retried by calling an undefined `makeRandomBasis`. |
| Entropy/entropy_intro | `vis_hists(I)`: `I` undefined (should be `Ih`), so the notebook crashed. |
| NeuralNets/mnist_linear, mnist_conv | Train loss was averaged over samples instead of batches, so it printed about 64× too small, and train-vs-test plots weren't comparable. |
| NeuralNets/torch_info | Ran out of memory on GPUs with less than about 4.5 GB. GPU timing lacked `synchronize()` (it measured kernel launches). The loop ran 100 iterations but reported "20 iters", as a total rather than per iteration. |
| NeuralNets/yale_conv | sigmoid before cross_entropy (⚑7). Crash if there are no mistakes. |
| PCA/pca_scatterFaces | Sampled subjects from 1..40, but labels are 0..39. |
| SLIC/slic_demo | Off-by-one bounds check in `reinitM` could index past the image edge. |
| SpatialFiltering/filters_explore3D | The "Cross-derivative" and "second derivative in both directions" plots were mislabeled: the latter was the product g''(x)g''(y), not the Laplacian. |
| FFT/fft_intro | Text said 80% of coefficients were zeroed; it's 96%. The "display error" was just LogNorm masking zeros. |
| FFT/fft_blur_sharpen | Gaussian formula missing its factor of 2. Box-cutoff artifacts were called aliasing (they're ringing). |
| SensingSamplingQuantization/spatial_resolution | (round 2) A comment said "bilinear sampling" on an `order=0` (nearest neighbor) call. |
| SensingSamplingQuantization/color_quantization | (round 2) Text referred to `I6`; the variable is `I4`. |
| BlockTransform/intro_spatial_coherence | (round 2) The 2D Haar "Extension" said wavelets are "precisely how JPEG" compresses (JPEG uses the DCT; wavelets are JPEG 2000), had the LH/HL edge orientations swapped, and wrote the block with `vmatrix` (determinant bars). |
| NeuralNets/yale_conv | (round 2) My round-1 text claimed about 96% accuracy; the unseeded split gives 93–96% from run to run. Now says so (⚑16). |
| Hardcoded data paths | `/home/dip365/...` and `~/data` paths in 9 notebooks now go through `dip_utils/data_paths.py`. 3 notebooks failed in the baseline because of them. |
| Links | 9 broken relative links, 1 dead hotlinked image, about 25 versioned doc links. |

## Repo-wide commits

| Change | Notes |
|---|---|
| `.claude/CLAUDE.md` | Rewritten for this repo: layout, notebook conventions, the no-solutions rule, workflow. |
| Infrastructure | Added `scikit-learn` and `opencv-python-headless` (used but undeclared) and dev tools (`jupyter`, `nbconvert`, `nbclient`, `nbdime`, `ruff`). New `dip_utils/data_paths.py` (one `DIP_DATA` root, default `~/data`, with helpful errors). New `scripts/check_book.py`: TOC and relative-link checks, plus headless execution. It treats a `NameError` in an activity as expected, and restores `dip_outs/` afterwards. README now describes uv and has a dataset table. Removed placeholder `main.py`. |
| Doc links | Versioned matplotlib/scipy/python/torchvision doc URLs now point at current docs. |
| Relative links | Fixed wrong `./` roots, `vis_utils.py:NNN` line refs, and a stray backtick. |
| `.claude/CLAUDE.md` (round 2) | Reader-task format; Segmentation folder. |
| `dip_utils/torch_utils.py` (round 2) | Shared `train`/`test` for the NeuralNets chapter (⚑8). |
| TOC (round 2) | spatial_ops moved (⚑4); six new notebooks linked; "Using this Book" explains 🔨 Your Turn and 🧠 Further Efforts; exercises marked 🔨; KLT and Canny entries point to the notebooks that cover them. Only "Communication, Compression, and Perception" is still *coming soon*. |
| TOC | Every notebook is linked (was 19 of 60). New "Using this Book" cell. Unwritten topics marked *(coming soon)*. Duplicate Huffman link fixed. |

**Execution:** 54/60 notebooks ran before the revision. Now all 60 run (play_mnist_correlate stops at its unanswered activity cell, as designed).

**Execution, round 2:** all 66 run. On a small GPU (this laptop's 3.7 GB), `check_book.py`'s 4-at-a-time execution can run torch_info and yale_conv out of GPU memory together; they pass when run alone (`uv run python scripts/check_book.py NeuralNets/yale_conv.ipynb`).

## Round 2 per-notebook changes

| Notebook | What changed |
|---|---|
| NumpyAndVisualization/matplotlib_tutorial | Suggested Activity → 🧠 Further Efforts (color cubes compared; how many samples are enough). |
| SensingSamplingQuantization/spatial_resolution | → 🧠 Further Efforts (interpolation orders; anti-aliasing, linked forward to low-pass and Fourier). Comment fix. |
| SensingSamplingQuantization/color_quantization | 🔨 Your Turn: Interactive Color Quantization (with an empty cell, which it lacked). Additional activities → 🧠 Further Efforts, trimmed from 8 to 4 plus "Going further" (dithering, non-uniform quantization). `I4` fix. |
| Enhancement/enhance_transfer | ⚑2: 🔨 Your Turn: Log Correction in Lab Space. |
| Enhancement/enhance_histeq | "I leave it to you" → 🔨 Your Turn: Equalize a Real Image (your guidance kept, plus a check against `equalize_hist`). |
| Entropy/entropy_intro | ⚑3: three 🔨 Your Turn sections. |
| Entropy/predictive_coding | → 🧠 Further Efforts: vertical prediction, PNG's predictors (new), cross-channel, quantized residuals. |
| Entropy/color_clustering | → 🧠 Further Efforts, 5 problems tightened (fit on a pixel sample for speed; median cut / Pillow `quantize`). |
| SpatialFiltering/spatial_ops | Summary rewritten (accurate, links onward to the chapter, including edge_detection). Potential Extensions → 🧠 Further Efforts (diagonal Sobel, unsharp masking at several scales, image types). ⚑4 in the TOC. |
| SpatialFiltering/generic_filter_demo | ⚑6: local standard deviation demo, box-filter rebuild with timing, two 🔨 Your Turn sections. Contents list added. |
| SpatialFiltering/imfilter_highpass_demo | Activity → 🧠 Further Efforts: 4- vs 8-neighbor kernel (new), LoG at several scales (with a warning that `gaussian_laplace` has the opposite sign to `laplace_h`, and its scale shrinks with σ), two sliders. |
| BlockTransform/block_viewing_demo | Two 🔨 Your Turn (larger image; four means per block); the 5-item list → 🧠 Further Efforts (median, activity per block, dominant colors, multiple scales), dropping the quad-tree item that duplicated your four-means prompt. |
| BlockTransform/basis_decomp_64pix | 🔨 Your Turn: Your Own Pixel Art, and Other Bases (with an empty cell). |
| BlockTransform/intro_spatial_coherence | "Extension" → "Looking Ahead: the 2D Haar Transform" (exposition, not a task), corrected, linked to haar_wavelets. |
| FFT/fft_blur_sharpen | 🔨 Your Turn: Sharpen in the Frequency Domain. |
| NeuralNets/mnist_linear | ⚑8: says the loops move to `torch_utils`. Summary rewritten (no longer claims the weights resemble digits, which contradicted the weight-map discussion). |
| NeuralNets/mnist_conv | ⚑8: imports `train`/`test`. Re-run: 99%. |
| NeuralNets/yale_conv | ⚑7, ⚑8, ⚑9. Accuracy text (⚑16). |

## Round 1 per-notebook changes

### NumpyAndVisualization
| Notebook | What changed |
|---|---|
| numpy_tutorial | Doc links only. |
| matplotlib_tutorial | Doc and relative links only. ⚑1 |
| interactive_vis | New **Interactive Image Display** section: a brightness slider using the book's `VBox` + `imshow().set_data` pattern, with a walkthrough (clipping, saturation, `set_clim`) and close/`plt.ion()` hygiene. |
| probability_gauss_uniform | Doc links only. |
| viewing_video | Explains the video array and `makeVideo`. Shows sample frames. New **Neighboring Frames Are Nearly the Same** (frame differences, temporal coherence → predictive coding). |

### SensingSamplingQuantization
| Notebook | What changed |
|---|---|
| spatial_resolution | None. ⚑1 |
| color_quantization | Doc links only. ⚑1 |
| heightmap_demo | Image-as-terrain motivation. Explains that `plot_surface` silently samples to 50×50. New **Smoothing the Terrain** preview. |
| spatial_res_gif_maker | `writer='pillow'` instead of ImageMagick. |
| playing_with_images | **Activity**: broken links fixed only. |

### Color
| Notebook | What changed |
|---|---|
| color_intro | New **Chromaticity** section (the title promised it): rg normalization, chromaticity image, pixel scatter, pointer to CIE xy. A link and a typo fixed. |
| color_HSV | Explains the saturation demo and hue as an angle. New **How the conversion works** (formulas plus V = max check). Reading the channels, including hue noise at low saturation. Explains `changeHue`'s wrap-around. Activity untouched. |
| color_YCbCr | Motivation. New **The Conversion** (BT.601 matrix, checked on primaries). Reading the channels. New **Chroma Subsampling** demo (dropping 63/64 of the chroma is nearly invisible; the same for Y is not) → 4:2:0 and JPEG. Dead image link replaced. `plt.ion()` added after the slider. |
| color_Lab | 61 → about 1,100 words. Opponent process and nonlinearity. Channel reading. New **Perceptual Uniformity** (equal RGB steps, unequal ΔE76/ΔE00). New **Illuminants and the White Point** (D65/D50/A, white-balance demo). |
| playing_with_color | **Activity**: untouched. |

### Enhancement
| Notebook | What changed |
|---|---|
| enhance_transfer | Removed the "*A lot of pictures from my slides might go here*" placeholder. Filled in the open "?" bullet. ⚑2 |
| enhance_histeq | Typos. |
| bit_slicing_example | Bit-plane math and an 8-plane figure. Explains why `I \| Im` leaves noise in the message's dark strokes. Adds exact embedding `(I & 0xFE) \| Im`, fragility note. The final comparison now uses the exact version. |
| gray_flower_example | How to read transfer curves (steep = more contrast) and what each of the five transforms does. |
| playing_with_enhance | **Activity**: untouched. |

### Entropy
| Notebook | What changed |
|---|---|
| entropy_intro | **Bug fix** `vis_hists(Ih)`. Interprets entropy (3.75 bpp) and Huffman (3.77 bpp, within 0.02 of the bound). ⚑3 |
| predictive_coding | Removed a stray empty cell. ⚑1 |
| color_clustering | Indexed-color motivation (GIF/PNG-8). Explains k-means, and why centers fall outside [0,255] (empty clusters; your in-code question). New **How Much Did We Save?** (24 → 8 bpp, label entropy 7.55). scipy/sklearn label fixed. ⚑1 |
| color_picking | Why the popularity palette fails (the sunset glow loses out to many near-identical dark colors) vs k-means. Median cut. |

### SpatialFiltering
| Notebook | What changed |
|---|---|
| coord_ops | Full walkthrough (coordinates, rotation matrix, inverse mapping, valid mask, floor sampling). New **Why Not Forward Mapping?** (holes demo). New **Rotating About the Center** with nearest vs bilinear via `map_coordinates`. Your note-to-self ("Really need to talk through…") removed, since it's now addressed. |
| spatial_ops | Back-link to predictive coding. Why `int16`. Unsharp-masking formula and overshoot/halo. Gradient and Laplacian math. Profile plot labeled. ⚑1, ⚑4 |
| imfilter_lowpass_demo | Correlation formula, normalization, convolution vs correlation, borders, separability. Reading the comparisons. Notes that the slider's 25-px kernel truncates the Gaussian past σ≈4. |
| imfilter_highpass_demo | Derives the Laplacian kernel, zero-sum property, L = 9(I − box3(I)), so I + αL *is* unsharp masking. Activity untouched. ⚑1 |
| generic_filter_demo | Non-linear filters, `generic_filter` mechanics and cost. ⚑6 |
| filters_explore3D | Explains each kernel shape. **Corrects** the mislabeled plots and adds the true Laplacian of Gaussian. |

### BlockTransform
| Notebook | What changed |
|---|---|
| intro_spatial_coherence | None. The empty "Extension: 2D Haar" tail would be folded into the Phase 3 Haar notebook. |
| view_basis_blocks | Broken link fixed. |
| block_viewing_demo | None. ⚑1 |
| block_glyph_demo | New title ("Glyph Image Converter"). Explains glyphs, resizing, block views, the transform loop (your commented variants), and the link to JPEG. |
| basis_decomp_64pix | 2D Haar transform math, basis images, how to read both 8×8 figures. Activity prompts untouched. |
| play_DCT_intro, play_Haar_compression, play_JPEG_compression | **Activities**: untouched. |

### FFT
| Notebook | What changed |
|---|---|
| fft_intro | New **Frequencies in 2D** (stripe patterns → dot pairs; distance = frequency, direction ⟂ stripes, linearity). Shift explained. The moon's periodic noise as spikes. **Fixes** 80% → 96% and explains the "display error". Ringing caveat. Phase intuition. Removed the self-export cell. |
| fft_blur_sharpen | New **Convolution Theorem** with a numeric check (frequency-domain blur equals `gaussian_filter`, max difference 3×10⁻¹⁰), σ_s = N/(2πσ_f), box-vs-Gaussian via sinc. Note on `fftn` over color. **Fixes** the Gaussian formula and "aliasing". High-pass interpretation. The closing "How might we sharpen?" prompt is left open. |

### PCA (ordered as an arc in the TOC)
| Notebook | What changed |
|---|---|
| pca_intro_2d | PCA/KLT motivation. Explains the synthetic data's known answer. Covariance/eigenvector math, verified against sklearn. Decorrelation. Reconstruction math. New **Dimensionality reduction** (1-component projection; MSE equals the dropped variance). |
| pca_intro | Iris introduction. Reading the 2D vs PCA views, explained variance, PC1 ≈ petal size (with a standardization caveat). |
| pca_mnist | Data path. Explains components. Adds mean digit and variance curve (10 PCs → 49%, 64 → 86%), k-component reconstructions of test digits, and a PC scatter colored by label. |
| pca_scatterFaces | Data path. Eigenfaces intro. Reading each plot and t-SNE. **Fixes** subject sampling and the 320→400 comment. |
| pca_spanFaces | Data path. Explains the sorted animation, `makeinterp`, what PC0 does (mostly brightness/lighting). Slider label fixed. |
| pca_reconstructFaces | Data path (was `/home/dip365`, failed in the baseline). Coefficients, magnitude ordering, slider, out-of-sample residual. Fixed the example `IMAGE` path (`josh_thumbnail.png` is 112×92). |

### SLIC
| Notebook | What changed |
|---|---|
| demo_kmeans_2D | Objective J. Init/assign/update steps labeled. Convergence argument. New run-to-convergence loop. Caveats (center bias between unequal blobs, initialization, choosing K). Empty cells dropped. |
| demo_kmeans_image | Pixels as RGB points, initialization, the loop and empty clusters, the scatter's R-G projection, lost rare colors (the purple flowers). |
| slic_demo | **Restructured**: the single 200-line cell is split into 10 staged cells, each explained (5D distance, local window and O(N), compactness, gradient reinit, mode cleanup, RGB vs paper's CIELAB). New skimage comparison (compactness 10 vs 30). Off-by-one fixed. |

### Radon
| Notebook | What changed |
|---|---|
| radon_forward_example | CT motivation, Radon definition, the phantom, reading a sinogram. Points to the activity for `iradon`. |
| radon_dot_animation | Derives point → sinusoid (amplitude = distance, phase = angle). Explains the animation and its accumulating interpolation blur. |
| radon_draw_your_own | Usage and predicting the sinogram by superposition. |
| play_radon_iradon | **Activity**: untouched. The demos avoid interpreting the activity's specific cases and don't demo `iradon` manipulations. |

### NeuralNets
| Notebook | What changed |
|---|---|
| torch_info | **Rewritten timing** (results are machine-dependent): `BATCH` parameter (was 4.4 GB on the GPU), runs without CUDA, `synchronize()`, fixed loop count and units, transfer timing, float32 vs float64 comparison. On this laptop float64 is about 10× *slower* on the GPU, while float32 is about 3× faster. Takeaways. |
| mnist_explore | Data path (`download=True`). Dataset items, `ToTensor`, grids, the summed sevens. (Deliberately no per-digit mean images: they'd give away the correlate activity's templates.) |
| play_mnist_correlate | **Activity**: data path only. |
| mnist_linear | Data path. Model, softmax, the five-step training loop, optimizer, results (about 92.5%). Zero-centered weight colormap; templates are mostly negative evidence. **Loss-averaging fix**. ⚑1, ⚑8 |
| mnist_conv | Data path. Layer-by-layer architecture, normalization, where the 1.2M parameters are, curves (99.0%), mistakes. **Loss-averaging fix**. Removed the mkdir and stale nbconvert cells. ⚑8 |
| yale_explore | Data paths (were `/home/dip365`, failed in the baseline). Labels (no yaleB14), lighting variation, augmentation, unstratified split. |
| yale_conv | Data path (failed in the baseline). Shape tracing. **Logits fix** ⚑7. Jittered-test caveat ⚑9. Overfitting (train loss → 0, test loss ≈ 0.35, 96%). Mistakes are the darkest photos. Guard for zero mistakes. ⚑8 |

<a id='phase-3-new-notebooks'></a>
## Phase 3: new notebooks (round 2)

All six follow the book's conventions, run headless, and had every number and visual claim checked against their own outputs. Each ends with a 🔨 Your Turn and a 🧠 Further Efforts. They avoid giving away existing exercises (⚑12).

| Notebook | Contents | Reader tasks |
|---|---|---|
| SpatialFiltering/geometric_transforms ("Geometric Transforms") | Picks up coord_ops' loose ends. Homogeneous coordinates; the affine family on a letter F; composition and order (rotate-then-translate vs the reverse; rotation about a point as T R T⁻¹); `warp` with `AffineTransform` and the `.inverse` gotcha shown side by side; rotate/scale sliders; projective transforms, with the 8×8 linear system for a homography solved by hand and checked against `ProjectiveTransform.estimate`; rectifying skimage's `text` photo. | 🔨 rectify your own photo. 🧠 which transforms commute; affine from 3 points; registration. |
| SpatialFiltering/edge_detection ("Gradient Maps and Edge Detection") | Gradient magnitude, and direction shown as hue; noise (sky gradient ×10 at 5% noise) and smoothing at σ = 1, 2, 4 (derivative of Gaussian, linked to filters_explore3D); Canny step by step: vectorized non-maximum suppression, then double threshold and hysteresis via `ndimage.label`; comparison with `skimage.feature.canny` (same outlines, differences mostly in the grass); σ/threshold sliders. | 🔨 tune Canny on a noisy image. 🧠 direction histograms; interpolated NMS; color edges. |
| Segmentation/otsu_threshold ("Otsu's Method") | Thresholding; Otsu derived (within- vs between-class variance) and implemented with cumulative sums (matches `threshold_otsu`: 107 on `coins`); separability; threshold slider; global failure on `page` (dark-side paper is darker than bright-side ink) and `threshold_local`. | 🔨 count the coins with `ndimage.label`. 🧠 multi-Otsu; noise and smoothing; color channels. |
| BlockTransform/haar_wavelets ("Haar Wavelets") | From the pixel-pair step to the 1D transform (repeated steps equal `make_haar_matrix`, checked); 2D subbands and the pyramid; energy (approximation: 1.6% of coefficients, 97.7% of the energy); inverse; global keep-the-largest compression (20%: 45.6 dB, 5%: 35.9 dB, 1%: 28.5 dB, with Haar blockiness explained); slider; JPEG 2000. Whole image, not per block (⚑12). | 🔨 denoising by shrinking detail coefficients vs Gaussian blur. 🧠 block/pyramid equivalence; YCbCr; PyWavelets. |
| BlockTransform/reconstruction_comparison ("Comparing Reconstruction Efficiency") | Blocks as 64-vectors, bases as Kronecker products; Parseval (PSNR from dropped energy, checked against an actual block reconstruction); the 64-D KLT (and `make_klt_basis`'s separable version); PSNR curves for all six bases (DCT within 0.07–0.35 dB of each image's own KLT on four images; a borrowed KLT is no better than the DCT); KLT vs DCT patterns; why JPEG chose the DCT. Covers the TOC's KLT entry. | 🔨 beat the DCT by 1 dB (checked feasible: photos and skimage textures only get about 0.5 dB, so the guidance points to synthetic images). 🧠 adaptive selection; block size; color. |
| FFT/dft_intro ("The Discrete Fourier Transform") | Euler's formula and sampled phasors; the DFT matrix next to the DCT's, checked against `np.fft.fft` and FF^H = NI; magnitude and phase of a shifted cosine; aliasing (7 Hz sampled at 8 Hz equals 1 Hz) linked to moiré and anti-aliasing; a 10-line recursive radix-2 FFT with timing (the prose is machine-independent: the timing curves were bumpy); separable 2D, then on to fft_intro. Now first in the Fourier section of the TOC. | 🔨 find three hidden tones in noise. 🧠 spectral leakage; DCT vs DFT on a ramp; circular convolution. |

## Phase 4: publishing (not started)

Your decision on ⚑5: dataset/GPU notebooks are published with committed outputs; datasets stay out of the repo. Open question on the mechanism: ⚑14. The plan is Jupyter Book 2 (`myst.yml` mirroring the TOC), a GitHub Actions workflow that builds and deploys to GitHub Pages, Colab launch links on each page, and retiring the Jekyll `_config.yml`. Deploying is outward-facing, so I'll set it up for your review rather than push.

## Commit index

Generated with `git log --reverse --format='%h %s' main..book-revision`; see that command for the current list.
