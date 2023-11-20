## Getting started

Before running any scripts make sure you install all packages from `runners/requirements.txt` into your 
preferred Python environment (virtualenv is strongly encouraged, but not mandatory).

You can do this by running `pip install -r runners/requirements.txt`. 
Depending on your distribution this may be `pip` or `pip3`. 
Requirements were generated on Windows machine,
so in case of Linux/Mac/UNIX OS you may need to remove `pywin32` and `pywinpty`. 

This project is a set of Python scripts/programs/modules.
To use it, you first need to clone the repository (it's not provided in PIP registry).

It is generally recommended to use some sort of virtual environment to separate dependencies
used here from system-wide ones. Any standard Python solution will be good (`virtualenv`, `venv` etc.).
Scripts were only tested on Python 3.10.0, so for other versions minor adjustments may be needed. 

Next, in the `runners` directory there is a `requirements.txt` file, describing
packages that needs to be present in the environment. Install the requirements
using `pip install -r requirements.txt`.

Detailed steps required for reproduction are described in `reproduction.md` file, 
usage on own data and planned points of extension are described in `usage-runners.md`.

### Directory structure

There are three main directories in the repository:

 - `runners`, containing automated and semi-automated Python scripts for data acquisition and modelling
 - `manual_analysis`, containing Jupyter notebooks with overall data research and reporting 
 - `data`, containing relevant small pieces of data

`data` and `manual_analysis` directories are mostly relevant for reproduction of the original study,
if you wish to use this project to run new experiments, `runners` will be the directory you'll be mostly interested in.

The repository does not contain all the raw data required - those can be downloaded from reproduction packages
available on Zenodo.

Analysis scripts from `manual_analysis` directory are Jupyter notebooks are are developed to be used in Jupyter.
Major parts of those scripts is replicated between each other and, as such, they are not meant for reuse
outside the scope of original research.
