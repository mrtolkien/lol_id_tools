from typing import Dict

import requests


# TODO Move data from ddragon to cdragon to get ID of removed items too


def get_ddragon_url(latest_version, locale: str, object_type: str):
    dd_url = "https://ddragon.leagueoflegends.com"

    return f"{dd_url}/cdn/{latest_version}/data/{locale}/{object_type}.json"


def parse_champions(full_patch: str, locale: str = "en_US") -> Dict[int, str]:
    url = get_ddragon_url(full_patch, locale, "champion")
    data = requests.get(url).json()

    return {
        int(champion_dict["key"]): champion_dict["name"]
        for champion_dict in data["data"].values()
    }


def parse_items(full_patch: str, locale: str = "en_US") -> Dict[int, str]:
    url = get_ddragon_url(full_patch, locale, "item")
    data = requests.get(url).json()

    result = {}

    for item_id, item_dict in data["data"].items():
        if "Enchantment" not in item_dict["name"]:
            result[int(item_id)] = item_dict["name"]

        # Handling old-school jungle enchantments
        else:
            for from_item_id in item_dict["from"]:
                from_item = data["data"][from_item_id]
                if "Jungle" in from_item["tags"]:
                    result[
                        int(item_id)
                    ] = f"{from_item['name']} - {item_dict['name'].replace('Enchantment: ', '')}"

    return result


def parse_runes(full_patch: str, locale: str = "en_US") -> Dict[int, str]:
    url = get_ddragon_url(full_patch, locale, "runesReforged")
    data = requests.get(url).json()

    result = {}

    for rune_tree in data:
        # Adding tree names
        result[rune_tree["id"]] = rune_tree["name"]

        for slot in rune_tree["slots"]:
            for rune in slot["runes"]:
                result[rune["id"]] = rune["name"]

    cdragon_locale = "default"
    url = f"http://raw.communitydragon.org/latest/plugins/rcp-be-lol-game-data/global/{cdragon_locale}/v1/perks.json"

    cdragon_data = requests.get(url).json()

    for rune in cdragon_data:
        if 5000 < rune["id"] < 5010:
            result[rune["id"]] = rune["name"]

    return result


def parse_summoners(full_patch: str, locale: str = "en_US") -> Dict[int, str]:
    url = get_ddragon_url(full_patch, locale, "summoner")
    data = requests.get(url).json()

    return {
        int(data["data"][summoner_spell]["key"]): data["data"][summoner_spell]["name"]
        for summoner_spell in data["data"]
    }
