from dataclasses import dataclass
from typing import List
import requests


BASE_URL = (
    "http://raw.communitydragon.org/PATCH/plugins/rcp-be-lol-game-data/global/LOCALE/v1"
)

ENDPOINTS = {
    "ITEM": "items.json",
    "CHAMPION": "champion-summary.json",
    "RUNE": "perks.json",
    "RUNE_TREE": "perkstyles.json",
}


@dataclass(frozen=True)
class ObjectInfo:
    name: str
    id: int
    object_type: str


def get_patch_base_url(patch: str = None, locale: str = None):
    if not patch:
        patch = "latest"
    if not locale:
        locale = "default"

    return BASE_URL.replace("PATCH", patch).replace("LOCALE", locale)


def parse_endpoint(
    endpoint: str, patch: str = None, locale: str = None
) -> List[ObjectInfo]:
    """
    Parses a CDragon endpoint

    Only supports values in ENDPOINTS, should rarely be used as-is
    """

    if endpoint not in ENDPOINTS:
        raise ValueError("Endpoint not understood or supported")

    url = f"{get_patch_base_url(patch, locale)}/{ENDPOINTS[endpoint]}"

    raw_data = requests.get(url).json()

    output = []

    if endpoint == "RUNE_TREE":
        for style in raw_data["styles"]:
            output.append(
                ObjectInfo(name=style["name"], id=style["id"], object_type=endpoint)
            )

        return output

    for champion_dict in raw_data:
        if champion_dict["id"] < 0:
            continue

        output.append(
            ObjectInfo(
                name=champion_dict["name"], id=champion_dict["id"], object_type=endpoint
            )
        )

    return output


def get_full_patch_info(patch: str = None, locale: str = None):
    """
    Queries all available cdragon endpoints for ID information
    """
    patch_id_information = []

    # TODO Make the queries parallel
    for endpoint in ENDPOINTS:
        patch_id_information.extend(
            parse_endpoint(endpoint, patch=patch, locale=locale)
        )

    return patch_id_information

##

