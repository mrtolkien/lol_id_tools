from typing import Dict, TypedDict
import requests

from lol_id_tools import parsing


class PatchData(TypedDict):
    champion: dict
    item: dict
    rune: dict
    summoner_spell: dict


cache: Dict[str, PatchData] = {}


def get_simple_name(
    input_id,
    object_type,
    patch,
):
    if patch not in cache:
        cache[patch] = get_patch_data(patch)

    return cache[patch][object_type][input_id]


def get_patch_data(patch: str):
    patches_list = requests.get(
        "https://ddragon.leagueoflegends.com/api/versions.json"
    ).json()

    try:
        full_patch = next(p for p in patches_list if p.startswith(patch))
    except StopIteration:
        raise ValueError(f"Patch {patch} not found")

    return PatchData(
        champion=parsing.parse_champions(full_patch),
        item=parsing.parse_items(full_patch),
        rune=parsing.parse_runes(full_patch),
        summoner_spell=parsing.parse_summoners(full_patch),
    )
