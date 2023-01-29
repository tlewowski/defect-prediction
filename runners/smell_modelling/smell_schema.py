
ALL_COLUMNS = [
    "revision",
    "entity",
    "project_x",
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
    "project_y",
    "PMD_ATFD",
    "PMD_CLASS_FAN_OUT",
    "PMD_LOC",
    "PMD_NCSS",
    "PMD_NOAM",
    "PMD_NOPA",
    "PMD_TCC",
    "PMD_WMC",
    "PMD_WOC",
    "id",
    "reviewer_id",
    "sample_id",
    "smell",
    "severity",
    "review_timestamp",
    "type",
    "repository",
    "path",
    "start_line",
    "end_line",
    "link",
    "is_from_industry_relevant_project"]

METRIC_SETS = {
    'all': ["JAVAMETRICS_access_modifier", "JAVAMETRICS_is_static", "JAVAMETRICS_is_final", "JAVAMETRICS_CYCLO", "JAVAMETRICS_LD", "JAVAMETRICS_LOC_M", "JAVAMETRICS_LOC_C", "JAVAMETRICS_MRD", "JAVAMETRICS_NOAM", "JAVAMETRICS_NOL_C", "JAVAMETRICS_NOL_M", "JAVAMETRICS_NOMR_C", "JAVAMETRICS_NOMR_M", "JAVAMETRICS_NOM", "JAVAMETRICS_NOMM", "JAVAMETRICS_NOPA", "JAVAMETRICS_NOPV", "JAVAMETRICS_WMC", "JAVAMETRICS_WMCNAMM", "JAVAMETRICS_WOC", "JAVAMETRICS_NPM", "JAVAMETRICS_NOVAR", "JAVAMETRICS_NOSE_C", "JAVAMETRICS_NOSE_M", "JAVAMETRICS_NOTB_M", "JAVAMETRICS_NOTB_C", "JAVAMETRICS_LDVC_M", "JAVAMETRICS_LDVC_C", "JAVAMETRICS_NDCWC", "JAVAMETRICS_LMNC", "PMD_ATFD", "PMD_CLASS_FAN_OUT", "PMD_LOC", "PMD_NCSS", "PMD_NOAM", "PMD_NOPA", "PMD_TCC", "PMD_WMC", "PMD_WOC"],
    'all-non-null-numeric': ["JAVAMETRICS_LD", "JAVAMETRICS_LOC_C", "JAVAMETRICS_MRD", "JAVAMETRICS_NOAM", "JAVAMETRICS_NOL_C", "JAVAMETRICS_NOMR_C", "JAVAMETRICS_NOM", "JAVAMETRICS_NOMM", "JAVAMETRICS_NOPA", "JAVAMETRICS_NOPV", "JAVAMETRICS_WMC", "JAVAMETRICS_WMCNAMM", "JAVAMETRICS_WOC", "JAVAMETRICS_NPM", "JAVAMETRICS_NOSE_C", "JAVAMETRICS_NOTB_C", "JAVAMETRICS_LDVC_C", "JAVAMETRICS_NDCWC", "JAVAMETRICS_LMNC", "PMD_ATFD", "PMD_CLASS_FAN_OUT", "PMD_LOC", "PMD_NCSS", "PMD_NOAM", "PMD_NOPA", "PMD_TCC", "PMD_WMC", "PMD_WOC"]
}

# JM NULLS:
# LOC_M, CYCLO, NOL_M, NOMR_M, NOVAR, NOSE_M, NOTB_M, LDVC_M,

METRIC_SETS['javametrics'] = list(filter(lambda x: x.startswith("JAVAMETRICS_"), METRIC_SETS['all']))
METRIC_SETS['javametrics-numeric'] = list(filter(lambda x: x.startswith("JAVAMETRICS_"), METRIC_SETS['all-non-null-numeric']))
METRIC_SETS['pmd'] = list(filter(lambda x: x.startswith("PMD_"), METRIC_SETS['all-non-null-numeric']))