from concurrent.futures.thread import ThreadPoolExecutor
import lol_id_tools as lit

import os

try:
    os.remove(lit.lol_id_tools.lod.data_location)
except FileNotFoundError:
    pass


def translation_test_function(en_name, kr_name):
    assert lit.get_translation(en_name, "ko_KR") == kr_name
    assert lit.get_translation(kr_name, "en_US") == en_name


def test_mf_id():
    # Base case
    assert lit.get_id("Miss Fortune", object_type="champion") == 21
    # Case sensitivity test
    assert lit.get_id("missfortune", object_type="champion") == 21
    # Typo test
    assert lit.get_id("misforune", object_type="champion") == 21

    # Different languages test
    assert lit.get_id("미스 포츈", input_locale="ko_KR") == 21
    assert lit.get_id("미스 포츈", input_locale="korean") == 21
    assert lit.get_id("missfortune", input_locale="french") == 21

    # Nickname test
    assert lit.get_id("MF") == 21

    # Get name from ID test
    assert lit.get_name(21, object_type="champion") == "Miss Fortune"


def test_mf_translation():
    translation_test_function("Miss Fortune", "미스 포츈")


def test_botrk_id():
    # Base case
    assert lit.get_id("Blade of the Ruined King") == 3153
    # Case sensitivity test
    assert lit.get_id("Blade of the ruined king") == 3153
    # Typo test
    assert lit.get_id("Blade of the kuined ring") == 3153
    # Korean test
    assert lit.get_id("몰락한 왕의 검") == 3153
    # Nickname test
    assert lit.get_id("botrk") == 3153

    # Name test
    assert lit.get_name(3153, object_type="item") == "Blade of the Ruined King"


def test_botrk_translation():
    translation_test_function("Blade of The Ruined King", "몰락한 왕의 검")


def test_grasp_id():
    # Base case
    assert lit.get_id("Grasp of the Undying") == 8437
    # Case sensitivity test
    assert lit.get_id("grasp of the undying") == 8437
    # Shorthand test
    assert lit.get_id("undying") == 8437
    # Typo test
    assert lit.get_id("graps of the undying") == 8437
    # Korean test
    assert lit.get_id("착취의 손아귀") == 8437

    # Name test
    assert lit.get_name(8437, object_type="rune") == "Grasp of the Undying"


def test_grasp_translation():
    translation_test_function("Grasp of the Undying", "착취의 손아귀")


def test_jungle_item():
    assert lit.get_name(1400) == "Stalker's Blade - Warrior"


def test_keystone():
    assert lit.get_name(8000) == "Precision"


def test_perks():
    assert lit.get_name(5002) == "Armor"


def test_summoner_spell():
    assert lit.get_name(21, object_type="summoner_spell") == "Barrier"


def test_parallel_updates():
    # Just checking nothing crashes
    with ThreadPoolExecutor() as executor:
        for i in range(0, 5):
            executor.submit(lit.get_id, "nonsense", 100, retry=True)
