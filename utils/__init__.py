

def countDuplicatesInList(dupedList):
    """
    count tags
    """
    uniqueSet = set(item for item in dupedList)
    return [(item, dupedList.count(item)) for item in uniqueSet]
