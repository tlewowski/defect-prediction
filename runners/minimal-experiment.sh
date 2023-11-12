# python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 1 --workspace ../features-20231022 --random_seed 540957747 --training_fraction 0.8 --no-save_models --save_artifacts --metric_sets pydriller --pipelines unscaled-featureselected-2-kbest-randomforest unscaled-featureselected-2-svc-randomforest
python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 40 --workspace ../minimal-features-20231028 --random_seed 611846724 --training_fraction 0.8 --no-save_models --save_artifacts --metric_sets 3-1 3-2 5-1 5-2 5-3 6-1 6-2 7-1 7-2 7-3 7-4 7-5 7-6 8-1 9-1 9-2 --pipelines unscaled-randomforest



python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 50 --workspace ../minimal-features-20231029 --random_seed 707529263 --training_fraction 0.8 --no-save_models --save_artifacts --metric_sets 1-1 1-2 1-3 1-4 1-5 1-6 1-7 2-1 3-1 3-2 5-1 5-2 5-3 6-1 6-2 7-1 7-2 7-3 7-4 7-5 8-1 8-2 9-1 9-2 --pipelines unscaled-randomforest

python -m defect_modelling.experiment --data_file ../data/prejoined_full.csv --model_count 50 --workspace ../minimal-features-20231112 --random_seed 1532198046 --training_fraction 0.8 --no-save_models --save_artifacts --metric_sets 1A 1B 1C 1D 1E 1F 1G 1H 1I 1J 1K 1L 1M 1M 1P 2A 3A 3B 5A 5B 5C 6A 6B 7A 7B 7C 7D 7E 8A 8B 9A 9B --pipelines unscaled-randomforest
