"""
Build the book's website with Jupyter Book 2 (MyST).

The notebooks are written for interactive use: `%matplotlib widget` figures,
sliders, and datasets that live outside the repository. This script stages a
copy of the book in _site/, adapted for a static website, and builds it there.
The notebooks in the repository are never modified.

- myst.yml is generated from TOC.ipynb, so the site's navigation always matches
  the book's table of contents, labels included ("🔨 exercise: ...").
- On the home page, the Topics list becomes galleries of the notebooks' header
  figures (topics_gallery, styled by site.css).
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
import os
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
SITE_DOMAIN = 'https://profstough.github.io'   # GitHub Pages; BASE_URL adds the repo's path

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
IMG_RE = re.compile(r'<img\b[^>]*>|!\[[^\]]*\]\([^)]*\)')
COMMENT_RE = re.compile(r'<!--.*?-->', re.DOTALL)


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


def topics_gallery(items):
    """The home page's Topics list as galleries of header figures, one per chapter, each figure
    linking to its notebook (styled by site.css). On a phone there is no hover to show the
    previews, and an image processing book should open with images.

    Unlinked items are groups (a heading, when a chapter has only groups; otherwise their
    pages simply join the chapter's gallery) or notes ("coming soon", "see ... under ...")."""
    root = {'children': []}
    stack = [(-1, root)]
    for level, label, file in items:
        while stack[-1][0] >= level:
            stack.pop()
        node = {'label': label, 'file': file, 'children': []}
        stack[-1][1]['children'].append(node)
        stack.append((level, node))

    def cards(nodes):
        out, notes = [], []
        for n in nodes:
            if n['file']:
                kind, title = re.match(r'(?:(🔨 exercise|demo|extra): )?(.*)', n['label']).groups()
                title = title.replace('*', r'\*')   # L*a*b*
                stem = Path(n['file']).stem
                out.append(f'[![](dip_figs/headers/{stem}.jpg){f"*{kind}* " if kind else ""}'
                           f'**{title}**](./{n["file"]})')
            elif not n['children']:
                notes.append(n['label'])
            sub_out, sub_notes = cards(n['children'])
            out += sub_out
            notes += sub_notes
        return out, notes

    def gallery(nodes):
        out, notes = cards(nodes)
        block = [':::{div}', ':class: toc-gallery', *out, ':::', ''] if out else []
        return block + [f'{note}\n' for note in notes]

    lines = []
    for k, chapter in enumerate(root['children'], 1):
        lines.append(f'## {k}. {chapter["label"]}\n')
        if any(n['file'] for n in chapter['children']):
            lines += gallery(chapter['children'])
            continue
        for n in chapter['children']:
            if n['children']:
                lines += [f'### {n["label"]}\n', *gallery(n['children'])]
            else:
                lines.append(f'{n["label"]}\n')
    return '\n'.join(lines)


def write_myst_yml(toc):
    config = {
        'version': 1,
        'project': {
            'title': 'Digital Image Processing in Python',
            'authors': [{'name': 'Joshua Stough', 'url': 'https://profstough.github.io/'}],
            'license': 'CC-BY-SA-4.0',
            'github': REPO_URL,
            'toc': toc,
            'settings': {'output_matplotlib_strings': 'remove'},
        },
        'site': {
            # Follows each page's title in the browser tab and link previews; with the project
            # title it read "Digital Image Processing in Python - Digital Image Processing in Python".
            'title': 'imageprocessing-awesome',
            'template': 'book-theme',
            'options': {'logo_text': 'Digital Image Processing in Python', 'style': 'site.css'},
        },
    }
    with open(SITE / 'myst.yml', 'w') as f:
        yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)


# ---------------------------------------------------------------- notebooks

def separate_images(source):
    """Give each image its own paragraph. The theme shrinks images that share a paragraph
    to inline slivers, so side-by-side images (fine in Jupyter and VS Code) are stacked."""
    paras = re.split(r'(\n\s*\n)', source)
    for k, para in enumerate(paras):
        imgs = IMG_RE.findall(para)
        if len(imgs) > 1 and not IMG_RE.sub('', COMMENT_RE.sub('', para)).strip():
            paras[k] = '\n\n'.join(imgs)
    return ''.join(paras)


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


def source_links(path):
    """Page frontmatter: no "edit" pencil for readers, and the "source" link points at the
    file in the repository (by default both would point into _site/, which isn't in it)."""
    return {'edit_url': None, 'source_url': f'{REPO_URL}/blob/main/{path.relative_to(SITE).as_posix()}'}


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
        c.source = separate_images(c.source)
        if 'expected-output' in c.get('metadata', {}).get('tags', []):
            c.source = to_dropdown(c.source)
    front = {'short_title': label, **source_links(path)}
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
    shutil.copy2(ROOT / 'scripts' / 'site.css', SITE / 'site.css')
    toc = nbformat.read(ROOT / 'TOC.ipynb', as_version=4)
    topics = next(c for c in toc.cells if c.cell_type == 'markdown' and '# Topics' in c.source)
    topics.source = topics.source[:topics.source.index('\n1. ')] + '\n\n' + topics_gallery(items)
    nbformat.write(toc, SITE / 'TOC.ipynb')

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
            front = yaml.safe_dump({'title': title, **source_links(p)}, allow_unicode=True)
            p.write_text(f'---\n{front}---\n\n' + p.read_text())

    write_myst_yml(myst_toc(items))
    print(f'staged {sum(1 for _ in SITE.glob("*/*.ipynb"))} notebooks in {SITE.relative_to(ROOT)}/')


def add_head_tags(page):
    html = page.read_text(encoding='utf-8')
    if '</head>' not in html:
        sys.exit(f'no </head> in {page}')
    tags = ''.join(tag for tag in HEAD_TAGS if tag not in html)
    page.write_text(html.replace('</head>', tags + '</head>', 1), encoding='utf-8')


def fix_sitemap(html_dir):
    """The static export fetches every page from a temporary local server, so the
    sitemap's links (and robots.txt's pointer to it) come out as localhost:3000.
    Point them at the published site."""
    site_url = SITE_DOMAIN + os.environ.get('BASE_URL', '')
    for name in ('sitemap.xml', 'robots.txt'):
        path = html_dir / name
        text = path.read_text(encoding='utf-8')
        path.write_text(re.sub(r'http://localhost:\d+', site_url, text), encoding='utf-8')


def absolute_preview_images(html_dir):
    """Each page's preview image (og:image, read by Slack, Messages, LinkedIn, ...) comes out
    as a path within the site; link previews need the full address."""
    og = re.compile(r'(<meta property="og:image" content=")(/[^"]*")')
    for page in html_dir.rglob('*.html'):
        html = page.read_text(encoding='utf-8')
        fixed = og.sub(lambda m: m[1] + SITE_DOMAIN + m[2], html)
        if fixed != html:
            page.write_text(fixed, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--stage', action='store_true', help='only stage _site/, without building')
    args = parser.parse_args()
    stage()
    if not args.stage:
        result = subprocess.run(['jupyter-book', 'build', '--html', '--execute'], cwd=SITE, check=False)
        if result.returncode == 0:
            add_head_tags(SITE / '_build' / 'html' / 'index.html')
            fix_sitemap(SITE / '_build' / 'html')
            absolute_preview_images(SITE / '_build' / 'html')
        sys.exit(result.returncode)


if __name__ == '__main__':
    main()
