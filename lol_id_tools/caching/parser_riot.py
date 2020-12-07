from lol_id_tools.logger import lit_logger
import requests

dd_url = "https://ddragon.leagueoflegends.com"

# TODO Move data from ddragon to cdragon to get ID of removed items too


def load_riot_objects(local_data, latest_version, locale: str, object_type: str):
    """Loads the selected type of objects in the database.

    Queries the Riot servers for the local_data then writes it to the database.
    All three object types are meant to be called together.

    Args:
        local_data: Dictionary to write to
        latest_version: the latest version available on dd
        locale: the locale to load
        object_type: the type of object to load__
    """
    url = get_ddragon_url(latest_version, locale, object_type)

    lit_logger.debug(f"Querying {url}")
    response = requests.get(url)

    riot_data = response.json()

    if object_type == "champion":
        parse_champions(riot_data, locale, local_data)
    elif object_type == "item":
        parse_items(riot_data, locale, local_data)
    elif object_type == "runesReforged":
        parse_runes(riot_data, locale, local_data)
    elif object_type == "summoner":
        parse_summoner_spells(riot_data, locale, local_data)


def get_ddragon_url(latest_version, locale: str, object_type: str):
    # Riot changed name for some reason
    return f"{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json"


def parse_champions(data, locale, local_data):
    for champion_tag, champion_dict in data["data"].items():
        local_data[locale][int(champion_dict["key"])]["champion"] = champion_dict["name"]


def parse_items(data, locale, local_data):
    for item_id, item_dict in data["data"].items():
        if "Enchantment" not in item_dict["name"]:
            local_data[locale][int(item_id)]["item"] = item_dict["name"]
        else:
            for from_item_id in item_dict["from"]:
                from_item = data["data"][from_item_id]
                if "Jungle" in from_item["tags"]:
                    local_data[locale][int(item_id)][
                        "item"
                    ] = f"{from_item['name']} - {item_dict['name'].replace('Enchantment: ', '')}"


def parse_runes(data, locale, local_data):
    for rune_tree in data:
        # Adding tree names
        local_data[locale][rune_tree["id"]]["rune"] = rune_tree["name"]
        for slot in rune_tree["slots"]:
            for rune in slot["runes"]:
                local_data[locale][rune["id"]]["rune"] = rune["name"]


def parse_summoner_spells(riot_data, locale, local_data):
    for summoner_spell in riot_data["data"]:
        summoner_spell_info = riot_data["data"][summoner_spell]
        local_data[locale][int(summoner_spell_info["key"])]["summoner_spell"] = summoner_spell_info["name"]


def parse_cdragon_runes(local_data, locale):
    # TODO Clean this up
    cdragon_locale = locale.lower() if locale != "en_US" else "default"
    url = f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/{cdragon_locale}/v1/perks.json"

    lit_logger.debug(f"Querying {url}")
    response = requests.get(url)
    cdragon_data = response.json()

    for rune in cdragon_data:
        # TODO Get perks only in a cleaner way
        if 5000 < rune["id"] < 5010:
            local_data[locale][rune["id"]]["rune"] = rune["name"]
