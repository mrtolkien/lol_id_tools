import json
import os
import rapidfuzz

with open(os.path.join(os.path.dirname(__file__), 'locales.json'), encoding='utf-8') as file:
    locales_dict = json.load(file)

with open(os.path.join(os.path.dirname(__file__), 'nicknames.json'), encoding='utf-8') as file:
    raw_nicknames = json.load(file)
    nicknames = {}
    for locale_ in raw_nicknames:
        nicknames.update(raw_nicknames[locale_])


def clean_locale(locale: str):
    """Returns a "clean" locale from a user-entered input.
    """
    # If not, we check if the locale is "clean". If not, we match it to our language list.
    if locale in locales_dict.values():
        return locale

    matching_language, score = rapidfuzz.process.extractOne(locale, locales_dict.keys())
    if score > 80:
        return locales_dict[matching_language]
    else:
        raise ValueError('The locale name could not be understood')
