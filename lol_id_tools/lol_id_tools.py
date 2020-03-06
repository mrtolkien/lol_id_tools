import concurrent.futures
import os
import threading
from pprint import pprint
import logging as log
import requests
import joblib
from fuzzywuzzy import process


class LolIdTools:
    def __init__(self, *init_locales: str):
        """
        A python class for fuzzy matching of champion, items, and rune names in League of Legends.

        :param init_locales: locales to load during initialisation.

        Examples:
            lit = LolIdTools()
                On first run, will create English language data. On subsequent runs, will load existing data.
            lit = LolIdTools('ko_KR')
                Creates Korean language data if not present in the dump file.

        Display runtime information by showing DEBUG level logging: log.basicConfig(level=log.DEBUG)
        """

        # Save directory is ~/.config/lol_id_tools
        self._save_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')
        self._app_data_location = os.path.join(self._save_folder, 'id_dictionary.pkl.z')
        if not os.path.exists(self._save_folder):
            os.makedirs(self._save_folder)

        self._dd_url = 'https://ddragon.leagueoflegends.com/'
        self._nicknames_url = 'https://raw.githubusercontent.com/mrtolkien/lol_id_tools/master/data/nicknames.json'

        self._names_dict_name = 'from_names'
        self._ids_dict_name = 'from_ids'
        self._nicknames_dict = None

        try:
            # Reload the dump
            self._app_data = joblib.load(self._app_data_location)
            self._locales = self._app_data['loaded_locales']
            log.debug('LolIdGetter app data loaded from file. Latest version: {}.'
                      .format(self._app_data['latest_version']))
            # If we instantiated the class new locales, we only create those not loaded yet.
            for locale in init_locales:
                if locale not in self._locales:
                    self.add_locale(locale)
        except (FileNotFoundError, EOFError):
            # If no locales are given and no dump exists, we create the English data as default
            if init_locales == ():
                init_locales = ['en_US']

            self._locales = list(init_locales)
            self.reload_app_data()

    def get_id(self, input_str: str, retry: bool = True):
        """
        Tries to get you the Riot ID for the given input string.
        Logs an INFO level message if matching is slightly unsure, and WARNING if it is very unsure.

        :param input_str: the name of the object you are searching for.
        :param retry: will try once to reload all the data if it is not finding a good match. default is True.

        :return: the ID whose name was closest to the input string.

        Examples:
            lit.get_id('Miss Fortune')
            lit.get_id('MF')
            lit.get_id('미스 포츈')
            lit.get_id('Dio')
        """
        # For performance we directly return if we have a perfect match (case-sensitive)
        if input_str in self._app_data['from_names']:
            return self._app_data['from_names'][input_str]['id']

        tentative_name, ratio = process.extractOne(input_str, self._app_data['from_names'].keys())

        log_output = ' matching from {} to {}. Type: {}, Locale: {}, Ratio {}'.format(
            input_str,
            tentative_name,
            self._app_data['from_names'][tentative_name]['id_type'],
            self._app_data['from_names'][tentative_name]['locale'],
            ratio
        )

        if ratio >= 90:
            log.debug('High confidence' + log_output)
        elif 75 <= ratio < 90:
            log.info('Low confidence' + log_output)
        elif ratio <= 75:
            if retry:
                self.reload_app_data()
                return self.get_id(input_str, False)
            else:
                log.warning('Very low confidence' + log_output)

        return self._app_data['from_names'][tentative_name]['id']

    def get_name(self, input_id: int, locale: str = 'en_US', retry=True):
        """
        Gets you the name for the Riot object with the given ID and locale.

        :param input_id: Riot ID of the object.
        :param locale: Locale you want the name in. default is 'en_US'.
        :param retry: will try once to reload all the data if it is not finding a match. default is True.

        :return: the matching object name. Raises a KeyError if not found.

        Examples:
            lit.get_name(21)
            lit.get_name(21, 'ko_KR')
        """
        if locale not in self._locales:
            self.add_locale(locale)

        try:
            return self._app_data[self._ids_dict_name][input_id, locale]['name']
        except KeyError:
            if retry:
                self.reload_app_data()
                self.get_name(input_id, locale, False)
            else:
                log.error('Could not find the object with ID {}'.format(input_id))
                raise KeyError

    def get_translation(self, input_str: str, output_locale: str = 'en_US', retry: bool = True):
        """
        Tries to get the translation of a given Riot object name matching with the loaded locals.

        :param input_str: name of the object
        :param output_locale: the output locale. default is 'en_US'
        :param retry: will try once to reload all the data if it is not finding a good match. default is True.

        :return: the best translation result through fuzzy matching.

        Examples:
            lit.get_translation('미스 포츈')
            lit.get_translation('Miss Fortune', 'ko_KR')
            lit.get_translation('MF')   # Returns the "clean name" that was fuzzy matched, can be useful too!
        """
        return self.get_name(self.get_id(input_str, retry), output_locale)

    def show_available_locales(self):
        """
        Displays available locales from Riot.
        """
        pprint(self._get_json('{}cdn/languages.json'.format(self._dd_url)))

    def show_loaded_locales(self):
        """
        Displays loaded locales.
        """
        pprint(self._app_data['loaded_locales'])

    def add_locale(self, locale: str):
        """
        Adds a new locale to the package.
        To delete locales, regenerate the data with reload_app_data().

        :param locale: locale to add
        """
        if locale in self._locales:
            print('Trying to add an existing locale. Exiting.')
            return

        # TODO cleanup the nicknames getter as there is slight code duplication between this and reload_app_data.
        self._locales.append(locale)

        nicknames_thread = None
        if self._nicknames_dict is None:
            nicknames_thread = threading.Thread(target=self._load_nicknames)
            nicknames_thread.start()

        # self._app_data['latest_version'] will have a value set if we loaded other locales and speeds things up
        try:
            latest_version = self._app_data['latest_version']
        except (KeyError, AttributeError):
            latest_version = self._get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]

        self._load_locale(locale, latest_version)

        if nicknames_thread is not None:
            nicknames_thread.join()

        self._add_nicknames()

        joblib.dump(self._app_data, self._app_data_location)

    def reload_app_data(self, *locales: str):
        """
        Reloads all the data from scratch and dumps it for future use of the package.

        :param locales: If empty, refreshes the locales already existing. If not, loads only the given locales.

        Examples:
            reload_app_data()
                Refreshes existing locales
            reload_app_data('en_US', 'fr_FR', 'ko_KR')
                Destroys existing locales and loads English, French, and Korean language info.
        """
        if locales != ():
            self._locales = list(locales)

        nicknames_thread = threading.Thread(target=self._load_nicknames)
        nicknames_thread.start()

        self._app_data = {self._names_dict_name: {}, self._ids_dict_name: {},
                          'loaded_locales': [],
                          'latest_version': self._get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]}

        threads_list = [nicknames_thread]
        for locale in self._locales:
            thread = threading.Thread(target=self._load_locale, args=(locale, self._app_data['latest_version'],))
            thread.start()
            threads_list.append(thread)

        for thread in threads_list:
            thread.join()

        self._add_nicknames()

        joblib.dump(self._app_data, self._app_data_location)

    def _load_locale(self, locale, latest_version):
        data = {}
        # We can use a with statement to ensure threads are cleaned up promptly
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            # Start the load operations and mark each future with its URL
            future_to_get = {
                executor.submit(self._get_json,
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
            id_information = {
                'id': int(champion_dict['key']),
                'locale': locale,
                'id_type': 'champion',
                'name': champion_dict['name']
            }
            self._add_id_information(id_information)

        for item_id, item_dict in data['item']['data'].items():
            id_information = {
                'id': int(item_id),
                'locale': locale,
                'id_type': 'item',
                'name': item_dict['name']
            }
            self._add_id_information(id_information)

        for rune_tree in data['runesReforged']:
            for slot in rune_tree['slots']:
                for rune in slot['runes']:
                    id_information = {
                        'id': rune['id'],
                        'locale': locale,
                        'id_type': 'rune',
                        'name': rune['name']
                    }
                    self._add_id_information(id_information)

        self._app_data['loaded_locales'].append(locale)

    def _add_id_information(self, id_info):
        # Adding the name -> ID info mapping
        self._app_data[self._names_dict_name][id_info['name']] = id_info

        # Testing if we have overlapping IDs. Doesn’t happen on patch 10.5
        if (id_info['id'], id_info['locale']) in self._app_data[self._ids_dict_name]:
            log.warning('Multiple objects with ID {}'.format(id_info['id']))
            log.warning('\tExisting object: {}'.format(
                self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']]['name'],
                self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']]['id_type']))
            log.warning('\tNew object: {}/{}'.format(id_info['name'], id_info['id_type']))

        # Adding the ID, locale -> ID info mapping
        self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']] = id_info

    def _load_nicknames(self):
        self._nicknames_dict = self._get_json(self._nicknames_url)

    def _add_nicknames(self):
        for locale in self._nicknames_dict:
            if locale not in self._locales:
                pass
            for nickname, real_name in self._nicknames_dict[locale].items():
                try:
                    self._app_data[self._names_dict_name][nickname] = self._app_data[self._names_dict_name][real_name]
                except KeyError:
                    log.info('Unable to add {}/{} as a nickname because it doesn’t match a Riot name.'
                             .format(nickname, real_name))

    @staticmethod
    def _get_json(url):
        log.debug('Making call: {}'.format(url))
        return requests.get(url=url).json()

##

