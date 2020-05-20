import logging

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
    elif object_type == 'summoner_spell':
        parse_summoner_spells(riot_data, locale, local_data)


def get_ddragon_url(latest_version, locale: str, object_type: str):
    # Riot changed name for some reason
    if object_type == 'rune':
        object_type = 'runesReforged'
    elif object_type == 'summoner_spell':
        object_type = 'summoner'

    return f'{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json'


def parse_champions(data, locale, local_data):
    for champion_tag, champion_dict in data['data'].items():
        local_data[locale][int(champion_dict['key'])]['champion'] = champion_dict['name']


def parse_items(data, locale, local_data):
    for item_id, item_dict in data['data'].items():
        local_data[locale][int(item_id)]['item'] = item_dict['name']


def parse_runes(data, locale, local_data):
    for rune_tree in data:
        # Adding tree names
        local_data[locale][rune_tree['id']]['rune'] = rune_tree['name']
        for slot in rune_tree['slots']:
            for rune in slot['runes']:
                local_data[locale][rune['id']]['rune'] = rune['name']


def parse_summoner_spells(riot_data, locale, local_data):
    for summoner_spell in riot_data['data']:
        summoner_spell_info = riot_data['data'][summoner_spell]
        local_data[locale][int(summoner_spell_info['key'])]['summoner_spell'] = summoner_spell_info['name']


async def parse_cdragon_runes(local_data, http_session, locale):
    # TODO Clean this up
    cdragon_locale = locale.lower() if locale != 'en_US' else 'default'
    url = f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/{cdragon_locale}/v1/perks.json"

    async with http_session.get(url) as response:
        logging.debug(f'Querying {url}')
        cdragon_data = await response.json()

    for rune in cdragon_data:
        # TODO Get perks only in a cleaner way
        if 5000 < rune['id'] < 5010:
            local_data[locale][rune['id']]['rune'] = rune['name']
