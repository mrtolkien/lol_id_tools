import pytest
import requests

import lol_id_tools
from lol_id_tools import parsing


latest_version = requests.get(
    "https://ddragon.leagueoflegends.com/api/versions.json"
).json()[0]


def test_parse_champions():
    data = parsing.parse_champions(latest_version)

    # More champions than Pokemons
    assert len(data) > 150

    for id_, name in data.items():
        # We test using the *old* parser!
        assert name == lol_id_tools.get_name(id_, object_type="champion")


def test_parse_items():
    data = parsing.parse_items(latest_version)

    # More items than Pokemons
    assert len(data) > 200

    for id_, name in data.items():
        # We test using the *old* parser!
        assert name == lol_id_tools.get_name(id_, object_type="item")


def test_parse_runes():
    data = parsing.parse_runes(latest_version)

    # Not that many runes really
    assert len(data) > 5 * 9

    for id_, name in data.items():
        # We test using the *old* parser!
        assert name == lol_id_tools.get_name(id_, object_type="rune")


def test_parse_summoners():
    data = parsing.parse_summoners(latest_version)

    # Not that many summoners
    assert len(data) > 5

    for id_, name in data.items():
        # We test using the *old* parser!
        assert name == lol_id_tools.get_name(id_, object_type="summoner_spell")


@pytest.mark.parametrize(
    "tuple",
    [
        (1, "Annie", "champion", "12.3"),
        (1400, "Stalker's Blade - Warrior", "item", "10.1"),
        (8135, "Treasure Hunter", "rune", "12.6"),
        (8135, "Ravenous Hunter", "rune", "12.5"),
    ],
)
def test_get_name_with_patch(tuple):
    id_, name, type_, patch = tuple

    response = lol_id_tools.get_name(
        id_,
        object_type=type_,
        patch=patch,
    )

    assert response == name


def test_class():
    lit = lol_id_tools.VersionedNameGetter("12.6")

    assert "Annie" == lit.get_name(1, object_type="champion")
    assert "Treasure Hunter" == lit.get_name(8135, object_type="rune")
