"""
Build the book's website with Jupyter Book 2 (MyST).

The notebooks are written for interactive use: `%matplotlib widget` figures,
sliders, and datasets that live outside the repository. This script stages a
copy of the book in _site/, adapted for a static website, and builds it there.
The notebooks in the repository are never modified.

- myst.yml is generated from TOC.ipynb, so the site's navigation always matches
  the book's table of contents, labels included ("🔨 exercise: ...").
- Figures are drawn inline, in their starting state (see static_nb.py). Sliders
  can't respond on a static page; readers run the notebooks for that.
- Notebooks that need a dataset or a GPU (those with `expected:` cells) and the
  exercises are not executed. The dataset notebooks show their "Expected output"
  blocks instead, turned into MyST dropdowns.
- Anchors written as <a id='name'></a> become MyST labels. MyST labels are
  shared by the whole project, so each gets its notebook's name as a prefix,
  (notebook-name)=, and links to it, in the same notebook or another, are
  rewritten to match.

Usage:
    uv run python scripts/build_site.py                # stage, execute, build into _site/_build/html
    uv run python scripts/build_site.py --stage        # only stage _site/ (then e.g. `jupyter-book start` there)
    BASE_URL=/imageprocessing-awesome uv run python scripts/build_site.py   # as served on GitHub Pages
"""

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import nbformat
import yaml
from static_nb import make_static

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / '_site'
REPO_URL = 'https://github.com/profstough/imageprocessing-awesome'

# Copied into the staging folder besides the chapter folders.
SUPPORT = ['dip_pics', 'dip_figs', 'dip_utils', 'dip_outs', 'cc-license.png',
           'README.md', 'private_fork_instructions.md', 'colab_setup.ipynb']
# Pages linked from the TOC notebook, shown at the end of the site. Notebooks here are not executed.
EXTRA_PAGES = [('README.md', 'About the Repository'),
               ('private_fork_instructions.md', 'Making a Private Fork'),
               ('colab_setup.ipynb', 'Running in Colab')]
# Added to the home page's <head> after the build; the theme has no option for custom tags.
# Google Search Console checks this one to verify that we own the site.
HEAD_TAGS = ['<meta name="google-site-verification" content="ZGLircp48Kj8i7a3afTlN3-K_UGnEjov1ia8QoVELBQ" />']

ITEM_RE = re.compile(r'^( *)1\. (.*?)\s*$')
LINK_RE = re.compile(r'\[(.*?)\]\((?:\./)?([^)#\s]+\.ipynb)\)')
ANCHOR_RE = re.compile(r'''<a id=['"]([\w-]+)['"]>\s*</a>[ \t]*\n(?:[ \t]*\n)*''')
TARGET_RE = re.compile(r'\]\(([^)\s#]*)#([\w-]+)\)')


# ---------------------------------------------------------------- the TOC

def toc_items():
    '''Parse the numbered "Topics" list of TOC.ipynb into (level, label, file or None).'''
    toc = nbformat.read(ROOT / 'TOC.ipynb', as_version=4)
    topics = next(c.source for c in toc.cells if c.cell_type == 'markdown' and '# Topics' in c.source)
    items = []
    for line in topics.split('\n'):
        m = ITEM_RE.match(line)
        if not m:
            continue
        level, text = len(m[1]) // 4, m[2]
        link = LINK_RE.search(text)
        if link:
            items.append((level, link[1].replace('\\*', '*'), link[2]))
        else:
            items.append((level, re.sub(r'\*\*|\\', '', text).strip(), None))
    return items


def myst_toc(items):
    '''Nest the parsed items into a MyST toc; unlinked items become groups (or are dropped if empty).'''
    root = {'children': []}
    stack = [(-1, root)]
    for level, label, file in items:
        while stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1]
        entry = {'file': file} if file else {'title': label, 'children': []}
        parent.setdefault('children', []).append(entry)   # a page can have child pages too
        stack.append((level, entry))

    def prune(entries):
        kept = []
        for e in entries:
            if 'children' in e:
                e['children'] = prune(e['children'])
                if not e['children']:
                    if 'file' not in e:
                        continue    # e.g. "(coming soon)" or "see ... under ..." notes
                    del e['children']
            kept.append(e)
        return kept

    return [{'file': 'TOC.ipynb'}, *prune(root['children']),
            {'title': 'About', 'children': [{'file': f} for f, _ in EXTRA_PAGES]}]


