import asyncio
import aiohttp

from lol_id_tools.parsers import load_objects
from lol_id_tools.sqlite_interface import ghost_session, LolObject, object_types_enum


def locale_in_database(locale: str):
    """Checks if the chosen locale has already been loaded.

    Args:
        The locale to check.

    Returns:
        The first object with the corresponding locale or None.
    """
    return ghost_session().query(LolObject.locale).filter(LolObject.locale == locale).first()


async def load_locale(locale):
    # TODO Grab the latest version
    latest_version = '10.9.1'
    async with aiohttp.ClientSession() as http_session:
        await asyncio.wait([asyncio.create_task(load_objects(http_session, latest_version, locale, object_type))
                            for object_type in object_types_enum.enums])


async def reload_locales():
    pass
