import functools

ALL_COLUMNS = ["project",
"revision",
"entity",
"JAVAMETRICS_access_modifier",
"JAVAMETRICS_is_static",
"JAVAMETRICS_is_final",
"JAVAMETRICS_CYCLO",
"JAVAMETRICS_LD",
"JAVAMETRICS_LOC_M",
"JAVAMETRICS_LOC_C",
"JAVAMETRICS_MRD",
"JAVAMETRICS_NOAM",
"JAVAMETRICS_NOL_C",
"JAVAMETRICS_NOL_M",
"JAVAMETRICS_NOMR_C",
"JAVAMETRICS_NOMR_M",
"JAVAMETRICS_NOM",
"JAVAMETRICS_NOMM",
"JAVAMETRICS_NOPA",
"JAVAMETRICS_NOPV",
"JAVAMETRICS_WMC",
"JAVAMETRICS_WMCNAMM",
"JAVAMETRICS_WOC",
"JAVAMETRICS_NPM",
"JAVAMETRICS_NOVAR",
"JAVAMETRICS_NOSE_C",
"JAVAMETRICS_NOSE_M",
"JAVAMETRICS_NOTB_M",
"JAVAMETRICS_NOTB_C",
"JAVAMETRICS_LDVC_M",
"JAVAMETRICS_LDVC_C",
"JAVAMETRICS_NDCWC",
"JAVAMETRICS_LMNC",
"JAVAMETRICS2_AverageNumberOfAddedLines",
"JAVAMETRICS2_MaxNumberOfAddedLines",
"JAVAMETRICS2_AgeInDays",
"JAVAMETRICS2_AverageNumberOfDaysBetweenChanges",
"JAVAMETRICS2_NumberOfBugFixes",
"JAVAMETRICS2_CodeChurn",
"JAVAMETRICS2_MeanCommitMessageLength",
"JAVAMETRICS2_NumberOfRevisions",
"JAVAMETRICS2_NumberOfCommitsWithoutMessage",
"JAVAMETRICS2_DaysWithCommits",
"JAVAMETRICS2_AverageNumberOfDeletedLines",
"JAVAMETRICS2_MaxNumberOfDeletedLines",
"JAVAMETRICS2_MeanAuthorCommits",
"JAVAMETRICS2_NumberOfDistinctCommitters",
"JAVAMETRICS2_AverageNumberOfModifiedLines",
"JAVAMETRICS2_MaxNumberOfModifiedLines",
"JAVAMETRICS2_NumberOfRefactorings",
"JAVAMETRICS2_AuthorFragmentation",
"JAVAMETRICS2_DaysPassedSinceTheLastChange",
"JAVAMETRICS2_LambdaDensity",
"JAVAMETRICS2_LinesOfCode",
"JAVAMETRICS2_MethodReferenceDensity",
"JAVAMETRICS2_NumberOfAccessorMethods",
"JAVAMETRICS2_NumberOfLambdaExpressions",
"JAVAMETRICS2_NumberOfMethodReferences",
"JAVAMETRICS2_NumberOfMethods",
"JAVAMETRICS2_NumberOfMutatorMethods",
"JAVAMETRICS2_NumberOfPublicFields",
"JAVAMETRICS2_NumberOfPrivateFields",
"JAVAMETRICS2_WeightedMethodsPerClass",
"JAVAMETRICS2_WeightedMethodsPerClassWithoutAccessorAndMutatorMethods",
"JAVAMETRICS2_WeightOfClass",
"JAVAMETRICS2_NumberOfPublicMethods",
"JAVAMETRICS2_ResponseForClass",
"JAVAMETRICS2_NumberOfFieldAnnotations",
"PMD_ATFD",
"PMD_CLASS_FAN_OUT",
"PMD_LOC",
"PMD_NCSS",
"PMD_NOAM",
"PMD_NOPA",
"PMD_TCC",
"PMD_WMC",
"PMD_WOC",
"buggy",
"fix",
"year",
"author_date",
"la",
"ld",
"nf",
"nd",
"ns",
"ent",
"ndev",
"age",
"nuc",
"aexp",
"arexp",
"asexp"]

