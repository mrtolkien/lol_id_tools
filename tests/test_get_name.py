import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "input_id,output_locale,object_type,output",
    [
        (0, None, None, ""),
        (-1, None, None, ""),
        (21, "en_US", "champion", "Miss Fortune"),
        (21, "ko_KR", "champion", "미스 포츈"),
        (3153, "en_US", "item", "Blade of The Ruined King"),
        (3153, "ko_KR", "item", "몰락한 왕의 검"),
        (8437, "en_US", "rune", "Grasp of the Undying"),
        (8437, "ko_KR", "rune", "착취의 손아귀"),
        (8000, "en_US", "rune", "Precision"),
        (5002, "en_US", "rune", "Armor"),
        (21, "en_US", "summoner_spell", "Barrier"),
    ],
)
def test_get_name(input_id, output_locale, object_type, output):
    assert lol_id_tools.get_name(input_id, output_locale=output_locale, object_type=object_type) == output
