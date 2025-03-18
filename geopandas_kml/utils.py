import string
import random

IDT = " " * 4

BACK_WORD = "\nThe value you passed ---> kward: {kward}: type: {type}, value: {value}"


def formatter(sentence: str, max_cols: int = 100) -> str:
    """
    ## Summary:
        Format the sentence to fit the maximum number of columns.
    Args:
        sentence(str): A sentence to format.
        max_cols(int): The maximum number of columns.
    Returns:
        str: A formatted sentence.
    """
    new_sentence = ""
    new_lines = sentence.split("\n")

    if isinstance(new_lines, str):
        new_lines = [new_lines]

    for line in new_lines:
        new_sentence += "\n"
        counter = 0
        words = line.split(" ")
        for word in words:
            if max_cols < counter + len(word):
                new_sentence += "\n"
                counter = 0
            new_sentence += word + " "
            counter += len(word) + 1
    return new_sentence.replace("\n", f"\n{IDT}")


def generate_id(length: int = 10) -> str:
    """
    ## Summary:
        Generate a random ID. This ID is used to identify the style, placemark, etc.
    Args:
        length(int):
            Length of the ID. Default is 10.
    Returns:
        str: Random ID.
    Examples:
        >>> generate_id(5)
        'X2Y4Z'
    """
    alphabet = string.ascii_uppercase
    numbers = "".join(list(map(str, list(range(10)))))
    chars = alphabet + numbers
    style_id = "".join(random.choices(chars, k=length))
    return style_id
