import json
import os
from collections import namedtuple
from typing import Dict
from lol_id_tools.levensthein_utils import best_match

IdInfo = namedtuple('IdInfo', ['name', 'object_type'])
NameInfo = namedtuple('NameInfo', ['id', 'object_type', 'locale'])


def load_nickname_data() -> Dict[str, Dict[str, str]]:
    """Returns the parsed nicknames.json.
    """
    with open(os.path.join(os.path.dirname(__file__), 'local_data', 'nicknames.json'), encoding='utf-8') as file:
        return json.load(file)


with open(os.path.join(os.path.dirname(__file__), 'local_data', 'locales.json'), encoding='utf-8') as file:
    locales_dict = json.load(file)


def get_clean_locale(locale: str):
    """Returns a "clean" locale from a user-entered input.
    """
    # We check if the locale is "clean". If not, we match it to our language list.
    if locale in locales_dict.values():
        return locale

    matching_language, score = best_match(locale, locales_dict.keys())
    if score > 80:
        return locales_dict[matching_language]
    else:
        raise ValueError('The locale name could not be understood')
