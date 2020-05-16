import asyncio
from lol_id_tools.levensthein_utils import best_match
from lol_id_tools.local_data_parser import get_clean_locale
from lol_id_tools.lol_object_data import LolObjectData

# Instantiating a LolObjectData object is very light as all its fields are ghost loaded.
lod = LolObjectData()


def get_name(id_: int, locale: str = 'en_US', retry=False) -> str:
    """Gets you the name of the associated Riot object.

    If the chosen locale is not loaded in the database, it will be loaded before returning the result.

    Args:
        id_: Riot ID of the object.
        locale: Locale of the output.
        retry: Optional variable specifying if local_data should be reloaded if the object cannot be found.

    Returns:
        The matching object name.

    Raises:
        KeyError: The corresponding object was not found.
        ValueError: The locale was not understood properly.

    Usage example:
        get_name(21)
        get_name(21, 'ko_KR')
    """
    # We start by cleaning up our locale
    locale = get_clean_locale(locale)

    # First, we see if the object is there with the given constraints
    try:
        return lod.riot_data[locale][id_].name
    except KeyError:
        pass

    if locale not in lod.loaded_locales:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.create_task(lod.load_locale(locale)))
        return get_name(id_, locale, False)

    if retry:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.create_task(lod.reload_all_locales()))
        return get_name(id_, locale, False)

    raise KeyError('The associated Riot object could not be found.')


class NoMatchingNameFound(Exception):
    pass


def get_id(object_name: str, minimum_score: int = 75,
           input_locale: str = None, object_type: str = None, retry: bool = False) -> int:
    """Returns the best Riot ID guess for the given name.

    Will return the id that matches the query best. Best used in curated environments.

    Args:
        object_name: Search string.
        minimum_score: Optional minimum ratio (between 0 and 100) under which the function retries or raises.
        input_locale: The language the input was in.
        object_type: Optional boolean specifying the type of the object in [champion, item, rune].
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
    object_name = object_name.lower()

    # Handling some Leaguepedia special cases as having an ID of 0, might be stupid and should just raise
    if not object_name or object_name == 'none' or object_name == 'loss of ban' or object_name == 'no item':
        return 0

    # First, we try to directly get the object with the exact input name
    try:
        return lod.names_to_id[object_name].id
    except KeyError:
        pass

    possible_names = lod.names_to_id

    if object_type:
        possible_names = {name: possible_names[name] for name in possible_names
                          if possible_names[name].object_type == object_type}

    if input_locale:
        locale = get_clean_locale(input_locale)

        # If the locale was not loaded yet, we restart the process
        if locale not in lod.loaded_locales:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(loop.create_task(lod.load_locale(locale)))
            return get_id(object_name, minimum_score, input_locale, object_type, False)

        possible_names = {name: possible_names[name] for name in possible_names
                          if possible_names[name].locale == locale}

    name_guess, score = best_match(object_name, possible_names.keys())

    if score*100 < minimum_score:
        if retry:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(loop.create_task(lod.reload_all_locales()))
            return get_id(object_name, minimum_score, input_locale, object_type, False)
        else:
            raise NoMatchingNameFound('No object name close enough to the input string found.')

    return lod.names_to_id[name_guess].id


def get_translation(object_name: str, output_locale: str = 'en_US', minimum_score: int = 75,
                    input_locale: str = None, object_type: str = None, retry: bool = False) -> str:
    """Returns the best translation guess for the given name.

    Will return the id that matches the query best. Best used in curated environments.

    Args:
        object_name: Search string.
        output_locale: The language to translate to, with 'en_US' as the default value.
        minimum_score: Optional minimum ratio (between 0 and 100) under which the function retries or raises.
        input_locale: The language the input was in.
        object_type: Optional boolean specifying the type of the object in [champion, item, rune].
        retry: Optional variable specifying if local_data should be reloaded if the object cannot be found.

    Returns:
        The matching object ID.

    Raises:
        NoResultFound: No result scored above the minimum_score.
        ValueError: One of the input locales was not understood properly.

    Usage example:
        get_translation('미스 포츈')
        get_translation('Miss Fortune', 'ko_KR')
        get_translation('mf')
    """
    return get_name(get_id(object_name, minimum_score, input_locale, object_type, retry), output_locale)
