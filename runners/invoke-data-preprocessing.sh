#!/bin/bash

python runners/defect-modelling/prejoin.py --defects_file data/apache-jit/apachejit_total.csv --class_metrics_files data/merged-defects/jm.csv data/merged-defects/jm2.csv data/merged-defects/pmd.csv --out_file workdir/prejoined_full.csv