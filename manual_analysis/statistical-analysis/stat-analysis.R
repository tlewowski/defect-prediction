# Statistical analysis of the results of the experiments.
# Statistical calculations were conducted using the reproducer R package by Madeyski et al., available from CRAN [1]. We used the probability of superiority $\hat{p}$ (PHat) non-parametric effect size measure (function PHat.test from reproducer) to assess the size of the effect. To assess statistical significance, we used confidence intervals based on the t-distribution as recommended by Brunner and Munzel. For positive effect sizes, we identified the effect size as significantly greater than zero if the lower confidence interval limit was greater than the null hypothesis value, which is 0.5 for $\hat{p}$. For negative effect sizes, we identified the effect size as significantly less than zero if the upper confidence interval limit was less than the null hypothesis value.
# L. Madeyski, B. Kitchenham, and T. Lewowski, reproducer: Reproduce Statistical Analyses and Meta-Analyses, 2023. R package version 0.5.3. https://CRAN.R-project.org/package=reproducer
library(reproducer) 
library(tidyverse)
library(dplyr)

#setwd("/Users/lma/Documents/...")

# Example statistical analysis for AllMetrics vs PyDriller process metrics for the MCC metric
data <- readxl::read_excel("./Out_23_AllMetricsVsPyDrillerProcessMetrics.xlsx")#, sheet = "Out_23_AllMetricsVsPyDrillerPro")

pHatTest_mcc <- reproducer::PHat.test(
  x=dplyr::filter(data, metric_set == "pydriller")$real_mcc, 
  y=dplyr::filter(data, metric_set == "all-non-null-numeric")$real_mcc, 
  alternative="greater")
pHatTest_mcc
# Outout:
# # A tibble: 1 × 8
#      phat sqse.phat phat.df phat.tvalue phat.pvalue phat.ci.lower phat.ci.upper phat.sig
#     <dbl>     <dbl>   <dbl>       <dbl>       <dbl>         <dbl>         <dbl> <lgl>   
#   1 0.650  0.000537    512.        6.46    1.22e-10         0.612             1 TRUE   

# Example statistical analysis for AllMetrics vs PyDriller process metrics for the precision
pHatTest_precision <- reproducer::PHat.test(
  x=dplyr::filter(data, metric_set == "all-non-null-numeric")$real_precision,  
  y=dplyr::filter(data, metric_set == "pydriller")$real_precision,
  alternative="greater")
pHatTest_precision
# Outout:
# # A tibble: 1 × 8
#      phat sqse.phat phat.df phat.tvalue phat.pvalue phat.ci.lower phat.ci.upper phat.sig
#     <dbl>     <dbl>   <dbl>       <dbl>       <dbl>         <dbl>         <dbl> <lgl>   
#   1 0.679  0.000525    416.        7.80    2.58e-14         0.641             1 TRUE  


