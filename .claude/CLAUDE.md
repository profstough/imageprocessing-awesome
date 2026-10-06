# Agent Instructions for imageprocessing-awesome

This repo is an interactive textbook, *Digital Image Processing in Python* (Joshua Stough), written as Jupyter notebooks. The audience is undergraduates. Readers run the notebooks locally (uv + VS Code/JupyterLab) or in Colab.

## Hard rule: never solve activities
- Activity notebooks (`play_*.ipynb`, `playing_with_*.ipynb`) and activity/exercise sections inside demo notebooks contain **intentionally empty answer cells**. Never fill them in, sketch solutions, or add hints that give the answer away.
- In activity notebooks you may change scaffolding only: imports, data paths, broken links, typos in the prompts.
- New notebooks may include activity *prompts* followed by empty code cells.

## Layout
- `TOC.ipynb`: front matter and the table of contents (the book's index). Every notebook should be linked from it.
- `<Chapter>/`: one folder per topic (NumpyAndVisualization, SensingSamplingQuantization, Color, Enhancement, Entropy, SpatialFiltering, Segmentation, BlockTransform, FFT, PCA, SLIC, Radon, NeuralNets, ...).
- `dip_utils/`: shared helpers imported by the notebooks:
  - `vis_utils.py`: `vis_image`, `vis_pair`, `vis_triple`, `vis_hists`, `vis_rgb_cube`/`vis_hsv_cube`/`vis_lab_cube`/`vis_ybr_cube`, `vis_surface`, `vis_blocks`
  - `matrix_utils.py`: `arr_info`
  - `wavelet_utils.py`: Haar/DCT/standard/random/KLT basis matrices
  - `huff_utils.py`, `huffnode.py`: Huffman coding
  - `data_paths.py`: dataset locations
- `dip_pics/`: input images. `dip_figs/`: explanatory figures (`dip_figs/expected/`: generated expected outputs, see below). `dip_outs/`: generated outputs.
- Datasets (MNIST, ORL, Yale) live outside the repo under `$DIP_DATA` (default `~/data`). Notebooks must get their paths from `dip_utils/data_paths.py`, never from hardcoded absolute paths.

## Notebook conventions (match these when editing or writing)
- The first cell is markdown: `# Title`, then an optional `## Subtitle`, then `stough 202-`, then a numbered list of anchor links to the sections (`<a id='name'></a>` placed before each section header).
- Imports cell:
  ```python
  %matplotlib widget
  import matplotlib.pyplot as plt
  import numpy as np
  import sys
  sys.path.insert(0, '../dip_utils')
  from matrix_utils import arr_info
  from vis_utils import (vis_pair, ...)
  ```
  The torch notebooks may use `%matplotlib inline`.
- Load images with relative paths: `plt.imread('../dip_pics/<name>')`.
- Display equations in `\begin{equation*} ... \end{equation*}`; inline math in `$...$`.
- Put `&nbsp;` on its own line before major section headers, for spacing.
- Interactive demos follow the pattern `plt.ioff()` → figure + `ipywidgets` slider → `slider.observe(update)` → `VBox([slider, fig.canvas])`.
- Voice: first person, conversational, explains *why* as well as *what*. After an important code cell, add a markdown cell that walks through it. Link back to earlier chapters with relative links (`../Chapter/notebook.ipynb`). The model voice is `Enhancement/enhance_transfer.ipynb`.
- Reader tasks come in two consistent forms, both anchored, listed in the first-cell contents list when the notebook has one, and preceded by `&nbsp;`:
  - **In-flow tasks**: `## 🔨 Your Turn: <Task>`, a sentence or two of motivation, `**Task:**` (what to produce and how to tell it worked), `**Guidance:**` (bullets: functions/docs to use, pitfalls, how to check), then one or more empty code cells. Later cells must not depend on the answer.
  - **End-of-notebook problem sets**: `## 🧠 Further Efforts` (anchor `further`), one framing sentence, then a numbered list of `**Title.**` prompts, each with a `*Guidance:*` line.
  - Guidance is explicit enough for a reader working alone, but it never gives the answer away (no solution code, no "the answer is").
- Reuse `dip_utils` helpers before writing new ones. Add a helper to `dip_utils` only when several notebooks need it.

## Environment & commands
- Package manager: `uv` (`uv sync`; `uv add <pkg>`; dev tools with `uv add --dev`). Use the `.venv` kernel.
- PyTorch is installed from the CUDA 12.6 index (see `pyproject.toml`). Notebooks must still run on CPU, so guard GPU use with `torch.cuda.is_available()`.
- Lint helpers: `uv run ruff check dip_utils scripts`.
- Book check: `uv run python scripts/check_book.py`. It cross-checks TOC links against notebook files and executes notebooks headless. Use `--no-exec` for links only, or pass notebook paths to run a subset.
- Expected outputs: in notebooks that need a dataset or GPU, key cells carry the tag `expected:<name>`. `uv run python scripts/make_expected_figs.py [notebook ...]` runs them with the data, saves those cells' figures (or printed text) to `dip_figs/expected/<notebook>/`, and maintains the collapsed "Expected output" markdown cell (tag `expected-output`) after each one. Don't edit those markdown cells by hand; re-run the script after changing a tagged cell or anything before it. `--blocks-only` rebuilds the cells without executing.
- Review notebook diffs with `uv run nbdiff-web main -- <notebook>`.

## Workflow
- Clear outputs before committing (`uv run jupyter nbconvert --clear-output --inplace <nb>`), so diffs show source only.
- Revisions are reviewed notebook by notebook: one commit per notebook, with the message `<Chapter>/<notebook>: <summary>`. Record each change and open questions in `REVISION_REVIEW.md` while a revision branch is active.
- Flag questionable existing content for Josh instead of deleting it.
