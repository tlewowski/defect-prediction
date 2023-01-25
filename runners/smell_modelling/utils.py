
def cleanse(data, all_cols):
    relevant_data = data.loc[:, all_cols]

    print("SMELL_UTILS: Cleansing for a total of {} entries.".format(len(relevant_data.index)))

    if "PMD_TCC" in relevant_data:
        # filling in for utility classes, that have no members
        relevant_data["PMD_TCC"].fillna(2, inplace=True)

    if "PMD_WOC" in relevant_data:
        # filling in for utility classes that have no non-static methods
        relevant_data["PMD_WOC"].fillna(2, inplace=True)

    if "PMD_NOPA" in relevant_data:
        # filling for interfaces that cannot have public attributes
        # PMD leave that empty, as the field doesn't make sense for an interface
        relevant_data["PMD_NOPA"].fillna(0, inplace=True)

    if "PMD_NOAM" in relevant_data:
        # filling for interfaces that cannot have public attributes, so no accessors either
        # PMD leave that empty, as the field doesn't make sense for an interface
        relevant_data["PMD_NOAM"].fillna(0, inplace=True)

    if "PMD_WMC" in relevant_data:
        # filling for interfaces that cannot have implementations, so total weight is 0
        # PMD leave that empty, as the field doesn't make sense for an interface
        relevant_data["PMD_WMC"].fillna(0, inplace=True)

    if "PMD_CLASS_FAN_OUT" in relevant_data:
        # filling for interfaces that cannot have implementations, so no method-level depedencies
        # PMD leave that empty, as the field doesn't make sense for an interface
        relevant_data["PMD_CLASS_FAN_OUT"].fillna(0, inplace=True)

    dropped = relevant_data.dropna()
    print("SMELL_UTILS: After dropping NAs, {} reviews/samples left".format(len(dropped.index)))
    return dropped