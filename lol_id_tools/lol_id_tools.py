import concurrent.futures
import os
import threading
from collections import defaultdict
from pprint import pprint
import requests
import joblib


class LolIdTools:
    def __init__(self, *locales: str):
        """
        A python class for fuzzy matching of champion, items, and rune names in League of Legends.

        :param locales: locales to load during initialisation. Default: en_US.
        """
        # If no locales are given, it still unpacks into an empty tuple
        if locales == ():
            locales = ('en_US', )

        # Default save directory is ~/.config/lol_id_tools
        self._save_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')
        self._app_data_location = os.path.join(self._save_folder, 'id_dictionary.pkl.z')
        if not os.path.exists(self._save_folder):
            os.makedirs(self._save_folder)

        self._dd_url = 'https://ddragon.leagueoflegends.com/'

        # First, we try to load existing files.
        try:
            # By default, this should be almost instant
            self._app_data = joblib.load(self._app_data_location)
            self._locales = self._app_data['loaded_locales']
            # If we instantiated the class with new locales, we only load those.
            for locale in locales:
                if locale not in self._locales:
                    self.add_locale(locale)
        except (FileNotFoundError, EOFError) as e:
            self._locales = locales
            self._recreate_app_data()

    def show_available_locales(self):
        pprint(self._get_json('https://ddragon.leagueoflegends.com/cdn/languages.json'))

    def show_loaded_locales(self):
        pprint(self._app_data['loaded_locales'])

    def add_locale(self, locale: str):
        pass

    def get_id(self, input_str: str, retry=True):
        # First, check if the string is directly in the dictionary (instant?)
        # Then extract one with FuzzyMatching and update depending on ratio
        pass

    def get_translation(self, input_str: str, output_locale: str = 'en_US'):
        pass

    def _recreate_app_data(self):
        self._app_data = defaultdict(dict)
        self._app_data['loaded_locales'] = []

        self._app_data['latest_version'] = self._get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]

        threads_list = []
        for locale in self._locales:
            thread = threading.Thread(target=self._add_locale, args=(locale, self._app_data['latest_version'],))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        joblib.dump(self._app_data, self._app_data_location)

    def _add_locale(self, locale, latest_version):
        nicknames_thread = threading.Thread(target=self._add_nicknames, args=(locale,))
        nicknames_thread.start()

        data = {}
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Start the load operations and mark each future with its URL
            future_to_get = {executor.submit(self._get_json,
                                             '{}cdn/{}/data/{}/{}.json'
                                             .format(self._dd_url, latest_version, locale, key)): key
                             for key in ['item', 'runesReforged', 'champion']
                             }
            for future in concurrent.futures.as_completed(future_to_get):
                request_type = future_to_get[future]
                try:
                    data[request_type] = future.result()
                except Exception as exc:
                    print('%r generated an exception: %s' % (request_type, exc))

        for champion_tag, champion_dict in data['champion']['data'].items():
            id_info = {
                'id': champion_dict['key'],
                'locale': locale,
                'id_type': 'champion',
                'clean_name': champion_dict['name']
            }
            self._app_data['from_names'][champion_dict['name']] = id_info
            self._app_data['from_names'][champion_dict['title']] = id_info

            self._app_data['from_id_locale'][champion_dict['key'], locale] = champion_dict['name']

        for item_id, item_dict in data['item']['data'].items():
            id_info = {
                'id': int(item_id),
                'locale': locale,
                'id_type': 'item',
                'clean_name': item_dict['name']
            }
            self._app_data['from_names'][item_dict['name']] = id_info
            self._app_data['from_id_locale'][int(item_id), locale] = item_dict['name']

        for rune_tree in data['runesReforged']:
            for slot in rune_tree['slots']:
                for rune in slot['runes']:
                    id_info = {
                        'id': rune['id'],
                        'locale': locale,
                        'id_type': 'rune',
                        'clean_name': rune['name']
                    }
                    self._app_data['from_names'][rune['name']] = id_info
                    self._app_data['from_id_locale'][rune['id'], locale] = rune['name']

        # It's almost impossible this thread hasn't finished... But you never know!
        nicknames_thread.join()

        self._app_data['loaded_locales'].append(locale)

    def _add_nicknames(self, locale):
        pass

    @staticmethod
    def _get_json(url):
        print('Making call: {}'.format(url))
        return requests.get(url=url).json()

##
