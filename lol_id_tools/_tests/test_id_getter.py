import os
from unittest import TestCase
import lol_id_tools as lit


class TestIDGetter(TestCase):
    def test___init(self):
        lol_id_getter = lit.LoLIDGetter(['EN', 'KR'])

        self.assertIsNotNone(lol_id_getter.languages)
        self.assertTrue(os.path.exists(lol_id_getter.save_folder))
