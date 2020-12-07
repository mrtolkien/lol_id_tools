import pytest
import lol_id_tools.caching.locale_handler


@pytest.mark.parametrize("language_name", ["english", "English", "en_us", "en_US", "NA"])
def test_american_english(language_name):
    assert lol_id_tools.caching.locale_handler.get_clean_locale(language_name) == "en_US"


@pytest.mark.parametrize("language_name", ["korean", "kr", "ko_KR", "kokr"])
def test_korean(language_name):
    assert lol_id_tools.caching.locale_handler.get_clean_locale(language_name) == "ko_KR"
