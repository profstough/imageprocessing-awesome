"""
Draw the RGB color cube in YCbCr coordinates, for Color/color_YCbCr.ipynb.

Replaces a figure that was hotlinked from a paper on Semantic Scholar's CDN
(it can't be bundled into the website, and isn't ours to copy). Writes
dip_figs/ycbcr_cube.png.

Usage:
    uv run python scripts/make_ycbcr_cube_figure.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.color import rgb2ycbcr

OUT = Path(__file__).resolve().parent.parent / 'dip_figs' / 'ycbcr_cube.png'
N = 40   # samples along each edge of a cube face

# Points on the six faces of the RGB cube, with each point's own color.
t = np.linspace(0, 1, N)
a, b = (g.ravel() for g in np.meshgrid(t, t))
faces = []
for axis in range(3):
    for value in (0.0, 1.0):
        face = np.empty((a.size, 3))
        face[:, axis] = value
        face[:, [k for k in range(3) if k != axis]] = np.stack([a, b], axis=1)
        faces.append(face)
rgb = np.concatenate(faces)
ycbcr = rgb2ycbcr(rgb.reshape(-1, 1, 3)).reshape(-1, 3)   # Y in [16, 235], Cb and Cr in [16, 240]

fig = plt.figure(figsize=(4.5, 4))
ax = fig.add_subplot(projection='3d')
ax.scatter(ycbcr[:, 1], ycbcr[:, 2], ycbcr[:, 0], c=rgb, s=6, depthshade=False)
ax.set_xlabel('Cb (chroma blue)')
ax.set_ylabel('Cr (chroma red)')
ax.set_zlabel('Y (luma)')
ax.set_xlim(16, 240)
ax.set_ylim(16, 240)
ax.set_zlim(16, 235)
ax.view_init(elev=18, azim=-60)
ax.set_title('The RGB cube in YCbCr coordinates', fontsize=10)
fig.tight_layout()
fig.savefig(OUT, dpi=120, bbox_inches='tight')
print('wrote', OUT.relative_to(OUT.parent.parent))
