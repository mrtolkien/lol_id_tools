import warnings
from typing import Optional

from rapidfuzz.process import extractOne

from lol_id_tools.local_data_parser import get_clean_locale
from lol_id_tools.logger import lit_logger
from lol_id_tools.lol_object_data import LolObjectData

# Instantiating a LolObjectData object is very light as all its fields are ghost loaded.
lod = LolObjectData()


# TODO Add older patches support
def get_name(
    input_id: int, output_locale: str = "en_US", object_type=None, retry=True, fallback_to_none=True
) -> Optional[str]:
    """Gets you the name of the associated Riot object.

    If the chosen locale is not loaded in the database, it will be loaded before returning the result.

    Args:
        input_id: Riot ID of the object
        output_locale: Locale of the output
        object_type: specifics the object type you want the name of, in ['champion', 'item', 'rune', 'summoner_spell']
        retry: Optional variable specifying if local_data should be reloaded once if the object cannot be found
        fallback_to_none: whether the tool returns None in case of a KeyError

    Returns:
        The matching object name.

    Raises:
        KeyError: The corresponding object was not found.
        ValueError: The locale was not understood properly.

    Usage example:
        get_name(21)
        get_name(21, 'ko_KR')
    """
    try:
        input_id = int(input_id)
    except ValueError:
        raise ValueError(f"{input_id} could not be cast to an integer.")

    # Riot uses 0 as a "no item" value and -1 as "no ban" value.
    if input_id <= 0:
        return ""

    # We start by cleaning up our locale
    output_locale = get_clean_locale(output_locale)

    # First, we see if the object is there with the given constraints
    try:
        if not object_type:
            if lod.loaded_data[output_locale][input_id].__len__() > 1:
                warning_text = f"Multiple objects with ID {input_id} found, please inform object_type."
                lit_logger.warning(warning_text)
            for object_type in ["champion", "item", "rune", "summoner_spell"]:
                # Iterating this way to have a priority between object types
                # TODO Rework that for more readable code
                if object_type in lod.loaded_data[output_locale][input_id]:
                    break

        return lod.loaded_data[output_locale][input_id][object_type]
    except KeyError:
        pass

    if output_locale not in lod.loaded_locales:
        lod.load_locale(output_locale)
        return get_name(input_id, output_locale, retry=False)

    if retry:
        lod.reload_all_locales()
        return get_name(input_id, output_locale, retry=False)

    error_text = f"Riot object with id {input_id} could not be found."

    if not fallback_to_none:
        raise KeyError(error_text)
    else:
        lit_logger.warning(error_text)
        return None


class NoMatchingNameFound(Exception):
    pass


def get_id(
    input_str: str,
    minimum_score: int = 75,
    input_locale: str = None,
    object_type: str = None,
    retry: bool = True,
) -> int:
    """Returns the best Riot ID guess for the given name.

    Will return the id that matches the query best. Best used in curated environments.

    Args:
        input_str: Search string.
        minimum_score: Optional minimum ratio (between 0 and 100) under which the function retries or raises.
        input_locale: The language the input was in.
        object_type: Optional string in ['champion', 'item', 'rune', 'summoner_spell']
        retry: Optional variable specifying if local_data should be reloaded if the object cannot be found.

    Returns:
        The matching object ID.

    Raises:
        NoMatchingNameFound: No string scored above the minimum_score.
        ValueError: The locale was not understood properly.

    Usage example:
        get_id('Miss Fortune')
        get_id('MF')
        get_id('미스 포츈')
        get_id('Dio')
    """
    input_str = input_str.lower()

    # Handling some Leaguepedia special cases as having an ID of 0, might be stupid and should just raise
    if not input_str or input_str == "none" or input_str == "loss of ban" or input_str == "no item":
        return 0

    # We try to directly get the object with the exact input name
    try:
        return lod.names_to_id[input_str].id
    except KeyError:
        pass

    # If we run get_id() with no locale and nothing is loaded, we load english by default.
    if not input_locale and not lod.loaded_locales:
        lod.load_locale("en_US")

    possible_names_to_id = lod.names_to_id

    if object_type:
        possible_names_to_id = {
            name: possible_names_to_id[name]
            for name in possible_names_to_id
            if possible_names_to_id[name].object_type == object_type
        }

    if input_locale:
        locale = get_clean_locale(input_locale)

        # If the locale was not loaded yet, we restart the process
        if locale not in lod.loaded_locales:
            lod.load_locale(locale)
            return get_id(input_str, minimum_score, input_locale, object_type, retry=False)

        possible_names_to_id = {
            name: possible_names_to_id[name]
            for name in possible_names_to_id
            if possible_names_to_id[name].locale == locale
        }

    name_guess, score, idx = extractOne(input_str, possible_names_to_id.keys())

    # TODO Handle multiple objects having the same score (happens with substrings of longer names)
    lit_logger.info(f"Name guess was {name_guess} from {input_str}")

    if score < minimum_score:
        if retry:
            lod.reload_all_locales()
            return get_id(input_str, minimum_score, input_locale, object_type, retry=False)
        else:
            error_text = f"No object name close enough to '{input_str}' found."
            raise NoMatchingNameFound(error_text)

    return lod.names_to_id[name_guess].id


def get_translation(
    object_name: str,
    output_locale: str = "en_US",
    minimum_score: int = 75,
    input_locale: str = None,
    object_type: str = None,
    retry: bool = True,
) -> str:
    """Returns the best translation guess for the given name.

    Will return the id that matches the query best. Best used in curated environments.

    Args:
        object_name: Search string
        output_locale: The language to translate to, with 'en_US' as the default value
        minimum_score: Optional minimum ratio (between 0 and 100) under which the function retries or raises
        input_locale: The language the input was in
        object_type: Optional string in ['champion', 'item', 'rune', 'summoner_spell']
        retry: Optional variable specifying if local_data should be reloaded if the object cannot be found

    Returns:
        The matching object ID

    Raises:
        NoResultFound: No result scored above the minimum_score
        ValueError: One of the input locales was not understood properly

    Usage example:
        get_translation('미스 포츈')
        get_translation('Miss Fortune', 'ko_KR')
        get_translation('mf')
    """
    return get_name(get_id(object_name, minimum_score, input_locale, object_type, retry), output_locale,)
