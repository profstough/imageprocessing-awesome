"""
Header figures: a preview, under each notebook's title, of what the notebook does.

The figure is the notebook's own output: tag the code cell that best shows what
the notebook is about (in VS Code: "Add Cell Tag"; in JupyterLab: the property
inspector) with `header`. This script runs the notebook up to and including that
cell, saves the cell's last figure to dip_figs/headers/<notebook>.jpg, and keeps
an <img> line for it in the first cell, after the "stough 202-" line. On the
website, a page's first image is also its preview card, so this gives every
chapter a thumbnail.

Interactive cells are captured in their starting state. As in
make_expected_figs.py, code in the tagged cell's metadata under
`header_snapshot` (e.g. "slider.value = 10") is appended when this script runs
the cell, to capture a more telling state.

Exercises have nothing to run, and their header must never show an answer. For
them, put self-contained code that draws the *problem* (e.g. the kinds of
images the reader will work on) in the notebook's metadata under `header_code`;
it runs on its own, from the notebook's folder, with dip_utils importable.

Usage:
    uv run python scripts/make_header_figs.py                   # every notebook with a header
    uv run python scripts/make_header_figs.py Enhancement/enhance_transfer.ipynb
    uv run python scripts/make_header_figs.py --lines-only      # only update the <img> lines
"""

import argparse
import re
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, DeadKernelError
from static_nb import make_static

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dip_figs' / 'headers'
TAG = 'header'
WIDTH = 600   # display width (px) in the notebook and on the website
DPI = 150
QUALITY = 85   # JPEG: a tenth the size of a PNG for these mostly photographic figures
IMG_RE = re.compile(r'<img src="\.\./dip_figs/headers/[^"]*"[^>]*>\n*')
SETUP = "%matplotlib inline\nimport matplotlib.pyplot as plt\nimport sys\nsys.path.insert(0, '../dip_utils')"


def header_index(nb):
    tagged = [i for i, c in enumerate(nb.cells) if c.cell_type == 'code' and TAG in c.get('metadata', {}).get('tags', [])]
    if len(tagged) > 1:
        raise RuntimeError(f'{len(tagged)} cells are tagged {TAG!r}; tag one')
    return tagged[0] if tagged else None


def has_header(nb):
    return header_index(nb) is not None or 'header_code' in nb.metadata


def notebooks_with_headers():
    found = []
    for p in sorted(ROOT.glob('*/*.ipynb')):
        if p.relative_to(ROOT).parts[0].startswith(('_', '.')):   # e.g. the _site/ build
            continue
        if has_header(nbformat.read(p, as_version=4)):
            found.append(p)
    return found


def save_code(fig_path):
    return (f"\n\nplt.gcf().savefig({str(fig_path)!r}, dpi={DPI}, bbox_inches='tight', "
            f"facecolor='white', pil_kwargs={{'quality': {QUALITY}}})")


def runnable_copy(nb, fig_path):
    '''The cells up to the header cell, with inline figures, ending by saving its figure;
    or, for an exercise, just its header_code.'''
    i = header_index(nb)
    if i is None:
        run = nbformat.v4.new_notebook()
        run.cells = [nbformat.v4.new_code_cell(SETUP),
                     nbformat.v4.new_code_cell(nb.metadata['header_code'] + save_code(fig_path))]
        return run
    run = make_static(nbformat.from_dict(nb))
    run.cells = run.cells[:i + 1]
    cell = run.cells[i]
    snapshot = cell.get('metadata', {}).get('header_snapshot')
    if snapshot:
        cell.source += '\n\n' + snapshot
    cell.source += save_code(fig_path)
    return run


def title_of(nb):
    m = re.search(r'^# (.+)$', nb.cells[0].source, re.MULTILINE)
    return m[1].strip() if m else 'this notebook'


def update_line(nb_path, nb):
    '''Put the <img> line in the first cell, after "stough 202-" (or after the title block).'''
    fig_path = OUT / f'{nb_path.stem}.jpg'
    if not fig_path.exists():
        print('    no saved figure; run without --lines-only')
        return
    rel = (Path('..') / fig_path.relative_to(ROOT)).as_posix()
    img = f'<img src="{rel}" alt="Preview: {title_of(nb)}" width="{WIDTH}"/>'
    lines = IMG_RE.sub('', nb.cells[0].source).split('\n')
    at = next((k + 1 for k, ln in enumerate(lines) if ln.startswith('stough 20')), None)
    if at is None:   # no byline: after the leading headings and notes
        at = next((k for k, ln in enumerate(lines) if ln.strip() and not ln.startswith(('#', '>'))), len(lines))
    nb.cells[0].source = '\n'.join(lines[:at] + ['', img, ''] + lines[at:]).replace('\n\n\n', '\n\n')
    for c in nb.cells:
        c.pop('id', None)
    nbformat.validate(nb)
    nbformat.write(nb, nb_path)


def run(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    OUT.mkdir(parents=True, exist_ok=True)
    fig_path = OUT / f'{nb_path.stem}.jpg'
    fig_path.unlink(missing_ok=True)
    NotebookClient(runnable_copy(nb, fig_path), timeout=1800, kernel_name='python3',
                   resources={'metadata': {'path': str(nb_path.parent)}}).execute()
    print(f'    {fig_path.relative_to(ROOT)}' if fig_path.exists() else '    NO FIGURE')
    update_line(nb_path, nb)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('notebooks', nargs='*', help='notebooks to process (default: all with a header)')
    parser.add_argument('--lines-only', action='store_true', help="don't execute; only update the <img> lines")
    args = parser.parse_args()
    paths = [Path(p).resolve() for p in args.notebooks] or notebooks_with_headers()
    failed = []
    for p in paths:
        print(p.relative_to(ROOT))
        try:
            if args.lines_only:
                update_line(p, nbformat.read(p, as_version=4))
            else:
                run(p)
        except (CellExecutionError, DeadKernelError, TimeoutError, RuntimeError, OSError, KeyError) as e:
            # Report, and keep going with the other notebooks.
            print(f'    FAILED: {type(e).__name__}: {str(e)[-300:]}')
            failed.append(p)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
