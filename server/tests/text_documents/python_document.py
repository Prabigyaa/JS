"""
The module comment.
"""

def main():
    print("\n----------------------------------------------------------")
    print("This python document is for testing the workings of server.")
    print("----------------------------------------------------------\n")


"""
External docstring only, docstring before a function definition.
"""
def func_following_external_docstring(float_to_print: float) -> None:
    print(float_to_print)


def func_with_docstring_inside(string_to_print: str) -> None:
    """
    Internal docstring only, docstring after function definition.
    """
    print(string_to_print)


# comment before function
def func_after_a_comment(integer_to_print: int) -> None:
    print(integer_to_print)


"""
External docstring along with internal one.
"""
def func_after_a_docstring_and_docstring_inside(num1: int, num2: int) -> int:
    """
    Internal docstring along with internal one.
    """
    return num1 + num2


# External comment along with internal one.
def func_after_a_comment_and_comment_inside(num1: float, num2: float) -> float:
    # Internal comment along with external one.
    return num1 * num2


# External comment with internal docstring.
def func_after_a_comment_and_docstring_inside(lst1: list, lst2: list, output: list) -> list:
    """
    Internal docstring with external comment.
    """

    output.extend(lst1)
    output.extend(lst2)

    return output


"""
External docstring with internal comment.
"""
def func_after_a_docstring_and_comment_inside(check_key: str, dict: dict[str, object]) -> bool:
    # Internal comment with external docstring.

    return dict.get(check_key) is not None


def a_function_giving_errors():

    # A lone comment.

    # Comment with identifier
    complete_identifier = False

    # Comment with incomplete identifier
    incomplete_identifier

    """
    Docstring before identifier
    """
    complete_identifier_after_docstring = ["Moon", "Earth", "Europa"]


if __name__ == "__main__":
    main()
