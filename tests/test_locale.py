import pytest
import lol_id_tools.caching.locale_handler


# TODO Add "NA", "en_us", "EUW" once server support is written
@pytest.mark.parametrize("language_name", ["english", "English", "en_US"])
def test_american_english(language_name):
    assert lol_id_tools.caching.locale_handler.get_clean_locale(language_name) == "en_US"


@pytest.mark.parametrize("language_name", ["korean", "ko_KR"])
def test_korean(language_name):
    assert lol_id_tools.caching.locale_handler.get_clean_locale(language_name) == "ko_KR"
