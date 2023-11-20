## What are those "runners"?

"Runners" are various scripts used to perform each step of the research.
Most of them are implemented using CLI applications using Python `argparse` module. 

## Getting started
This project is a set of Python scripts/programs/modules.
To use it, you first need to clone the repository (it's not provided in PIP registry).

It is generally recommended to use some sort of virtual environment to separate dependencies
used here from system-wide ones. Any standard Python solution will be good (`virtualenv`, `venv` etc.).
Scripts were only tested on Python 3.10.0, so for other versions minor adjustments may be needed. 

Next, in the `runners` directory there is a `requirements.txt` file, describing
packages that needs to be present in the environment. Install the requirements
using `pip install -r requirements.txt`.


Each runner can be triggered like a standard Python module (not necessarily a script). 
This means that `python -m defect_modelling.defects_pipeline` will work, but `python defect_modelling/defects_pipeline.py` will not.

## Available runners

The following runners are available:

 - `metric_gathering.multirun` - running data collection on multiple repository revisions
 - `metric_gathering.singlerun` - running data collection from a single revision
 - `defect_modelling.experiment` - running complete experiment on defect prediction (multiple runs for multiple pipelines)
 - `defect_modelling.defects_pipeline` - running a single defect prediction pipeline (training + testing)
 - `defect_modelling.prejoin` - joining metrics for defect prediction
 - `smell_modelling.evaluate` - evaluating existing code smell models
 - `smell_modelling.smells` - building code smell models
 - `smell_modelling.build_experiment` - running complete experiment (build + evaluate) on code smell models
 - `smell_modelling.prejoin` - joining metrics for code smell modelling

Each runner has a help command accessible via CLI `--help` option that describes meanings of all available options.
