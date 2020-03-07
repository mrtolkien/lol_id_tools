import os
from unittest import TestCase
import lol_id_tools as lit
import logging as log
log.basicConfig(level=log.DEBUG)


class TestTools(TestCase):
    def test___init(self):
        id_tool = lit.LolIdTools()

        self.assertIsNone(id_tool.show_loaded_locales())
        self.assertTrue(os.path.exists(id_tool._save_folder))

    def test__reload(self):
        id_tool = lit.LolIdTools()

        id_tool.reload_app_data('en_US', 'ko_KR')
        self.assertEqual(id_tool._app_data[id_tool._locales_list_name], ['en_US', 'ko_KR'])

    def test__prints(self):
        # Testing console output is annoying, just calling the functions and checking it doesn’t crash!
        id_tool = lit.LolIdTools()
        id_tool.reload_app_data('en_US', 'ko_KR')

        self.assertIsNone(id_tool.show_loaded_locales())
        self.assertIsNone(id_tool.show_available_locales())

    def test__add_locale(self):
        id_tool = lit.LolIdTools()
        id_tool.reload_app_data('en_US', 'ko_KR')

        id_tool.add_locale('fr_FR')

        self.assertEqual(id_tool._app_data[id_tool._locales_list_name], ['en_US', 'ko_KR', 'fr_FR'])

    def test_mf_id(self):
        id_tool = lit.LolIdTools('en_US', 'ko_KR')

        # Base case
        self.assertEqual(id_tool.get_id('Miss Fortune'), 21)
        # Case sensitivity test
        self.assertEqual(id_tool.get_id('missfortune'), 21)
        # Typo test
        self.assertEqual(id_tool.get_id('misforune'), 21)
        # Korean test
        self.assertEqual(id_tool.get_id('미스 포츈'), 21)
        # Nickname test
        self.assertEqual(id_tool.get_id('MF'), 21)

        # Get name from ID test
        self.assertEqual(id_tool.get_name(21, 'en_US'), 'Miss Fortune')

        # Object type test
        self.assertNotEqual(id_tool.get_id('Miss Fortune', input_type='item'), 21)

    def test_mf_translation(self):
        self._test_translation('Miss Fortune', '미스 포츈')

    def test_botrk_id(self):
        id_tool = lit.LolIdTools('en_US', 'ko_KR')

        # Base case
        self.assertEqual(id_tool.get_id('Blade of the Ruined King'), 3153)
        # Case sensitivity test
        self.assertEqual(id_tool.get_id('Blade of the ruined king'), 3153)
        # Typo test
        self.assertEqual(id_tool.get_id('Blade of the kuined ring'), 3153)
        # Korean test
        self.assertEqual(id_tool.get_id('몰락한 왕의 검'), 3153)
        # Nickname test
        self.assertEqual(id_tool.get_id('botrk'), 3153)

        # Name test
        self.assertEqual(id_tool.get_name(3153, 'en_US'), 'Blade of the Ruined King')

        # Object type test
        self.assertNotEqual(id_tool.get_id('Blade of the Ruined King', input_type='rune'), 3153)

    def test_botrk_translation(self):
        self._test_translation('Blade of the Ruined King', '몰락한 왕의 검')

    def test_grasp_id(self):
        id_tool = lit.LolIdTools('en_US', 'ko_KR')

        # Base case
        self.assertEqual(id_tool.get_id('Grasp of the Undying'), 8437)
        # Case sensitivity test
        self.assertEqual(id_tool.get_id('grasp of the undying'), 8437)
        # Shorthand test
        self.assertEqual(id_tool.get_id('grasp'), 8437)
        # Typo test
        self.assertEqual(id_tool.get_id('graps of the undying'), 8437)
        # Korean test
        self.assertEqual(id_tool.get_id('착취의 손아귀'), 8437)

        # Name test
        self.assertEqual(id_tool.get_name(8437, 'en_US'), 'Grasp of the Undying')

        # Object type test
        self.assertNotEqual(id_tool.get_id('Grasp of the Undying', input_type='champion'), 8437)

    def test_grasp_translation(self):
        self._test_translation('Grasp of the Undying', '착취의 손아귀')

    def _test_translation(self, en_name, kr_name):
        self.assertEqual(lit.LolIdTools('en_US', 'ko_KR').get_translation(en_name, 'ko_KR'), kr_name)
        self.assertEqual(lit.LolIdTools('en_US', 'ko_KR').get_translation(kr_name, 'en_US'), en_name)
