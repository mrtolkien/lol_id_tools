import asyncio
import rapidfuzz
from sqlalchemy.orm import Query
from sqlalchemy.orm.exc import NoResultFound
from lol_id_tools.sqlite_interface import ghost_session, LolObject
from lol_id_tools.bulk_loaders import locale_in_database, load_locale, reload_locales


def _load_then_one(query: Query, locale=None, retry=False) -> LolObject:
    """Returns .one() after loading the needed data.

    If a locale is supplied and not in the database, loads it before retrying.

    Args:
        query: An SQLAlchemy-built query.
        locale: Optional locale of the output for name-related queries.
        retry: Optional boolean specifying if we should reload and retry.

    Returns:
        the .one() object of the query.

    Raises:
        NoResultFound: no corresponding row in our database.
    """
    try:
        return query.one()
    except NoResultFound:
        if locale and not locale_in_database(locale):
            asyncio.run(load_locale(locale))
            return _load_then_one(query, None, False)

        if retry:
            asyncio.run(reload_locales())
            return _load_then_one(query, None, False)

        raise KeyError


def get_name(id_: int, locale: str = 'en_US', retry=False):
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

    Usage example:
        get_name(21)
        get_name(21, 'ko_KR')
    """
    lol_object = _load_then_one(ghost_session().query(LolObject)
                                .filter(LolObject.id == id_,
                                        LolObject.locale == locale),
                                locale,
                                retry)

    return lol_object.name
