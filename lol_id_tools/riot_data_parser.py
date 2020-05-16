import logging

from lol_id_tools.local_data_parser import IdInfo

dd_url = 'https://ddragon.leagueoflegends.com'


async def load_objects(riot_data, http_session, latest_version, locale: str, object_type: str):
    """Loads the selected type of objects in the database.

    Queries the Riot servers for the local_data then writes it to the database.
    All three object types are meant to be called together.

    Args:
        riot_data: Dictionary to write to
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
        parse_champions(data, locale, riot_data)
    elif object_type == 'item':
        parse_items(data, locale, riot_data)
    elif object_type == 'rune':
        parse_runes(data, locale, riot_data)


def get_url(latest_version, locale: str, object_type: str):
    # Riot changed name for some reason
    if object_type == 'rune':
        object_type = 'runesReforged'

    return f'{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json'


def parse_champions(data, locale, riot_data):
    for champion_tag, champion_dict in data['data'].items():
        riot_data[locale][int(champion_dict['key'])] = IdInfo(champion_dict['name'], 'champion')


def parse_items(data, locale, riot_data):
    for item_id, item_dict in data['data'].items():
        riot_data[locale][int(item_id)] = IdInfo(item_dict['name'], 'item')


def parse_runes(data, locale, riot_data):
    for rune_tree in data:
        for slot in rune_tree['slots']:
            for rune in slot['runes']:
                riot_data[locale][rune['id']] = IdInfo(rune['name'], 'rune')
