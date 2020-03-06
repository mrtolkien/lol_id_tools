import os


class LolIdTools:
    def __init__(self, *args: str):
        self.languages = args
        self.save_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)

    def get_id(self, input_str: str):
        pass

    def get_translation(self, input_str: str, output_language: str = 'EN'):
        pass
