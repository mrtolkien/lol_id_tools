import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "input_id,output_locale,object_type,output",
    [
        # Empty item slots
        (0, None, None, ""),
        (-1, None, None, ""),
        # ID not matching to any item
        (123456789, "en_US", "champion", None),
        # Standard tests
        (21, "en_US", "champion", "Miss Fortune"),
        (21, "ko_KR", "champion", "미스 포츈"),
        (3153, "en_US", "item", "Blade of The Ruined King"),
        (3153, "ko_KR", "item", "몰락한 왕의 검"),
        (8437, "en_US", "rune", "Grasp of the Undying"),
        (8437, "ko_KR", "rune", "착취의 손아귀"),
        (8000, "en_US", "rune", "Precision"),
        (5002, "en_US", "rune", "Armor"),
        (21, "en_US", "summoner_spell", "Barrier"),
        # Removed items tests
        (1400, "en_US", "item", "Stalker's Blade - Warrior"),
        (3025, "en_US", "item", "Iceborn Gauntlet"),
        (3146, "en_US", "item", "Hextech Gunblade"),
    ],
)
def test_get_name(input_id, output_locale, object_type, output):
    assert lol_id_tools.get_name(input_id, output_locale=output_locale, object_type=object_type) == output


@pytest.mark.parametrize(
    "patch,name", [("10.20.1", "Blade of the Ruined King"), ("10.23.1", "Blade of The Ruined King")]
)
def test_botrk_patches(patch, name):
    assert lol_id_tools.get_name(3153, object_type="item", patch=patch) == name


# TODO Add a check without the fallback to None and check it raises
