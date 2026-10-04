"""
Book consistency check.

1. Cross-checks the notebook links in TOC.ipynb against the notebooks on disk:
   every link should resolve, and every notebook should be linked.
2. Executes notebooks headless (outputs are discarded, never written back) and
   reports which ones fail.

Usage:
    uv run python scripts/check_book.py               # links + execute everything
    uv run python scripts/check_book.py --no-exec     # links only
    uv run python scripts/check_book.py PCA/*.ipynb   # execute a subset
"""

import argparse
import json
import re
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK_RE = re.compile(r'\]\((\./)?([^)#\s]+\.ipynb)(#[^)]*)?\)')


def book_notebooks():
    return sorted(p.relative_to(ROOT).as_posix() for p in ROOT.glob('*/*.ipynb')
                  if '.ipynb_checkpoints' not in p.parts)


def toc_links():
    toc = json.loads((ROOT / 'TOC.ipynb').read_text())
    text = '\n'.join(''.join(c['source']) for c in toc['cells'] if c['cell_type'] == 'markdown')
    return [m.group(2) for m in LINK_RE.finditer(text)]


def check_links():
    links = toc_links()
    notebooks = set(book_notebooks())
    ok = True
    missing = [link for link in links if not (ROOT / link).exists()]
    for link in missing:
        print(f'  BROKEN TOC LINK: {link}')
    dupes = sorted({link for link in links if links.count(link) > 1})
    for link in dupes:
        print(f'  DUPLICATE TOC LINK: {link}')
    unlinked = sorted(notebooks - set(links))
    for nb in unlinked:
        print(f'  NOT IN TOC: {nb}')
    ok = not (missing or unlinked)
    print(f'TOC: {len(links)} links, {len(missing)} broken, {len(dupes)} duplicated, '
          f'{len(unlinked)} notebooks unlinked.')
    return ok


def run_notebook(relpath, timeout):
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError, CellTimeoutError

    path = ROOT / relpath
    nb = nbformat.read(path, as_version=4)
    client = NotebookClient(nb, timeout=timeout, kernel_name='python3',
                            resources={'metadata': {'path': str(path.parent)}})
    start = time.time()
    try:
        client.execute()
        return relpath, 'ok', time.time() - start, ''
    except CellTimeoutError:
        return relpath, 'TIMEOUT', time.time() - start, f'cell exceeded {timeout}s'
    except CellExecutionError as e:
        # Keep the last line of the traceback: usually the exception message.
        lines = [line for line in str(e).strip().splitlines() if line.strip()]
        return relpath, 'FAIL', time.time() - start, lines[-1] if lines else repr(e)
    except Exception as e:  # noqa: BLE001 -- kernel death etc.
        return relpath, 'ERROR', time.time() - start, repr(e)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('notebooks', nargs='*', help='notebooks to execute (default: all)')
    parser.add_argument('--no-exec', action='store_true', help='only check TOC links')
    parser.add_argument('--timeout', type=int, default=600, help='per-cell timeout (s)')
    parser.add_argument('-j', '--jobs', type=int, default=4, help='parallel notebooks')
    args = parser.parse_args()

    links_ok = check_links()
    if args.no_exec:
        return 0 if links_ok else 1

    targets = ([Path(n).resolve().relative_to(ROOT).as_posix() for n in args.notebooks]
               or book_notebooks())
    print(f'\nExecuting {len(targets)} notebooks ({args.jobs} at a time)...')
    failures = 0
    with ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run_notebook, t, args.timeout) for t in targets]
        for fut in futures:
            relpath, status, secs, msg = fut.result()
            failures += status != 'ok'
            print(f'  {status:7s} {secs:6.1f}s  {relpath}' + (f'\n           {msg}' if msg else ''),
                  flush=True)
    print(f'\n{len(targets) - failures}/{len(targets)} notebooks executed cleanly.')
    return 0 if (links_ok and failures == 0) else 1


if __name__ == '__main__':
    sys.exit(main())
