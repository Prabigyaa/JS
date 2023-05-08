"""
Determining variable convention using Regular Expressions.
"""

import re
from enum import Enum


# class VariableConventions(Enum):
#     """
#     Enums representing variable naming conventions.

#     There might be combination of these
#     """

#     Undefined = 0
#     Snakecase = 1
#     Pascalcase = 2
#     Camelcase = 3

#     Hugariannotation = 4
#     Abbrevationbased = 5

#     Screamingsnakecase = 6


def get_convention(variables) -> str:
    """
  returns the name of naming convention with highest repetition
    """

    # containing_capital_letters = r"[A-Z]+"
    # containing_capital_letters_only = r"^[A-Z]+$"
    # starting_with_capital_letters = r"^[A-Z]"
    # containing_small_letters = r"[a-z]+"
    # starting_with_small_letters = r"^[a-z]"
    # containing_under_scores = r"_+"
    # starting_with_under_scores = r"^_"

    # contains_capital_letters = (
    #     re.search(containing_capital_letters, variable) is not None
    # )

    # contains_capital_letters_only = (
    #     re.search(containing_capital_letters_only, variable) is not None
    # )

    # starts_with_capital_letters = (
    #     re.search(starting_with_capital_letters, variable) is not None
    # )

    # contains_small_letters = re.search(containing_small_letters, variable) is not None
    # starts_with_small_letters = re.search(starting_with_small_letters, variable)

    # starts_with_under_scores = (
    #     re.search(starting_with_under_scores, variable) is not None
    # )

    # # for different conventions like local variables, private variables or others
    # while starts_with_under_scores:
    #     starts_with_under_scores = (
    #         re.search(starting_with_under_scores, variable[1:]) is not None
    #     )
    # # At this point, the remaining underscores (if any) shouldn't in the front
    # contains_under_scores = re.search(containing_under_scores, variable) is not None

    # matched_conventions: list[VariableConventions] = []

    # if contains_under_scores:

    #     if not contains_small_letters:
    #         matched_conventions.append(VariableConventions.Screamingsnakecase)
    #     else:
    #         matched_conventions.append(VariableConventions.Snakecase)

    # if starts_with_capital_letters:

    #     # if capital letters are present in other places and it's not screaming snake case
    #     if re.search(containing_capital_letters, variable[1:]) is not None and contains_small_letters:
    #         matched_conventions.append(VariableConventions.Pascalcase)

    # if starts_with_small_letters:

    #     if contains_capital_letters:
    #         matched_conventions.append(VariableConventions.Camelcase)

    # if len(matched_conventions) == 0:
    #     # some other cases

    #     # if there are only capital letters (in case of constants)
    #     if contains_capital_letters_only:
    #         matched_conventions.append(VariableConventions.Screamingsnakecase)
    #     else:  # if the list is empty then the convention isn't known
    #         matched_conventions.append(VariableConventions.Undefined)

    # return matched_conventions
    
    camelCase=re.compile(r"[a-z]{1}\w+[A-Z]{1}[a-z]+")
    pascalCase=re.compile(r"[A-Z]{1}\w+[A-Z]{1}")
    snakeCase=re.compile(r"\w+[_]{1}")
    kebabCase=re.compile(r"\w+[\-]{1}")

    camelCaseCount=0
    pascalCaseCount=0
    snakeCaseCount=0
    kebabCaseCount=0
    noConvention=0
    # Pascalcase_count=0



    for variable in variables:
        if re.match(camelCase,variable):
            camelCaseCount+=1
        elif re.match(pascalCase,variable):
            pascalCaseCount+=1
        elif re.match(snakeCase,variable):
            snakeCaseCount+=1
        elif re.match(kebabCase,variable):
            kebabCaseCount+=1
        else:
            noConvention+=1
            
    conventionCount={"camelCase":camelCaseCount,"snakeCase":snakeCaseCount,"kebabCase":kebabCaseCount,"pascalCase":pascalCaseCount,"noConvention":noConvention}
    majorityConvention=max(conventionCount,key=conventionCount.get)
    return majorityConvention
    
   

