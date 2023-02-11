#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell blob --metric_set pmd --workspace workdir-smell-experiment --model_target ../data/smells/pmd-blob.skops --cv 0
python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell blob --metric_set javametrics-numeric --workspace workdir-smell-experiment --model_target ../data/smells/jm-blob.skops --cv 0
python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell blob --metric_set all-non-null-numeric --workspace workdir-smell-experiment --model_target ../data/smells/all-blob.skops --cv 0
python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell "data class" --metric_set pmd --workspace workdir-smell-experiment --model_target ../data/smells/pmd-dc.skops --cv 0
python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell "data class" --metric_set javametrics-numeric --workspace workdir-smell-experiment --model_target ../data/smells/jm-dc.skops --cv 0
python smell_modelling/smells.py --data_file ../data/merged-defects/merged-smells.csv --smell "data class" --metric_set all-non-null-numeric --workspace workdir-smell-experiment --model_target ../data/smells/all-dc.skops --cv 0
