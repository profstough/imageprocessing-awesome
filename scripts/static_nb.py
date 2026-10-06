"""
Make a notebook's code run with static figures instead of interactive ones.

Shared by make_expected_figs.py and build_site.py. The notebooks themselves
use `%matplotlib widget` figures, often laid out with sliders via
`VBox([...])` or `AppLayout(...)` after `plt.ioff()`. For a static image
(an expected-output PNG, or a figure on the website) we want the inline
backend instead, with each figure drawn in its starting state:

- `%matplotlib widget` becomes `%matplotlib inline`;
- `plt.ioff()` and the widget layout statements are commented out, so that
  the figure is shown at the end of the cell like any other;
- lines setting ipympl-only canvas properties (`fig.canvas.layout...`) are
  commented out too, since a static canvas doesn't have them.
"""

LAYOUTS = ('VBox(', 'HBox(', 'AppLayout(')


def static_source(source):
    '''Return the code cell source, rewritten for static (inline) figures.'''
    out = []
    depth = 0          # open parentheses of a layout statement being commented out
    for line in source.replace('%matplotlib widget', '%matplotlib inline').split('\n'):
        stripped = line.strip()
        if depth > 0 or stripped.startswith(LAYOUTS) or stripped == 'plt.ioff()' or '.canvas.layout' in line:
            out.append('pass  # (static) ' + line)
            depth = max(depth + line.count('(') - line.count(')'), 0)
        else:
            out.append(line)
    return '\n'.join(out)


def make_static(nb):
    '''Rewrite every code cell of a notebook (an nbformat node) in place for static figures.'''
    for c in nb.cells:
        if c.cell_type == 'code':
            c.source = static_source(c.source)
    return nb
