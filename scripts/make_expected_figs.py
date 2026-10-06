"""
Expected outputs for the notebooks that need datasets (or a GPU).

Readers without the MNIST, ORL or Yale data, and the published book (built
without them), can't run these notebooks' key cells. This script runs the
notebooks with the data, saves the outputs of every cell tagged
`expected:<name>` to dip_figs/expected/<notebook>/<name>.png (or the tail of
its printed text), and keeps a collapsed "Expected output" block in a markdown
cell right after each tagged cell, so readers can see what the cell should
produce. The notebooks themselves are still saved without outputs.

To mark a cell, give it the tag `expected:<name>` (in VS Code: "Add Cell Tag";
in JupyterLab: the property inspector), with <name> a short file-name-safe
label, unique within the notebook. Then run this script on that notebook.

Usage:
    uv run python scripts/make_expected_figs.py                 # every notebook with tagged cells
    uv run python scripts/make_expected_figs.py NeuralNets/yale_conv.ipynb
    uv run python scripts/make_expected_figs.py --blocks-only   # rebuild the blocks from saved files

Notebooks run one at a time, so the GPU ones don't compete for memory.
"""

import argparse
import base64
import re
import sys
from pathlib import Path

import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError, DeadKernelError

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'dip_figs' / 'expected'
TAG = 'expected:'
BLOCK_TAG = 'expected-output'   # marks the markdown cells this script owns
TEXT_LINES = 12                 # how much of a text-only output to keep


def tagged_names(cell):
    return [t[len(TAG):] for t in cell.get('metadata', {}).get('tags', []) if t.startswith(TAG)]


def is_block(cell):
    return cell.cell_type == 'markdown' and BLOCK_TAG in cell.get('metadata', {}).get('tags', [])


def notebooks_with_tags():
    found = []
    for p in sorted(ROOT.glob('*/*.ipynb')):
        nb = nbformat.read(p, as_version=4)
        if any(tagged_names(c) for c in nb.cells):
            found.append(p)
    return found


def runnable_copy(nb):
    '''Inline figures instead of widgets, so outputs are PNGs; show slider figures at their initial state.'''
    run = nbformat.from_dict(nb)
    for c in run.cells:
        if c.cell_type != 'code':
            continue
        lines = c.source.replace('%matplotlib widget', '%matplotlib inline').split('\n')
        lines = [('pass  # ' + ln) if ln.strip().startswith(('VBox(', 'AppLayout(', 'plt.ioff()')) else ln
                 for ln in lines]
        c.source = '\n'.join(lines)
    return run


def text_of(outputs):
    parts = []
    for o in outputs:
        if o.get('output_type') == 'stream':
            parts.append(o['text'])
        elif 'data' in o and 'text/plain' in o['data'] and 'image/png' not in o['data']:
            parts.append(o['data']['text/plain'] + '\n')
    lines = ''.join(parts).rstrip('\n').split('\n')
    lines = [ln for ln in lines if ln.strip()]
    return '\n'.join((['...'] if len(lines) > TEXT_LINES else []) + lines[-TEXT_LINES:])


def save_outputs(stem, name, outputs):
    '''Write a cell's PNGs (or its text) under dip_figs/expected/<stem>/. Returns the files written.'''
    folder = OUT / stem
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob(f'{name}.*'):
        old.unlink()
    for old in folder.glob(f'{name}_[0-9]*.png'):
        old.unlink()
    pngs = [o['data']['image/png'] for o in outputs if 'data' in o and 'image/png' in o['data']]
    written = []
    for k, png in enumerate(pngs):
        f = folder / (f'{name}.png' if len(pngs) == 1 else f'{name}_{k}.png')
        f.write_bytes(base64.b64decode(png))
        written.append(f)
    if not pngs:
        text = text_of(outputs)
        if text:
            f = folder / f'{name}.txt'
            f.write_text(text + '\n')
            written.append(f)
    return written


def saved_files(stem, name):
    folder = OUT / stem
    files = sorted(folder.glob(f'{name}.png')) + sorted(folder.glob(f'{name}_[0-9]*.png'),
                                                         key=lambda f: int(re.findall(r'_(\d+)\.png$', f.name)[0]))
    return files or sorted(folder.glob(f'{name}.txt'))


def block_source(nb_path, files):
    body = []
    for f in files:
        rel = Path('..') / f.relative_to(ROOT)
        if f.suffix == '.png':
            body.append(f'<img src="{rel.as_posix()}" alt="expected output" style="max-width:100%">')
        else:
            body.append('```text\n' + f.read_text().rstrip('\n') + '\n```')
    return ('<details>\n'
            '<summary><b>Expected output</b> (what the cell above should show, if you can\'t run it)</summary>\n\n'
            + '\n\n'.join(body) + '\n\n</details>')


def update_blocks(nb_path, nb):
    '''Put an up-to-date block after every tagged cell, and drop blocks that no longer follow one.'''
    stem = nb_path.stem
    cells = []
    for c in nb.cells:
        if is_block(c):
            continue                       # re-created below where they belong
        cells.append(c)
        for name in tagged_names(c):
            files = saved_files(stem, name)
            if not files:
                print(f'    no saved output for {name}; run without --blocks-only')
                continue
            block = nbformat.v4.new_markdown_cell(block_source(nb_path, files))
            block.metadata['tags'] = [BLOCK_TAG]
            cells.append(block)
    nb.cells = cells
    for c in nb.cells:
        c.pop('id', None)
    nbformat.validate(nb)
    nbformat.write(nb, nb_path)


def run(nb_path):
    nb = nbformat.read(nb_path, as_version=4)
    allow_errors = nb_path.name.startswith(('play_', 'playing_with_'))   # activities stop at unanswered cells
    executed = runnable_copy(nb)
    NotebookClient(executed, timeout=3600, kernel_name='python3', allow_errors=allow_errors,
                   resources={'metadata': {'path': str(nb_path.parent)}}).execute()
    for c in executed.cells:
        for name in tagged_names(c):
            written = save_outputs(nb_path.stem, name, c.get('outputs', []))
            print(f'    {name}: ' + (', '.join(f.name for f in written) if written else 'NO OUTPUT'))
    update_blocks(nb_path, nb)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('notebooks', nargs='*', help='notebooks to process (default: all with tagged cells)')
    parser.add_argument('--blocks-only', action='store_true', help="don't execute; rebuild blocks from saved files")
    args = parser.parse_args()
    paths = [Path(p).resolve() for p in args.notebooks] or notebooks_with_tags()
    failed = []
    for p in paths:
        print(p.relative_to(ROOT))
        try:
            if args.blocks_only:
                update_blocks(p, nbformat.read(p, as_version=4))
            else:
                run(p)
        except (CellExecutionError, DeadKernelError, TimeoutError, RuntimeError, OSError) as e:
            # Report, and keep going with the other notebooks.
            print(f'    FAILED: {type(e).__name__}: {str(e)[-300:]}')
            failed.append(p)
    sys.exit(1 if failed else 0)


if __name__ == '__main__':
    main()
