#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

# Just run this line below - make sure that paths match
# Be aware that this may take a while!

python smell_modelling/build_experiment.py --data_file ../data/merged-defects/merged-smells.csv --model_count 500 --workspace ../workdir --random_seed 3867502256
