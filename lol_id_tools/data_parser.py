import logging

from lol_id_tools.local_data_parser import IdInfo

dd_url = 'https://ddragon.leagueoflegends.com'


async def load_riot_objects(local_data, http_session, latest_version, locale: str, object_type: str):
    """Loads the selected type of objects in the database.

    Queries the Riot servers for the local_data then writes it to the database.
    All three object types are meant to be called together.

    Args:
        local_data: Dictionary to write to
        http_session: ClientSession that issues the query
        latest_version: the latest version available on dd
        locale: the locale to load
        object_type: the type of object to load
    """
    url = get_ddragon_url(latest_version, locale, object_type)

    async with http_session.get(url) as response:
        logging.debug(f'Querying {url}')
        riot_data = await response.json()

    if object_type == 'champion':
        parse_champions(riot_data, locale, local_data)
    elif object_type == 'item':
        parse_items(riot_data, locale, local_data)
    elif object_type == 'rune':
        parse_runes(riot_data, locale, local_data)


def get_ddragon_url(latest_version, locale: str, object_type: str):
    # Riot changed name for some reason
    if object_type == 'rune':
        object_type = 'runesReforged'

    return f'{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json'


def parse_champions(data, locale, local_data):
    for champion_tag, champion_dict in data['data'].items():
        local_data[locale][int(champion_dict['key'])] = IdInfo(champion_dict['name'], 'champion')


def parse_items(data, locale, local_data):
    for item_id, item_dict in data['data'].items():
        local_data[locale][int(item_id)] = IdInfo(item_dict['name'], 'item')


def parse_runes(data, locale, local_data):
    for rune_tree in data:
        # Adding tree names
        local_data[locale][rune_tree['id']] = IdInfo(rune_tree['key'], 'rune')
        for slot in rune_tree['slots']:
            for rune in slot['runes']:
                local_data[locale][rune['id']] = IdInfo(rune['name'], 'rune')


async def parse_cdragon_runes(local_data, http_session, locale):
    # TODO Clean this up
    cdragon_locale = locale.lower() if locale != 'en_US' else 'default'
    url = f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/{cdragon_locale}/v1/perks.json"

    async with http_session.get(url) as response:
        logging.debug(f'Querying {url}')
        cdragon_data = await response.json()

    for rune in cdragon_data:
        # TODO Get perks in a cleaner way
        if 5000 < rune['id'] < 5010:
            local_data[locale][rune['id']] = IdInfo(rune['name'], 'rune')
