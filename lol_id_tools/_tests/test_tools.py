import os
from unittest import TestCase
import lol_id_tools as lit
import logging as log
log.basicConfig(level=log.DEBUG)


class TestTools(TestCase):
    def test___init(self):
        id_tool = lit.LolIdTools()

        self.assertIsNotNone(id_tool._locales)
        self.assertTrue(os.path.exists(id_tool._save_folder))

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

    def test_grasp_translation(self):
        self._test_translation('Grasp of the Undying', '착취의 손아귀')

    def _test_translation(self, en_name, kr_name):
        self.assertEqual(lit.LolIdTools('en_US', 'ko_KR').get_translation(en_name, 'ko_KR'), kr_name)
        self.assertEqual(lit.LolIdTools('en_US', 'ko_KR').get_translation(kr_name, 'en_US'), en_name)
