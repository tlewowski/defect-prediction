import pandas as pd
from defect_schema import METRIC_SETS


def cleanse(data):
    print("DEFECT_UTILS: Cleansing for a total of {} entries.".format(len(data.index)))

    # fields that are missing values in this analysis are not errors or data that could not be accessed
    # but rather items, that don't make sense for a particular class-like item (interface etc.)
    # PMD usually leaves them empty
    # for JavaMetrics N/As are inner classes, as it cannot analyze them
    # to make a fair comparison, we set those fields to a value that is not anywhere in the "real" data set
    # In programming world this would be something like -1, but apparently some ML models don't like negative inputs
    # So, since those metrics are in range [0, inf) or [0, 1], we'll shift them to [1, inf) or [1,2] and set 0 to the "non-existing"

    # Filling in for PMD - reasons:
    # TCC - utility classes, that have no members
    # WOC - utility classes that have no non-static methods
    # NOPA - interfaces that cannot have public attributes
    # NOAM - interfaces that cannot have public attributes, so no accessors either
    # WMC - interfaces that have no implementations, so total weight is 0
    # CLASS_FAN_OUT - interfaces that cannot have implementations, so no method-level depedencies

    for metric in METRIC_SETS['pmd']:
        if metric in data:
            data[metric] = data[metric].apply(lambda x: x + 1 if not pd.isna(x) else 0)

    for metric in METRIC_SETS['javametrics-numeric']:
        if metric in data:
            data[metric] = data[metric].apply(lambda x: x + 1 if not pd.isna(x) else 0)

    for metric in METRIC_SETS['javametrics2']:
        if metric in data:
            data[metric] = data[metric].apply(lambda x: x + 1 if not pd.isna(x) else 0)

    return data
#%%

