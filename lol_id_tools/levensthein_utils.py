from typing import Tuple
from Levenshtein import ratio
from collections import Counter


def best_match(string_to_match, matching_options) -> Tuple[str, int]:
    """Uses Levensthein’s distance to compute a similarity ratio
    """
    # TODO Implement that in C/Rust and calculate them all at once
    ratios = Counter()

    for second_string in matching_options:
        ratios[second_string] = ratio(string_to_match, second_string)

    return ratios.most_common(1)[0]
