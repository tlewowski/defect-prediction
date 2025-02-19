#!/bin/bash

# Working directory is <repository_root>/runners
# It is assumed that you have all the requirements installed already

# Just run this line below - make sure that paths match
# Be aware that this may take a while!

declare -a archs=(
  "single-layer-10-relu"
  "single-layer-5-relu"
  "single-layer-3-relu"
  "single-layer-1-relu"
  "dual-layer-30-10-relu"
  "dual-layer-20-10-relu"
  "dual-layer-30-5-relu"
  "dual-layer-20-5-relu"
  "dual-layer-30-3-relu"
  "dual-layer-20-3-relu"
  "triple-layer-40-20-10-relu"
  "triple-layer-30-20-10-relu"
  "triple-layer-30-20-5-relu"
  "triple-layer-40-20-5-relu"
  "triple-layer-40-15-5-relu"
  "triple-layer-30-15-3-relu"
  "quadruple-layer-40-20-10-5-relu"
  "quadruple-layer-40-15-8-3-relu"
  "quadruple-layer-40-15-8-1-relu"
)

for i in {1..10} ; do
  for arch in "${archs[@]}"
  do
    echo Running iteration $i for $arch
    poetry run python -m preprocessor.autoencoder --metric_set=all-non-null-numeric --data_file=../workdir/prejoined_full.csv --model_target ../autoencoders --save_models --architecture=$arch --iteration_id $i
  done
done
