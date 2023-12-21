# Statistical analysis of the results of the experiments.
# Statistical calculations were conducted using the reproducer R package by Madeyski et al., available from CRAN [1]. We used the probability of superiority $\hat{p}$ (PHat) non-parametric effect size measure (function PHat.test from reproducer) to assess the size of the effect. To assess statistical significance, we used confidence intervals based on the t-distribution as recommended by Brunner and Munzel. For positive effect sizes, we identified the effect size as significantly greater than zero if the lower confidence interval limit was greater than the null hypothesis value, which is 0.5 for $\hat{p}$. For negative effect sizes, we identified the effect size as significantly less than zero if the upper confidence interval limit was less than the null hypothesis value.
# L. Madeyski, B. Kitchenham, and T. Lewowski, reproducer: Reproduce Statistical Analyses and Meta-Analyses, 2023. R package version 0.5.3. https://CRAN.R-project.org/package=reproducer
library(reproducer) 
library(tidyverse)
library(dplyr)

#setwd("/Users/lma/Documents/...")

# Example statistical analysis for AllMetrics vs PyDriller process metrics for the MCC metric
basic_data <- readxl::read_excel("./basic-metrics-full.xlsx")#, sheet = "Out_23_AllMetricsVsPyDrillerPro")
single_data <- readxl::read_excel("./single-metric-results-full.xlsx")#, sheet = "Out_23_AllMetricsVsPyDrillerPro")
minimal_data <- readxl::read_excel("./minimal-results-full.xlsx")#, sheet = "Out_23_AllMetricsVsPyDrillerPro")

print("Pydriller vs ALL")
pHatTest_mcc <- reproducer::PHat.test(
  x=dplyr::filter(basic_data, metric_set == "pydriller")$real_mcc, 
  y=dplyr::filter(basic_data, metric_set == "all-non-null-numeric")$real_mcc, 
  alternative="greater")
pHatTest_mcc
# Outout:
# # A tibble: 1 × 8
#      phat sqse.phat phat.df phat.tvalue phat.pvalue phat.ci.lower phat.ci.upper phat.sig
#     <dbl>     <dbl>   <dbl>       <dbl>       <dbl>         <dbl>         <dbl> <lgl>   
#   1 0.650  0.000537    512.        6.46    1.22e-10         0.612             1 TRUE   

# Example statistical analysis for AllMetrics vs PyDriller process metrics for the precision
pHatTest_precision <- reproducer::PHat.test(
  y=dplyr::filter(basic_data, metric_set == "all-non-null-numeric")$real_precision,  
  x=dplyr::filter(basic_data, metric_set == "pydriller")$real_precision,
  alternative="greater")
pHatTest_precision
# Outout:
# # A tibble: 1 × 8
#      phat sqse.phat phat.df phat.tvalue phat.pvalue phat.ci.lower phat.ci.upper phat.sig
#     <dbl>     <dbl>   <dbl>       <dbl>       <dbl>         <dbl>         <dbl> <lgl>   
#   1 0.679  0.000525    416.        7.80    2.58e-14         0.641             1 TRUE  


print("PyDriller vs Process")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, metric_set == "process")$real_mcc, 
  y=dplyr::filter(basic_data, metric_set == "pydriller")$real_mcc, 
  alternative="greater")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, metric_set == "process")$real_precision, 
  y=dplyr::filter(basic_data, metric_set == "pydriller")$real_precision, 
  alternative="greater")



print("Product vs code smells")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, metric_set == "none")$real_mcc, 
  y=(dplyr::filter(basic_data, metric_set == "product") %>% dplyr::filter(smell_models == "False"))$real_mcc, 
  alternative="greater")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, metric_set == "none")$real_precision, 
  y=(dplyr::filter(basic_data, metric_set == "product") %>% dplyr::filter(smell_models == "False"))$real_precision, 
  alternative="greater")



print("With or without code smells")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, smell_models == "True")$real_mcc, 
  y=dplyr::filter(basic_data, smell_models == "False")$real_mcc, 
  alternative="greater")
reproducer::PHat.test(
  x=dplyr::filter(basic_data, smell_models == "True")$real_precision, 
  y=dplyr::filter(basic_data, smell_models == "False")$real_precision, 
  alternative="greater")

print("Single metric - code smells use or no")

reproducer::PHat.test(
  x=dplyr::filter(single_data, smell_models == "True")$real_mcc, 
  y=dplyr::filter(single_data, smell_models == "False")$real_mcc, 
  alternative="greater")
reproducer::PHat.test(
  x=dplyr::filter(single_data, smell_models == "True")$real_precision, 
  y=dplyr::filter(single_data, smell_models == "False")$real_precision, 
  alternative="greater")


print("Minimal sets - 7E vs 9B")

reproducer::PHat.test(
  x=dplyr::filter(minimal_data, metric_set == "7E")$real_mcc, 
  y=dplyr::filter(minimal_data, metric_set == "9B")$real_mcc, 
  alternative="greater")
reproducer::PHat.test(
  x=dplyr::filter(minimal_data, metric_set == "7E")$real_precision, 
  y=dplyr::filter(minimal_data, metric_set == "9B")$real_precision, 
  alternative="greater")








