#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already


# Basic experiment evaluations
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects2-workdir --random_seed 1027480567 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects3-workdir --random_seed 674371139 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects4-workdir --random_seed 4290224760 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects5-workdir --random_seed 3427575703 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects6-workdir --random_seed 1594437672 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects7-workdir --random_seed 2492896108 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops

python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects10-workdir --random_seed 3407870547 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops






# Single-metric experiment evaluations

python -m defect_modelling.single_metric_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 100 --workspace ../defects-single-workdir2 --random_seed 3462457372 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops

# Project-level experiment evaluations

python -m defect_modelling.split_by_project_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 10 --workspace ../defects-project-workdir2 --random_seed 3614672768 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops