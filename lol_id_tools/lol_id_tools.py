import asyncio
import rapidfuzz
from lol_id_tools.data.local_data import nicknames, clean_locale
from lol_id_tools.sqlite_classes import ghost_session, LolObject
from lol_id_tools.loaders import locale_in_database, load_locale, reload_data


def get_name(id_: int, locale: str = 'en_US', retry=False) -> str:
    """Gets you the name of the associated Riot object.

    If the chosen locale is not loaded in the database, it will be loaded before returning the result.

    Args:
        id_: Riot ID of the object.
        locale: Locale of the output.
        retry: Optional variable specifying if data should be reloaded if the object cannot be found.

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
    locale = clean_locale(locale)

    # First, we see if the object is there with the given constraints
    # Not using walrus operator to keep 3.5+ compatibility.
    try:
        return ghost_session().query(LolObject)\
            .filter(LolObject.id == id_, LolObject.locale == locale).one_or_none().name
    except AttributeError:
        pass

    if not locale_in_database(locale):
        asyncio.run(load_locale(locale))
        return get_name(id_, locale, False)

    if retry:
        asyncio.run(reload_data())
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
        minimum_score: Optional minimum Levensthein distance score under which the function retries or raises.
        input_locale: The language the input was in.
        object_type: Optional boolean specifying the type of the object in [champion, item, rune].
        retry: Optional variable specifying if data should be reloaded if the object cannot be found.

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
    # Handling some Leaguepedia special cases as a 0 item (
    if not object_name or object_name == 'None' or object_name == 'Loss of Ban' or object_name == 'No item':
        return 0

    # First, we try to directly get the object with the exact input name
    try:
        return ghost_session().query(LolObject.id).filter(LolObject.name == object_name).first().id
    except AttributeError:
        pass

    names_query = ghost_session().query(LolObject.id, LolObject.name)

    if object_type:
        names_query = names_query.filter(LolObject.object_type == object_type)

    if input_locale:
        locale = clean_locale(input_locale)

        # If the locale was not loaded yet, we restart the process
        if not locale_in_database(locale):
            asyncio.run(load_locale(locale))
            return get_id(object_name, minimum_score, input_locale, object_type, False)

        # If it was, we filter on it
        names_query = names_query.filter(LolObject.locale == locale)

    # TODO Review how we work with nicknames, likely put them in the sqlite DB too
    # TODO Find a smarter way to do the fuzzy matching with sqlite or change backend
    name_guess, score = rapidfuzz.process.extractOne(object_name,
                                                     [row.name for row in names_query] + list(nicknames.keys()))

    # If our result is a nickname, we go get the clean name
    if name_guess in nicknames:
        name_guess = nicknames[name_guess]

    if score < minimum_score:
        if not retry:
            raise NoMatchingNameFound('No object name close enough to the input string found.')
        else:
            reload_data()
            return get_id(object_name, minimum_score, input_locale, object_type, False)

    return ghost_session().query(LolObject.id).filter(LolObject.name == name_guess).first().id


def get_translation(object_name: str, output_locale: str = 'en_US', minimum_score: int = 75,
                    input_locale: str = None, object_type: str = None, retry: bool = False) -> str:
    """Returns the best translation guess for the given name.

    Will return the id that matches the query best. Best used in curated environments.

    Args:
        object_name: Search string.
        output_locale: The language to translate to, with 'en_US' as the default value.
        minimum_score: Optional minimum Levensthein distance score under which the function retries or raises.
        input_locale: The language the input was in.
        object_type: Optional boolean specifying the type of the object in [champion, item, rune].
        retry: Optional variable specifying if data should be reloaded if the object cannot be found.

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
