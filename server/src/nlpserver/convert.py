# convention="noConvention"

# words=['ca12mel','CASE']

def set_convention(words,convention)->str:
    variable=""
    if convention=="camelCase":
        wordsForVariable=[word.title() for word in words[1:]]#.insert(0,words[0])
        wordsForVariable.insert(0,words[0].lower())

        for word in wordsForVariable:
            variable+=word
    
    elif convention=="snakeCase":
        wordsForVariable=[word.title() for word in words]#.insert(0,words[0])
        
        for word in wordsForVariable:
            variable+=word
            
    elif convention=="kebabCase":
        wordsForVariable=[word.lower() for word in words]#.insert(0,words[0])
        
        for word in wordsForVariable:
            variable+=word+"-"
        variable=variable[:-1]

    elif convention=="pascalCase" or convention=="noConvention":
        wordsForVariable=[word.lower() for word in words]#.insert(0,words[0])
            
        for word in wordsForVariable:
            variable+=word+"_"
        variable=variable[:-1]
           
    return variable



    

       
