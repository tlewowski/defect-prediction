#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

python -m defect_modelling.basic_experiment --data_file ../data/merged-defects/prejoined_full.csv --model_count 100 --workspace ../defects2-workdir --random_seed 686511827 --smell_models ../data/smells/pmd-blob.skops ../data/smells/jm-blob.skops ../data/smells/all-blob.skops ../data/smells/pmd-dc.skops ../data/smells/jm-dc.skops ../data/smells/all-dc.skops