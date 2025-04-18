#!/bin/bash

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

total=2 * 10 * ${#archs[@]}
c=0

start=`date +%s`

report_status() {
  echo Executed $c our of total. Took: $((`date +%s`-start)) seconds
}

report_status
for i in {1..10} ; do
  for arch in "${archs[@]}"
  do
    echo Running iteration $i for $arch using ../autoencoders/autoencoder_${arch}_${i}.keras as model
    poetry run python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 5 --workspace ../workdir-autoencoders-20250203-$i-$arch-denoising --training_fraction 0.8 --no-save_artifacts  --no-save_models --metric_sets all-non-null-numeric --pipelines scaled-linear-ridge unscaled-randomforest unscaled-decisiontree --pretransformer_mode denoising --pretransformer_path ../autoencoders/autoencoder_${arch}_${i}.keras
    c=c+1
    report_status
    poetry run python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 5 --workspace ../workdir-autoencoders-20250203-$i-$arch-featureselection --training_fraction 0.8 --no-save_artifacts --no-save_models --metric_sets all-non-null-numeric --pipelines scaled-linear-ridge unscaled-randomforest unscaled-decisiontree --pretransformer_mode featureselection --pretransformer_path ../autoencoders/autoencoder_${arch}_${i}.keras
    c=c+1
    report_status
  done
done
