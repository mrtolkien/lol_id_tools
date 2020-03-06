import os


class LoLIDGetter:
    def __init__(self, languages_list: list):
        self.languages = languages_list
        self.save_folder = os.path.join(os.path.expanduser("~"), '.lol_data')

        if not os.path.exists(self.save_folder):
            os.makedirs(self.save_folder)
