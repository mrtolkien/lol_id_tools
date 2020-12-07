import json
import os

from rapidfuzz.process import extractOne

with open(os.path.join(os.path.dirname(__file__), "../local_data", "locales.json"), encoding="utf-8") as file:
    locales_dict = json.load(file)


def get_clean_locale(locale: str):
    """Returns a "clean" locale from a user-entered input.
    """
    # We check if the locale is "clean"
    if locale in locales_dict.values():
        return locale

    # If not, we match it to our language list (hardcoded at the moment)
    matching_language, score, idx = extractOne(locale, locales_dict.keys())
    if score > 80:
        return locales_dict[matching_language]
    else:
        raise ValueError("The locale name could not be understood")
