#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

python -m defect_modelling.defects_pipeline --input_data ../workdir/prejoined_full.csv --metric_set pydriller --class_set defects

python -m defect_modelling.defects_pipeline --input_data ../workdir/prejoined_full.csv --metric_set pydriller --class_set defects --smell_models ..\data\smells\all-blob.skops ..\data\smells\all-dc.skops ..\data\smells\pmd-blob.skops ..\data\smells\jm-blob.skops ..\data\smells\jm-dc.skops ..\data\smells\pmd-dc.skops