METRIC_SETS = {
    'all': ["JAVAMETRICS_access_modifier", "JAVAMETRICS_is_static", "JAVAMETRICS_is_final", "JAVAMETRICS_CYCLO", "JAVAMETRICS_LD", "JAVAMETRICS_LOC_M", "JAVAMETRICS_LOC_C", "JAVAMETRICS_MRD", "JAVAMETRICS_NOAM", "JAVAMETRICS_NOL_C", "JAVAMETRICS_NOL_M", "JAVAMETRICS_NOMR_C", "JAVAMETRICS_NOMR_M", "JAVAMETRICS_NOM", "JAVAMETRICS_NOMM", "JAVAMETRICS_NOPA", "JAVAMETRICS_NOPV", "JAVAMETRICS_WMC", "JAVAMETRICS_WMCNAMM", "JAVAMETRICS_WOC", "JAVAMETRICS_NPM", "JAVAMETRICS_NOVAR", "JAVAMETRICS_NOSE_C", "JAVAMETRICS_NOSE_M", "JAVAMETRICS_NOTB_M", "JAVAMETRICS_NOTB_C", "JAVAMETRICS_LDVC_M", "JAVAMETRICS_LDVC_C", "JAVAMETRICS_NDCWC", "JAVAMETRICS_LMNC", "JAVAMETRICS2_AverageNumberOfAddedLines", "JAVAMETRICS2_MaxNumberOfAddedLines", "JAVAMETRICS2_AgeInDays", "JAVAMETRICS2_AverageNumberOfDaysBetweenChanges", "JAVAMETRICS2_NumberOfBugFixes", "JAVAMETRICS2_CodeChurn", "JAVAMETRICS2_MeanCommitMessageLength", "JAVAMETRICS2_NumberOfRevisions", "JAVAMETRICS2_NumberOfCommitsWithoutMessage", "JAVAMETRICS2_DaysWithCommits", "JAVAMETRICS2_AverageNumberOfDeletedLines", "JAVAMETRICS2_MaxNumberOfDeletedLines", "JAVAMETRICS2_MeanAuthorCommits", "JAVAMETRICS2_NumberOfDistinctCommitters", "JAVAMETRICS2_AverageNumberOfModifiedLines", "JAVAMETRICS2_MaxNumberOfModifiedLines", "JAVAMETRICS2_NumberOfRefactorings", "JAVAMETRICS2_AuthorFragmentation", "JAVAMETRICS2_DaysPassedSinceTheLastChange", "JAVAMETRICS2_LambdaDensity", "JAVAMETRICS2_LinesOfCode", "JAVAMETRICS2_MethodReferenceDensity", "JAVAMETRICS2_NumberOfAccessorMethods", "JAVAMETRICS2_NumberOfLambdaExpressions", "JAVAMETRICS2_NumberOfMethodReferences", "JAVAMETRICS2_NumberOfMethods", "JAVAMETRICS2_NumberOfMutatorMethods", "JAVAMETRICS2_NumberOfPublicFields", "JAVAMETRICS2_NumberOfPrivateFields", "JAVAMETRICS2_WeightedMethodsPerClass", "JAVAMETRICS2_WeightedMethodsPerClassWithoutAccessorAndMutatorMethods", "JAVAMETRICS2_WeightOfClass", "JAVAMETRICS2_NumberOfPublicMethods", "JAVAMETRICS2_ResponseForClass", "JAVAMETRICS2_NumberOfFieldAnnotations", "PMD_ATFD", "PMD_CLASS_FAN_OUT", "PMD_LOC", "PMD_NCSS", "PMD_NOAM", "PMD_NOPA", "PMD_TCC", "PMD_WMC", "PMD_WOC", "la", "ld", "nf", "nd", "ns", "ent", "ndev", "age", "nuc", "aexp", "arexp", "asexp"],
    'all-non-null-numeric': ["JAVAMETRICS_LD", "JAVAMETRICS_LOC_C", "JAVAMETRICS_MRD", "JAVAMETRICS_NOAM", "JAVAMETRICS_NOL_C", "JAVAMETRICS_NOMR_C", "JAVAMETRICS_NOM", "JAVAMETRICS_NOMM", "JAVAMETRICS_NOPA", "JAVAMETRICS_NOPV", "JAVAMETRICS_WMC", "JAVAMETRICS_WMCNAMM", "JAVAMETRICS_WOC", "JAVAMETRICS_NPM", "JAVAMETRICS_NOSE_C", "JAVAMETRICS_NOTB_C", "JAVAMETRICS_LDVC_C", "JAVAMETRICS_NDCWC", "JAVAMETRICS_LMNC", "JAVAMETRICS2_AverageNumberOfAddedLines", "JAVAMETRICS2_MaxNumberOfAddedLines", "JAVAMETRICS2_AgeInDays", "JAVAMETRICS2_AverageNumberOfDaysBetweenChanges", "JAVAMETRICS2_NumberOfBugFixes", "JAVAMETRICS2_CodeChurn", "JAVAMETRICS2_MeanCommitMessageLength", "JAVAMETRICS2_NumberOfRevisions", "JAVAMETRICS2_NumberOfCommitsWithoutMessage", "JAVAMETRICS2_DaysWithCommits", "JAVAMETRICS2_AverageNumberOfDeletedLines", "JAVAMETRICS2_MaxNumberOfDeletedLines", "JAVAMETRICS2_MeanAuthorCommits", "JAVAMETRICS2_NumberOfDistinctCommitters", "JAVAMETRICS2_AverageNumberOfModifiedLines", "JAVAMETRICS2_MaxNumberOfModifiedLines", "JAVAMETRICS2_NumberOfRefactorings", "JAVAMETRICS2_AuthorFragmentation", "JAVAMETRICS2_DaysPassedSinceTheLastChange", "JAVAMETRICS2_LambdaDensity", "JAVAMETRICS2_LinesOfCode", "JAVAMETRICS2_MethodReferenceDensity", "JAVAMETRICS2_NumberOfAccessorMethods", "JAVAMETRICS2_NumberOfLambdaExpressions", "JAVAMETRICS2_NumberOfMethodReferences", "JAVAMETRICS2_NumberOfMethods", "JAVAMETRICS2_NumberOfMutatorMethods", "JAVAMETRICS2_NumberOfPublicFields", "JAVAMETRICS2_NumberOfPrivateFields", "JAVAMETRICS2_WeightedMethodsPerClass", "JAVAMETRICS2_WeightedMethodsPerClassWithoutAccessorAndMutatorMethods", "JAVAMETRICS2_WeightOfClass", "JAVAMETRICS2_NumberOfPublicMethods", "JAVAMETRICS2_ResponseForClass", "JAVAMETRICS2_NumberOfFieldAnnotations", "PMD_ATFD", "PMD_CLASS_FAN_OUT", "PMD_LOC", "PMD_NCSS", "PMD_NOAM", "PMD_NOPA", "PMD_TCC", "PMD_WMC", "PMD_WOC", "la", "ld", "nf", "nd", "ns", "ent", "ndev", "age", "nuc", "aexp", "arexp", "asexp"],
    'javametrics2-product': ["JAVAMETRICS2_LambdaDensity", "JAVAMETRICS2_LinesOfCode", "JAVAMETRICS2_MethodReferenceDensity", "JAVAMETRICS2_NumberOfAccessorMethods", "JAVAMETRICS2_NumberOfLambdaExpressions", "JAVAMETRICS2_NumberOfMethodReferences", "JAVAMETRICS2_NumberOfMethods", "JAVAMETRICS2_NumberOfMutatorMethods", "JAVAMETRICS2_NumberOfPublicFields", "JAVAMETRICS2_NumberOfPrivateFields", "JAVAMETRICS2_WeightedMethodsPerClass", "JAVAMETRICS2_WeightedMethodsPerClassWithoutAccessorAndMutatorMethods", "JAVAMETRICS2_WeightOfClass", "JAVAMETRICS2_NumberOfPublicMethods", "JAVAMETRICS2_ResponseForClass", "JAVAMETRICS2_NumberOfFieldAnnotations"],
    'javametrics2-process': ["JAVAMETRICS2_AverageNumberOfAddedLines", "JAVAMETRICS2_MaxNumberOfAddedLines", "JAVAMETRICS2_AgeInDays", "JAVAMETRICS2_AverageNumberOfDaysBetweenChanges", "JAVAMETRICS2_NumberOfBugFixes", "JAVAMETRICS2_CodeChurn", "JAVAMETRICS2_MeanCommitMessageLength", "JAVAMETRICS2_NumberOfRevisions", "JAVAMETRICS2_NumberOfCommitsWithoutMessage", "JAVAMETRICS2_DaysWithCommits", "JAVAMETRICS2_AverageNumberOfDeletedLines", "JAVAMETRICS2_MaxNumberOfDeletedLines", "JAVAMETRICS2_MeanAuthorCommits", "JAVAMETRICS2_NumberOfDistinctCommitters", "JAVAMETRICS2_AverageNumberOfModifiedLines", "JAVAMETRICS2_MaxNumberOfModifiedLines", "JAVAMETRICS2_NumberOfRefactorings", "JAVAMETRICS2_AuthorFragmentation", "JAVAMETRICS2_DaysPassedSinceTheLastChange"]
}

