# Revision Review: `book-revision` branch

A notebook-by-notebook log of this revision, so you can review the changes in context. Each notebook was changed in its own commit, and `git log --oneline main..book-revision -- <notebook>` shows its commits (the [commit index](#commit-index) at the bottom lists them). To see a notebook's diff rendered rather than as JSON: `uv run nbdiff-web main -- <notebook>`.

Rules followed throughout:
- **No activity answer cells were filled.** Activity notebooks got scaffolding fixes only (links, data paths). Where a planned demo would have answered an activity prompt, I skipped it (see ⚑6).
- Existing content was never deleted except for leftover cells (stray empty cells, self-export `nbconvert` lines, an addressed note-to-self), each noted below. Questionable content is flagged ⚑ for your decision.
- Every notebook executes headless (`uv run python scripts/check_book.py`). Numbers and visual claims in the new prose were checked against rendered figures and actual outputs, and corrected where they didn't hold.
- Prose is drafted in your voice for you to edit freely.

## Open decisions (⚑)

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
| Hardcoded data paths | `/home/dip365/...` and `~/data` paths in 9 notebooks now go through `dip_utils/data_paths.py`. 3 notebooks failed in the baseline because of them. |
| Links | 9 broken relative links, 1 dead hotlinked image, about 25 versioned doc links. |

## Repo-wide commits

| Change | Notes |
|---|---|
| `.claude/CLAUDE.md` | Rewritten for this repo: layout, notebook conventions, the no-solutions rule, workflow. |
| Infrastructure | Added `scikit-learn` and `opencv-python-headless` (used but undeclared) and dev tools (`jupyter`, `nbconvert`, `nbclient`, `nbdime`, `ruff`). New `dip_utils/data_paths.py` (one `DIP_DATA` root, default `~/data`, with helpful errors). New `scripts/check_book.py`: TOC and relative-link checks, plus headless execution. It treats a `NameError` in an activity as expected, and restores `dip_outs/` afterwards. README now describes uv and has a dataset table. Removed placeholder `main.py`. |
| Doc links | Versioned matplotlib/scipy/python/torchvision doc URLs now point at current docs. |
| Relative links | Fixed wrong `./` roots, `vis_utils.py:NNN` line refs, and a stray backtick. |
| TOC | Every notebook is linked (was 19 of 60). New "Using this Book" cell. Unwritten topics marked *(coming soon)*. Duplicate Huffman link fixed. |

**Execution:** 54/60 notebooks ran before the revision. Now all 60 run (play_mnist_correlate stops at its unanswered activity cell, as designed).

## Per-notebook changes

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

## Phase 3: proposed new notebooks (outlines for your approval)

Each would follow the book's conventions, with prose in your voice and activity prompts left empty for students.

1. **SpatialFiltering/geometric_transforms.ipynb** ("Geometric Transforms"): affine matrices in homogeneous coordinates (translate, rotate, scale, shear, composing them); warping with `skimage.transform.warp` and `AffineTransform`; interpolation orders compared; a projective homography (rectifying a photographed page or sign); a slider for rotation and scale. *Activity:* rectify a perspective photo by picking 4 corners.
2. **SpatialFiltering/edge_detection.ipynb** ("Gradient Maps and Edge Detection", plus the TOC's Canny entry): gradient magnitude and direction; noise sensitivity, and why we smooth first (derivative of Gaussian, linking to filters_explore3D); Canny step by step (smoothing, gradients, non-maximum suppression, double threshold, hysteresis), implemented simply and then compared to `skimage.feature.canny`; σ and threshold sliders. *Activity:* tune Canny on a noisy image.
3. **Segmentation/otsu_threshold.ipynb** ("Otsu's Method"): thresholding from histograms (linking to enhance_histeq); Otsu's between-class variance derived and implemented from the histogram, checked against `skimage.filters.threshold_otsu`; where global thresholding fails (uneven lighting) → local/adaptive thresholds. *Activity:* segment coins or text.
4. **BlockTransform/haar_wavelets.ipynb** ("Haar Wavelets"): from the pixel-pair averages/differences in intro_spatial_coherence to the 1D Haar transform; multilevel 2D decomposition (the familiar quadrant pyramid) using `wavelet_utils`; compression by keeping the largest coefficients; how this relates to JPEG 2000.
5. **BlockTransform/reconstruction_comparison.ipynb** ("Comparing Reconstruction Efficiency"): on 8×8 blocks of several images, PSNR versus fraction of coefficients kept, for the standard, random, Haar, DCT and KLT bases (all in `wavelet_utils`); shows KLT best on its own image, DCT close behind on any image, and why JPEG chose DCT. Also covers the TOC's "Karhunen-Loève Transform and Compression".
6. **FFT/dft_intro.ipynb** ("Discrete Fourier Transform"): the 1D DFT as a change of basis (the DFT matrix, built and visualized like `make_dct_matrix`); complex exponentials as rotating phasors; magnitude/phase of simple signals; sampling and aliasing; the FFT as a fast algorithm (timing O(N²) vs O(N log N)); bridge to 2D in fft_intro.

The TOC's "Communication, Compression, and Perception" (Entropy chapter) and the "Face Recognition" entry are covered or partly covered by existing material, so I don't propose new notebooks for them unless you want one.

## Phase 4: publishing (not started)

Waiting on ⚑5. The plan is Jupyter Book 2 (`myst.yml` mirroring the TOC), a GitHub Actions workflow that builds and deploys to GitHub Pages, Colab launch links on each page, and retiring the Jekyll `_config.yml`. Deploying is outward-facing, so I'll set it up for your review rather than push.

## Commit index

Generated with `git log --reverse --format='%h %s' main..book-revision`; see that command for the current list.