def write_myst_yml(toc):
    config = {
        'version': 1,
        'project': {
            'title': 'Digital Image Processing in Python',
            'authors': [{'name': 'Joshua Stough', 'url': 'http://joshuastough.com/'}],
            'license': 'CC-BY-SA-4.0',
            'github': REPO_URL,
            'toc': toc,
            'settings': {'output_matplotlib_strings': 'remove'},
        },
        'site': {
            'template': 'book-theme',
            'options': {'logo_text': 'Digital Image Processing in Python'},
        },
    }
    with open(SITE / 'myst.yml', 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------- notebooks

def to_dropdown(source):
    '''Turn an "Expected output" <details> block into a MyST dropdown.'''
    m = re.match(r'<details>\n<summary>(.*?)</summary>\n\n(.*)\n\n</details>\s*$', source, re.DOTALL)
    if not m:
        return source
    summary = re.sub(r'<code>(.*?)</code>', r'`\1`', m[1])
    summary = re.sub(r'<[^>]+>', '', summary)
    body = re.sub(r'<img src="([^"]+)"[^>]*>', r'![expected output](\1)', m[2])
    return f':::{{dropdown}} {summary}\n{body}\n:::'


def anchors_by_notebook(files):
    '''{notebook stem: set of its <a id> anchors}. Stems must be unique, since they prefix the labels.'''
    anchors = {}
    for f in files:
        stem = Path(f).stem
        assert stem not in anchors, f'two notebooks named {stem}'
        text = '\n'.join(c.source for c in nbformat.read(ROOT / f, as_version=4).cells)
        anchors[stem] = set(ANCHOR_RE.findall(text))
    return anchors


def retarget(m, path, anchors):
    '''Point a link to an anchor at its prefixed label: [..](#name) or [..](other.ipynb#name).'''
    target, name = m[1], m[2]
    stem = path.stem if not target else Path(target).stem if target.endswith('.ipynb') else None
    if stem in anchors and name in anchors[stem]:
        return f'](#{stem}-{name})'
    return m[0]


def stage_notebook(path, label, anchors, execute=True):
    nb = nbformat.read(path, as_version=4)
    needs_data = any(t.startswith('expected:') for c in nb.cells for t in c.get('metadata', {}).get('tags', []))
    is_exercise = path.name.startswith(('play_', 'playing_with_'))
    make_static(nb)
    for c in nb.cells:
        if c.cell_type != 'markdown':
            continue
        c.source = ANCHOR_RE.sub(lambda m: f'({path.stem}-{m[1]})=\n', c.source)
        c.source = TARGET_RE.sub(lambda m: retarget(m, path, anchors), c.source)
        if 'expected-output' in c.get('metadata', {}).get('tags', []):
            c.source = to_dropdown(c.source)
    front = {'short_title': label}
    if needs_data or is_exercise or not execute:
        front['execute'] = {'skip': True}
    front_cell = nbformat.v4.new_markdown_cell('---\n' + yaml.safe_dump(front, allow_unicode=True) + '---')
    nb.cells.insert(0, front_cell)
    for c in nb.cells:
        c.pop('id', None)
    nbformat.write(nb, path)


def stage():
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    items = toc_items()
    chapters = sorted({Path(f).parts[0] for _, _, f in items if f})
    ignore = shutil.ignore_patterns('.ipynb_checkpoints', '__pycache__')
    for name in chapters + SUPPORT:
        src = ROOT / name
        if src.is_dir():
            shutil.copytree(src, SITE / name, ignore=ignore)
        else:
            shutil.copy2(src, SITE / name)
    shutil.copy2(ROOT / 'TOC.ipynb', SITE / 'TOC.ipynb')

    files = [f for _, _, f in items if f]
    anchors = anchors_by_notebook([*files, 'TOC.ipynb'])
    for _, label, file in items:
        if file:
            stage_notebook(SITE / file, label, anchors)
    stage_notebook(SITE / 'TOC.ipynb', 'Contents', anchors)
    for file, title in EXTRA_PAGES:
        p = SITE / file
        if p.suffix == '.ipynb':
            stage_notebook(p, title, anchors, execute=False)
        else:
            p.write_text(f'---\ntitle: {title}\n---\n\n' + p.read_text())

    write_myst_yml(myst_toc(items))
    print(f'staged {sum(1 for _ in SITE.glob("*/*.ipynb"))} notebooks in {SITE.relative_to(ROOT)}/')


def add_head_tags(page):
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html:
        sys.exit(f'no </head> in {page}')
    tags = ''.join(tag for tag in HEAD_TAGS if tag not in html)
    page.write_text(html.replace('</head>', tags + '</head>', 1), encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stage', action='store_true', help='only stage _site/, without building')
    args = parser.parse_args()
    stage()
    if not args.stage:
        result = subprocess.run(['jupyter-book', 'build', '--html', '--execute'], cwd=SITE, check=False)
        if result.returncode == 0:
            add_head_tags(SITE / '_build' / 'html' / 'index.html')
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()
