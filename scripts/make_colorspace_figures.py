"""
Draw the color-space figures for the Color chapter, in place of figures that
were hotlinked from other sites (they can't be bundled into the website, and
aren't ours to copy):

- dip_figs/rgb_cube.png: the RGB cube, as colored blocks with labeled axes
  (color_YCbCr and color_Lab; replaces one hotlinked from Pinterest).
- dip_figs/ycbcr_cube.png: the RGB cube in YCbCr coordinates (color_YCbCr;
  replaces one hotlinked from a paper on Semantic Scholar's CDN).
- dip_figs/lab_gamut.png: the RGB cube in L*a*b* coordinates (color_Lab;
  replaces one hotlinked from colorapplications.com).

Usage:
    uv run python scripts/make_colorspace_figures.py
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from skimage.color import rgb2lab, rgb2ycbcr

FIGS = Path(__file__).resolve().parent.parent / 'dip_figs'
N = 40   # samples along each edge of a cube face


def cube_surface():
    """Points on the six faces of the RGB cube, in [0, 1]^3 (each point is its own color)."""
    t = np.linspace(0, 1, N)
    a, b = (g.ravel() for g in np.meshgrid(t, t))
    faces = []
    for axis in range(3):
        for value in (0.0, 1.0):
            face = np.empty((a.size, 3))
            face[:, axis] = value
            face[:, [k for k in range(3) if k != axis]] = np.stack([a, b], axis=1)
            faces.append(face)
    return np.concatenate(faces)


def save(fig, name, pad=0.1):
    fig.tight_layout()
    fig.savefig(FIGS / name, dpi=120, bbox_inches='tight', pad_inches=pad)
    plt.close(fig)
    print('wrote', (FIGS / name).relative_to(FIGS.parent))


def rgb_cube(n=6):
    """The cube as n x n x n colored blocks, seen from the white corner, black at the back."""
    filled = np.ones((n, n, n), dtype=bool)
    r, g, b = (np.indices((n, n, n)) + 0.5) / n
    colors = np.stack([r, g, b], axis=-1)
    fig = plt.figure(figsize=(5.4, 4.6))
    ax = fig.add_subplot(projection='3d')
    ax.voxels(filled, facecolors=colors, edgecolors=np.clip(colors * 0.85, 0, 1), linewidth=0.3,
              shade=False)   # unshaded, so each block shows its true color
    for axis, (name, color) in enumerate([('red', 'red'), ('green', 'green'), ('blue', 'blue')]):
        end = np.zeros(3)
        end[axis] = n * 1.3
        ax.quiver(0, 0, 0, *end, color='black', arrow_length_ratio=0.08, linewidth=1.5)
        ax.text(*(end * 1.1), name, color=color, fontsize=12, fontweight='bold', ha='center', va='center')
    for lim in (ax.set_xlim, ax.set_ylim, ax.set_zlim):   # room for the arrows and labels
        lim(0, n * 1.45)
    ax.view_init(elev=28, azim=45)
    ax.set_axis_off()
    ax.set_box_aspect((1, 1, 1))
    save(fig, 'rgb_cube.png')


def ycbcr_cube():
    rgb = cube_surface()
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
    save(fig, 'ycbcr_cube.png', pad=0.3)   # the tight crop doesn't count the 3D Y label


def lab_gamut():
    rgb = cube_surface()
    lab = rgb2lab(rgb.reshape(-1, 1, 3)).reshape(-1, 3)   # L* in [0, 100]; a*, b* roughly [-110, 130]
    fig = plt.figure(figsize=(4.5, 4))
    ax = fig.add_subplot(projection='3d')
    ax.scatter(lab[:, 1], lab[:, 2], lab[:, 0], c=rgb, s=6, depthshade=False)
    ax.set_xlabel('a* (green to red)')
    ax.set_ylabel('b* (blue to yellow)')
    ax.set_zlabel('L* (lightness)')
    ax.set_zlim(0, 100)
    ax.view_init(elev=18, azim=-60)
    ax.set_title('The RGB cube in L*a*b* coordinates', fontsize=10)
    save(fig, 'lab_gamut.png', pad=0.3)   # the tight crop doesn't count the 3D L* label


if __name__ == '__main__':
    rgb_cube()
    ycbcr_cube()
    lab_gamut()
