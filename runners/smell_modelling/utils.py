
def cleanse(data, all_cols):
    relevant_data = data.loc[:, all_cols]

    print("SMELL_UTILS: Cleansing for a total of {} entries.".format(len(relevant_data.index)))

    if "PMD_TCC" in relevant_data:
        # filling in for utility classes, that have no members
        relevant_data["PMD_TCC"].fillna(2, inplace=True)
    if "PMD_WOC" in relevant_data:
        # filling in for utility classes that have no non-static methods
        relevant_data["PMD_WOC"].fillna(2, inplace=True)

    #    relevant_data.fillna(5000, inplace=True)

    dropped = relevant_data.dropna()
    print("SMELL_UTILS: After dropping NAs, {} reviews/samples left".format(len(dropped.index)))
    return dropped