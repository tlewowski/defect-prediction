#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/merged-smells.csv --model_count 10 --workspace ../defects-workdir --random_seed 1139400319 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops
