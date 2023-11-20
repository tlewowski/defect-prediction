## Reproduction

The research consisted of several steps leading to finally building and evaluating defect prediction models.

Those steps are described in the order of execution below. Be aware that some of them
may take a rather long time (weeks) and are meant to be parallelized, possibly in a cloud setup.

All intermediate results coming from long-running processes can be also downloaded directly from Zenodo and used
as was in the original research.

This parallelization is _not_ included in the reproduction scripts, because it heavily depends
on the number of available machines and their power. Instead, each script that may be 
parallelized contains a description of required dependencies.

### General remarks

All the scripts that were run are included in a suite of `invoke-*.sh` bash scripts.
Those scripts are meant to be run in `bash` shell on a Linux machine, but they should work
just as well in any other OS with `bash` (perhaps with adjustment of paths)

### Data collection and preprocessing

There are three main steps related to preparing the final source data file:

1. Downloading open data sets used in the research (MLCQ from https://zenodo.org/record/3666840#.ZAHWE3bMKUk and ApacheJIT from https://zenodo.org/record/5907847#.ZAHWNnbMKUk)
2. Calculating metrics for all entities included in the data sets above (can take weeks)
3. Joining the generated intermediate files into a full data set 

For readers' convenience, complete data sets ready to be used in further steps are provided here:
- smells: https://metrics-v2.s3.eu-west-3.amazonaws.com/merged-smells.zip
- defects: https://metrics-v2.s3.eu-west-3.amazonaws.com/prejoined_full.zip

They are also available on Zenodo.

For readers who want to run the full reproduction, several support scripts are provided:

1. Cloning all the repositories at once can be done with `runners/repository_cloning/clone_all.py`, but the script is rather crude and it has to be copied into parent
directory of the cloned repositories (e.g. if you copy the script into `/var/repos`, cloned repositories will be placed in `/var/repos/[org]/[name]`, e.g. `/var/repos/apache/activemq`)
2. Download the full tooling package from https://metrics-v2.s3.eu-west-3.amazonaws.com/tools.tar.gz
3. All steps required for data collection are described in detail in script `runners/invoke-data-collection.sh`. This script is not meant to be ran as-is, since
it would likely take weeks to complete. Please read the comments written in the script to understand its planned usage.
4. After merging all the metric data on a per-tool basis, it needs to be joined with the source data set. This is done by
running `invoke-data-preprocessing.sh` script. 

In case of issues, first make sure that all paths are correct. Those scripts are meant to be fixed, so they assume a given location of
data (in `../data`) and their working directory (`runners`). Data collection script is much more challenging to get right, so
please refer to the instructions inside the script.

### Modelling and evaluation

Two types of entities are evaluated: code smells and defects

Watch out: modelling requires running the scripts as modules (`python -m dir.file`) instead of "as scripts" (`python dir/file.py`)

#### Code smells
To run smell modelling experiments, follow steps defined in `runners/invoke-smells-experiment.sh`

This file contains a fixed random seed, which means that it should always generate the exactly same 
code smell models. If you wish to modify it, you can alter the scripts without any major consequences.
In particular, you may want to alter the number of models build for each smell and metric set, because with the default setting
it may take up to a few days to complete.

Make sure that paths are adjusted to your setup.

To generate complete models that will be then used in defect prediction research, follow directions
defined in `runners/invoke-smell-models-generation.sh`.

Models used during the research conducted in the thesis can be found here:
https://metrics-v2.s3.eu-west-3.amazonaws.com/smell-models.zip

#### Defects

To run defect modelling experiments, follow steps defined in `runners/invoke-basic-experiment-cloud.sh`

Be aware that this script contains several experiments - in particular, there are two separate experiments
for single metrics (`single_metrics_experiment`) and for metric sets (`metric_sets`). Existence of code smells is 
calculated automatically on script startup, and then is added to the data set used for training and testing.

The last, fourth experiment can be reproduced using `runners/invoke-minimal-experiment.sh` script.

### Reporting

Reporting is done manually, basing on Jupyter notebooks in `manual_analysis`.

In particular, notebooks `smell-performance-*` and `defect-performance-*` (in subdirectories) contain basic analysis
of performance of created models. Exports from these notebooks were later on included in the research and accompanying papers.

Make sure that paths to data files match whatever you have on your machine.
