
def tokenizeString(aString, separators):
    #separators is an array of strings that are being used to split the the string.
    #sort separators in order of descending length
    separators.sort(key=len)
    listToReturn = []
    i = 0
    while i < len(aString):
  
        theSeparator = ""
        for current in separators:
            if current == aString[i:i+len(current)]:
                theSeparator = current
        if (theSeparator != "") :
            listToReturn += [theSeparator]   
            i = i + len(theSeparator)
        else:
            if (listToReturn == [])  :
                listToReturn = [""]
            if (listToReturn[-1] in separators)   :
                listToReturn += [""]
            listToReturn[-1] += aString[i]
            i += 1
    return listToReturn
