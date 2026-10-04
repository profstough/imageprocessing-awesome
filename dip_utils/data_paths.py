"""
Dataset Locations
stough, 202-

The larger datasets used in the book (MNIST, ORL faces, Yale faces) live
outside the repository, under a single data root. By default that's ~/data,
but you can point it elsewhere by setting the DIP_DATA environment variable
before launching Jupyter, e.g.

    $ export DIP_DATA=/path/to/my/data

Expected layout:

    $DIP_DATA/
        MNIST/            (downloaded automatically by torchvision)
        ORL/              (40 subfolders, one per subject, 10 images each)
        CroppedYale/      (yaleB01 ... yaleB39 subfolders)
        ExtendedYaleB/    (optional, only used in yale_explore)
"""

import os
from pathlib import Path

DATA_ROOT = Path(os.environ.get('DIP_DATA', '~/data')).expanduser()

_SOURCES = {
    'ORL': 'https://cam-orl.co.uk/facedatabase.html '
           '(also mirrored on Kaggle as "ORL faces / AT&T database of faces")',
    'CroppedYale': 'http://vision.ucsd.edu/~iskwak/ExtYaleDatabase/ExtYaleB.html '
                   '(the "Cropped Images" archive)',
    'ExtendedYaleB': 'http://vision.ucsd.edu/~iskwak/ExtYaleDatabase/ExtYaleB.html',
}


def _require(name):
    '''
    _require(name): return DATA_ROOT/name, raising a helpful error if it isn't there.
    '''
    path = DATA_ROOT / name
    if not path.is_dir():
        raise FileNotFoundError(
            f'Could not find the {name} dataset at {path}.\n'
            f'Download it from {_SOURCES[name]}\n'
            f'and unpack it so that {path} exists. '
            f'(Set the DIP_DATA environment variable to use a different data root.)')
    return str(path)


def mnist_root():
    '''
    mnist_root(): directory to hand torchvision.datasets.MNIST as root. Use with
    download=True and torchvision will fetch the data the first time.
    '''
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    return str(DATA_ROOT)


def orl_root():
    '''orl_root(): path to the ORL (AT&T) faces, suitable for torchvision ImageFolder.'''
    return _require('ORL')


def yale_root():
    '''yale_root(): path to the Cropped Yale Face Database B, for ImageFolder.'''
    return _require('CroppedYale')


def yale_ext_root():
    '''yale_ext_root(): path to the full Extended Yale Face Database B, for ImageFolder.'''
    return _require('ExtendedYaleB')
