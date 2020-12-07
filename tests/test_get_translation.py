import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "input_str,input_locale, output_locale,object_type,output",
    [
        ("Miss Fortune", "en_US", "ko_KR", "champion", "미스 포츈"),
        ("Blade of The Ruined King", "en_US", "ko_KR", "item", "몰락한 왕의 검"),
        ("Grasp of the Undying", "en_US", "ko_KR", "rune", "착취의 손아귀"),
    ],
)
def test_get_translation(input_str, input_locale, output_locale, object_type, output):
    assert (
        lol_id_tools.get_translation(
            input_str, input_locale=input_locale, output_locale=output_locale, object_type=object_type
        )
        == output
    )