# JM NULLS:
# LOC_M, CYCLO, NOL_M, NOMR_M, NOVAR, NOSE_M, NOTB_M, LDVC_M,

METRIC_SETS['javametrics'] = list(filter(lambda x: x.startswith("JAVAMETRICS_"), METRIC_SETS['all']))
METRIC_SETS['javametrics-numeric'] = list(filter(lambda x: x.startswith("JAVAMETRICS_"), METRIC_SETS['all-non-null-numeric']))
METRIC_SETS['javametrics2'] = METRIC_SETS['javametrics2-process'] + METRIC_SETS['javametrics2-product']
METRIC_SETS['pmd'] = list(filter(lambda x: x.startswith("PMD_"), METRIC_SETS['all']))
METRIC_SETS['pydriller'] = list(filter(lambda x: not x.startswith("PMD_") and not x.startswith("JAVAMETRICS"), METRIC_SETS['all']))
METRIC_SETS['product'] = METRIC_SETS['pmd'] + METRIC_SETS['javametrics-numeric'] + METRIC_SETS['javametrics2-product']
METRIC_SETS['process'] = METRIC_SETS['pydriller'] + METRIC_SETS['javametrics2-process']
METRIC_SETS['none'] = []

METRIC_SETS.update(dict([(m,[m]) for m in METRIC_SETS['all-non-null-numeric']]))

CLASS_SETS = {
    'defects': ['buggy'],
    'fixes': ['fix']
}

METRIC_SETS['minimal-good'] = ["la",
                               "JAVAMETRICS2_MeanAuthorCommits",
                               "JAVAMETRICS2_DaysPassedSinceTheLastChange",
                               "JAVAMETRICS2_NumberOfFieldAnnotations",
                               "JAVAMETRICS2_NumberOfAccessorMethods",
                               "JAVAMETRICS2_NumberOfMutatorMethods"
                               ]

METRIC_SETS['best-mcc'] = ["la", "JAVAMETRICS2_MeanAuthorCommits"]

METRIC_SETS['best-precision'] = ["la",
                               "JAVAMETRICS2_DaysPassedSinceTheLastChange",
                               "JAVAMETRICS2_NumberOfFieldAnnotations",
                               "JAVAMETRICS2_NumberOfAccessorMethods",
                               "JAVAMETRICS2_NumberOfMutatorMethods"
                               ]
