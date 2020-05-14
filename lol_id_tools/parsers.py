import logging
from lol_id_tools.sqlite_interface import ghost_session, LolObject

dd_url = 'https://ddragon.leagueoflegends.com'


async def load_objects(http_session, latest_version, locale: str, object_type: str):
    """Loads the selected type of objects in the database.

    Queries the Riot servers for the data then writes it to the database.
    All three object types are meant to be called together.

    Args:
        http_session: ClientSession that issues the query
        latest_version: the latest version available on dd
        locale: the locale to load
        object_type: the type of object to load
    """
    url = get_url(latest_version, locale, object_type)

    async with http_session.get(url) as response:
        logging.debug(f'Querying {url}')
        data = await response.json()

    if object_type == 'champion':
        parse_champions(data, locale)
    elif object_type == 'item':
        parse_items(data, locale)
    elif object_type == 'rune':
        parse_runes(data, locale)

    ghost_session().commit()


def get_url(latest_version, locale: str, object_type: str):
    # Riot changed name for some reason
    if object_type == 'rune':
        object_type = 'runesReforged'

    return f'{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json'


def parse_champions(data, locale):
    for champion_tag, champion_dict in data['data'].items():
        lol_object = LolObject(int(champion_dict['key']),
                               locale,
                               champion_dict['name'],
                               'champion')
        ghost_session().merge(lol_object)


def parse_items(data, locale):
    for item_id, item_dict in data['data'].items():
        lol_object = LolObject(int(item_id),
                               locale,
                               item_dict['name'],
                               'item')
        ghost_session().merge(lol_object)


def parse_runes(data, locale):
    for rune_tree in data:
        for slot in rune_tree['slots']:
            for rune in slot['runes']:
                lol_object = LolObject(rune['id'],
                                       locale,
                                       rune['name'],
                                       'rune')
                ghost_session().merge(lol_object)
