import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "input_str,input_locale,object_type,output",
    [
        # Empty items
        ("", "", "", 0),
        ("no item", "", "", 0),
        # Standard test with typos and nicknames
        ("Miss Fortune", "en_US", "champion", 21),
        ("MF", "en_US", "champion", 21),
        ("missfortune", "en_US", "champion", 21),
        ("misforune", "en_US", "champion", 21),
        ("미스 포츈", "ko_KR", "champion", 21),
        ("Miss Fortune", "fr_FR", "champion", 21),
        ("Blade of The Ruined King", "en_US", "item", 3153),
        ("Blade of the ruined king", "en_US", "item", 3153),
        ("botrk", "en_US", "item", 3153),
        ("몰락한 왕의 검", "ko_KR", "item", 3153),
        ("Grasp of the Undying", "en_US", "rune", 8437),
        ("grasp of the undying", "en_US", "rune", 8437),
        ("Grasp", "en_US", "rune", 8437),
        ("undying", "en_US", "rune", 8437),
        ("graps of the undying", "en_US", "rune", 8437),
        ("착취의 손아귀", "ko_KR", "rune", 8437),
        ("precision", "en_US", "rune", 8000),
        ("armor", "en_US", "rune", 5002),
        ("barrier", "en_US", "summoner_spell", 21),
        # Items removed in recent versions
        ("Stalker's Blade - Warrior", "en_US", "item", 1400),
        ("Iceborn Gauntlet", "en_US", "item", 3025),
        ("Hextech Gunblade", "en_US", "item", 3146),
    ],
)
def test_get_id(input_str, input_locale, object_type, output):
    assert lol_id_tools.get_id(input_str, input_locale=input_locale, object_type=object_type) == output

# TODO Write non-working values and check they properly raise
# Non-working values
# ("QWERTYUIOP", "en_US", "champion", None),
# ("TEST", "en_US", "champion", None),
