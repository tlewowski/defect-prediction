## Getting started

This project is a set of Python scripts/programs/modules.
To use it, you first need to clone the repository (it's not provided in PIP registry).

It is generally recommended to use some sort of virtual environment to separate dependencies
used here from system-wide ones. Any standard Python solution will be good (`virtualenv`, `venv` etc.).
Scripts were only tested on Python 3.10.0, so for other versions minor adjustments may be needed. 

Next, in the `runners` directory there is a `requirements.txt` file, describing
packages that needs to be present in the environment. Install the requirements
using `pip install -r requirements.txt`.

Detailed steps required for reproduction are described in `reproduction.md` file, 
usage on own data and planned points of extension are described in `usage.md`.

### Directory structure

There are three main directories in the repository:

 - `runners`, containing automated and semi-automated Python scripts for data acquisition and modelling
 - `manual_analysis`, containing Jupyter notebooks with overall data research and reporting 
 - `data`, containing relevant small pieces of data

`data` and `manual_analysis` directories are mostly relevant for reproduction of the original study,
if you wish to use this project to run new experiments, `runners` will be the directory you'll be mostly interested in.
