## imageprocessing
### [Joshua Stough](http://joshuastough.com), 202- (last update Spring 2026)

**Read it online:** [profstough.github.io/imageprocessing-awesome](https://profstough.github.io/imageprocessing-awesome/). To run and change the notebooks, set up a local copy as described below.

Imaging is everywhere! In this text, we will cover broadly the acquisition, processing, and analysis of digital images, covering topics ranging from the human visual system, to image and video compression algorithms, to pattern recognition and machine learning within the context of automatic image understanding. Best of all, for the sake of access, immediacy, and usability, all content and code examples are in the form of interactive Jupyterlab notebooks, including integrated activities!

*Written with extensive assistance of Claude in drafting narrative and copyediting, based on the draft notebook collection at [joshuastough/imageprocessing](https://github.com/joshuastough/imageprocessing).*

### A note on AI
With the advent of IDE-integrated LLM copilots, any of the integrated activities or playpen notebooks are trivial to complete. That is, your completion of them reflect almost nothing about *your* understanding of the material. If you're in class using this textbook resource, you can be expected to have to explain your work in non-augmented coding interviews throughout the course, which will comprise much of your grade. **These integrated activities are to help guide your learning, not add to your instructor's menial labor.**

### Compute Environment 
This text is tested on several platforms, but principally [Visual Studio Code](https://code.visualstudio.com/download) linked to a locally-run Python virtual environment managed by [uv](https://docs.astral.sh/uv/).
- [Please create a private fork of this project](private_fork_instructions.md), rather than publicly hosting your modified notebooks (with all of their solved activities).
- Install a local virtual environment supporting this textbook
  1. [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
  1. From the root of your clone, create the environment (this reads [pyproject.toml](./pyproject.toml) and the pinned `uv.lock`):
  ```
  $ uv sync
  ```
  1. In VS Code, open any notebook and select the `.venv` Python kernel. Or, from the terminal, `uv run jupyter lab`.

PyTorch is installed from the CUDA 12.6 wheel index. Notebooks that use it will fall back to the CPU if you don't have a CUDA-capable card. (A legacy conda environment, [env_dip26.yml](./env_dip26.yml), is still included for those who prefer it: `conda env create -f env_dip26.yml`.)

### Datasets
A few chapters (PCA, Neural Nets) use datasets too large to keep in the repository. All of them live under one data root, `~/data` by default. To use a different location, set the `DIP_DATA` environment variable before launching Jupyter.

| Dataset | Used in | How to get it |
|---|---|---|
| MNIST | `NeuralNets/mnist_*`, `PCA/pca_mnist` | Downloaded automatically by torchvision the first time |
| ORL (AT&T) faces | `PCA/pca_*Faces` | [AT&T Database of Faces](https://cam-orl.co.uk/facedatabase.html); unpack to `$DIP_DATA/ORL/` (40 subject folders) |
| Cropped Yale B | `NeuralNets/yale_*` | [Extended Yale B](http://vision.ucsd.edu/~iskwak/ExtYaleDatabase/ExtYaleB.html), "Cropped Images"; unpack to `$DIP_DATA/CroppedYale/` |
| Extended Yale B (full) | `NeuralNets/yale_explore` (last section only) | Same page; unpack to `$DIP_DATA/ExtendedYaleB/` |

No dataset? You can still read those notebooks: after each of their key cells, an **Expected output** dropdown shows what the cell produces when run with the data.

If a dataset is missing, the notebook stops with a message that says where to download it and where to put it (see [dip_utils/data_paths.py](./dip_utils/data_paths.py)).

### Opening in Colab
Alternatively you could work with this textbook through the cloud. Though there's a bit of additional hassle getting this textbook working in Colab, the payoff is that you can [link to your private fork of this project](https://colab.research.google.com/github/googlecolab/colabtools/blob/main/notebooks/colab-github-demo.ipynb) to save your work, without ever having to install a local environment. Additionally, some included notebooks use [PyTorch](https://pytorch.org/) or otherwise rely on a cuda-capable graphics card for optimal execution, which you may not have on your local machine (or which can be an additional hassle to get working). 

When executing in Colab, to every notebook that begins with `%matplotlib widget` you should:

- Insert a Code cell at the top and execute `!pip install ipympl`. This will install [ipympl](https://github.com/matplotlib/ipympl) in your Colab session, for producing interactive plots. 
- Then, insert a Code cell after with 
```python
from google.colab import output
output.enable_custom_widget_manager()
```

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/profstough/imageprocessing-awesome/blob/main/TOC.ipynb)
