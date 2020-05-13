import os
import lol_id_tools as lit
import threading
import pytest


@pytest.fixture()
def id_tool():
    return lit.LolIdTools('en_US', 'ko_KR')


def translation_test(en_name, kr_name, id_tool):
    assert id_tool.get_translation(en_name, 'ko_KR') == kr_name
    assert id_tool.get_translation(kr_name, 'en_US') == en_name


def test_init(id_tool):
    assert id_tool.show_loaded_locales() is None
    assert os.path.exists(id_tool._save_folder)


def test__reload(id_tool):
    id_tool.reload_app_data('en_US', 'ko_KR')

    # Testing on a set so order isn’t an issue.
    # TODO Rework this test after we change internal structure
    assert set(id_tool._app_data[id_tool._locales_list_name]) == {'en_US', 'ko_KR'}


def test__prints(id_tool):
    # Testing console output is annoying, just calling the functions and checking it does not crash!
    # TODO properly test the output
    id_tool.reload_app_data('en_US', 'ko_KR')

    assert id_tool.show_loaded_locales() is None
    assert id_tool.show_available_locales() is None


def test__add_locale(id_tool):
    id_tool.reload_app_data('en_US', 'ko_KR')
    id_tool.add_locale('fr_FR')

    assert set(id_tool._app_data[id_tool._locales_list_name]) == {'en_US', 'ko_KR', 'fr_FR'}


def test_mf_id(id_tool):
    # Base case
    assert id_tool.get_id('Miss Fortune') == 21
    # Case sensitivity test
    assert id_tool.get_id('missfortune') == 21
    # Typo test
    assert id_tool.get_id('misforune') == 21
    # Korean test
    assert id_tool.get_id('미스 포츈') == 21
    # Nickname test
    assert id_tool.get_id('MF') == 21

    # Get name from ID test
    assert id_tool.get_name(21, 'en_US') == 'Miss Fortune'

    # Object type test
    assert id_tool.get_id('Miss Fortune', input_type='item') != 21


def test_mf_translation(id_tool):
    translation_test('Miss Fortune', '미스 포츈', id_tool)


def test_botrk_id(id_tool):
    # Base case
    assert id_tool.get_id('Blade of the Ruined King') == 3153
    # Case sensitivity test
    assert id_tool.get_id('Blade of the ruined king') == 3153
    # Typo test
    assert id_tool.get_id('Blade of the kuined ring') == 3153
    # Korean test
    assert id_tool.get_id('몰락한 왕의 검') == 3153
    # Nickname test
    assert id_tool.get_id('botrk') == 3153

    # Name test
    assert id_tool.get_name(3153, 'en_US') == 'Blade of the Ruined King'

    # Object type test
    assert id_tool.get_id('Blade of the Ruined King', input_type='rune') != 3153


def test_botrk_translation(id_tool):
    translation_test('Blade of the Ruined King', '몰락한 왕의 검', id_tool)


def test_grasp_id(id_tool):
    # Base case
    assert id_tool.get_id('Grasp of the Undying') == 8437
    # Case sensitivity test
    assert id_tool.get_id('grasp of the undying') == 8437
    # Shorthand test
    assert id_tool.get_id('grasp') == 8437
    # Typo test
    assert id_tool.get_id('graps of the undying') == 8437
    # Korean test
    assert id_tool.get_id('착취의 손아귀') == 8437

    # Name test
    assert id_tool.get_name(8437, 'en_US') == 'Grasp of the Undying'

    # Object type test
    assert id_tool.get_id('Grasp of the Undying', input_type='champion') != 8437


def test_grasp_translation(id_tool):
    translation_test('Grasp of the Undying', '착취의 손아귀', id_tool)


def test_parallel_updates(id_tool):
    id_tool.reload_app_data('en_US', 'ko_KR')

    threads_list = []
    for i in range(0, 5):
        thread = threading.Thread(target=id_tool.reload_app_data)
        threads_list.append(thread)
        thread.start()

    for thread in threads_list:
        thread.join()

    # Making sure we still only have two locales
    assert id_tool._app_data[id_tool._locales_list_name].__len__() == 2
    # Testing on a set so order isn’t an issue.
    assert set(id_tool._app_data[id_tool._locales_list_name]) == {'en_US', 'ko_KR'}
