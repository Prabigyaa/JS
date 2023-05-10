"""
For combining separate variables with convention
"""


from variable_conventions import VariableConventions

def set_convention(words: list[str], convention: VariableConventions)->str:
    variable=""
    if convention==VariableConventions.Camelcase:
        wordsForVariable=[word.title() for word in words[1:]]#.insert(0,words[0])
        wordsForVariable.insert(0,words[0].lower())

        for word in wordsForVariable:
            variable+=word

    elif convention==VariableConventions.Pascalcase:
        wordsForVariable=[word.title() for word in words]#.insert(0,words[0])

        for word in wordsForVariable:
            variable+=word

    elif convention==VariableConventions.KebabCase:
        wordsForVariable=[word.lower() for word in words]#.insert(0,words[0])

        for word in wordsForVariable:
            variable+=word+"-"
        variable=variable[:-1]

    elif convention==VariableConventions.Snakecase or convention==VariableConventions.Undefined:
        wordsForVariable=[word.lower() for word in words]#.insert(0,words[0])

        for word in wordsForVariable:
            variable+=word+"_"
        variable=variable[:-1]

    return variable