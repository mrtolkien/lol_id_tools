import asyncio
import logging

import aiohttp
from sqlalchemy import distinct

from lol_id_tools.parsers import load_objects
from lol_id_tools.sqlite_classes import ghost_session, LolObject, object_types_enum


def locale_in_database(locale: str):
    """Checks if the chosen locale has already been loaded.

    Args:
        The locale to check.

    Returns:
        The first object with the corresponding locale or None.
    """
    return ghost_session().query(LolObject.locale).filter(LolObject.locale == locale).first()


async def load_locale(locale, latest_version=None):
    if not latest_version:
        latest_version = await get_latest_version()

    async with aiohttp.ClientSession() as http_session:
        await asyncio.wait([asyncio.create_task(load_objects(http_session, latest_version, locale, object_type))
                            for object_type in object_types_enum.enums])


async def reload_data():
    locales_in_db = ghost_session().query(distinct(LolObject.locale).label('locale'))
    latest_version = await get_latest_version()

    await asyncio.wait([asyncio.create_task(load_locale(row.locale, latest_version)) for row in locales_in_db])


async def get_latest_version():
    async with aiohttp.ClientSession() as http_session:
        url = 'https://ddragon.leagueoflegends.com/api/versions.json'
        async with http_session.get('https://ddragon.leagueoflegends.com/api/versions.json') as response:
            logging.debug(f'Querying {url}')
            data = await response.json()
        return data[0]


def reset_data():
    """Deletes everything in the locale database.

    Mostly for testing purposes.
    """
    lol_objects = ghost_session().query(LolObject)

    for lol_object in lol_objects:
        ghost_session().delete(lol_object)

    ghost_session().commit()
