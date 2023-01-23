#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

python defect-modelling/prejoin.py --defects_file ../data/apache-jit/apachejit_total.csv --out_file ../data/defects/merged-defects.csv --class_metrics_files ../data/merged-defects/jm.csv ../data/merged-defects/jm2.csv ../data/merged-defects/pmd.csv

python smell-modelling/prejoin.py --mlcq_file ../data/smells/mlcq-official.csv --out_file ../data/merged-defects/merged-smells.csv --class_metrics_files ../data/smells/complete_javametrics.csv ../data/smells/complete_pmd.csv
