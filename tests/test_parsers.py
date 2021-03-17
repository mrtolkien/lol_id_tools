from lol_id_tools.parsers.cdragon_parser import parse_endpoint, get_full_patch_info
import pytest


patches_list = ["latest", "10.20", "9.10", "8.10"]


def test_get_champions():
    champions = parse_endpoint("CHAMPION")

    assert len(champions) > 150

    assert next(o for o in champions if o.name == "Annie")


@pytest.mark.parametrize(
    "patch",
    patches_list,
)
def test_get_items(patch):
    items = parse_endpoint("ITEM", patch=patch)

    assert len(items) > 200

    assert next(o for o in items if o.name == "Long Sword")


@pytest.mark.parametrize(
    "patch",
    patches_list,
)
def test_get_runes_reforged(patch):
    runes = parse_endpoint("RUNE", patch=patch)

    assert len(runes) > 30


def test_get_rune_trees():
    runes = parse_endpoint("RUNE_TREE")

    assert len(runes) == 5


def test_get_full_patch_info():
    data = get_full_patch_info()

    assert len(data) > 400


# TODO Add old runes and items tests and function
