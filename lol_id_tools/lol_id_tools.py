import concurrent.futures
import os
import time
from concurrent.futures.thread import ThreadPoolExecutor
from pprint import pprint
import logging as log
import requests
import joblib
from fuzzywuzzy import process


class LolIdTools:
    # TODO Use async/await instead of multi threading everywhere!
    # TODO Currently this works very stupidly with concurrent instances running. Needs a deep cleanup.
    def __init__(self, *init_locales: str):
        """
        A python class for fuzzy matching of champion, items, and rune names in League of Legends.

        :param init_locales: additional locales to load during initialisation.
                    Loads 'en_US' on first run if nothing is specified.

        Examples:
            lit = LolIdTools()
                On first run, will create English language data. On subsequent runs, will load existing data.
            lit = LolIdTools('ko_KR')
                Creates Korean language data if not present in the dump file.

        Display runtime information by showing DEBUG level logging: log.basicConfig(level=log.DEBUG)
        """
        # Save directory is ~/.config/lol_id_tools
        self._save_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')
        if not os.path.exists(self._save_folder):
            os.makedirs(self._save_folder)

        self._app_data_location = os.path.join(self._save_folder, 'id_dictionary.pkl.z')

        self._dd_url = 'https://ddragon.leagueoflegends.com/'
        self._nicknames_url = 'https://raw.githubusercontent.com/mrtolkien/lol_id_tools/master/data/nicknames.json'

        # TODO Review data format, currently everything is in a big dictionary. A dedicated class would be better.
        self._names_dict_name = 'from_names'
        self._ids_dict_name = 'from_ids'
        self._locales_list_name = 'loaded_locales'
        self._latest_version_name = 'latest_version'

        self.updating = False

        try:
            # Try to reload the dump
            self._app_data = joblib.load(self._app_data_location)
            log.debug('LolIdGetter app data loaded from file. Latest version: {}.'
                      .format(self._app_data[self._latest_version_name]))
            # If we instantiated the class with new locales, we only create those not loaded yet.
            for locale in init_locales:
                if locale not in self._app_data[self._locales_list_name]:
                    # TODO This ain’t even parallel... Rework it.
                    self.add_locale(locale)
        except (FileNotFoundError, EOFError):
            # If no locales are given and no dump exists, we create the English data as default
            if init_locales == ():
                init_locales = 'en_US'

            self.reload_app_data(init_locales)

    def get_id(self, input_str: str, input_type: str = None, locale: str = None, retry: bool = False, return_ratio=False):
        """
        Tries to get you the Riot ID for the given input string. Can be made more precise with optional arguments.
        Logs an INFO level message if matching is slightly unsure, and WARNING if it is very unsure.

        :param input_str: the name of the object you are searching for. Required argument.
        :param input_type: accepts 'champion', 'item', 'rune'. Default is None.
        :param locale: accepts any locale and will load it if needed. Default is None.
        :param retry: will try once to reload all the data if it is not finding a good match. Default is True.
        :param return_ratio: returns (id, ratio) instead of just id

        :return: the ID whose name was closest to the input string.

        Examples:
            lit.get_id('Miss Fortune')
            lit.get_id('MF')
            lit.get_id('미스 포츈')
            lit.get_id('Dio')
        """
        # TODO make it work better with PyCharm’s console and eager loading, it creates issues at the moment
        # TODO make all functions also return ratio, and None + ratio in case of weird queries?
        # Handling some Leaguepedia special cases!
        if input_str is None or input_str == 'None' or input_str == 'Loss of Ban' or input_str == '':
            return None

        search_list = self._app_data[self._names_dict_name].keys()
        if input_type is not None:
            search_list = [n for n in search_list if self._app_data[self._names_dict_name][n]['id_type'] == input_type]
        if locale is not None:
            search_list = [n for n in search_list if self._app_data[self._names_dict_name][n]['locale'] == locale]

        # For performance we directly return if we have a perfect match (case-sensitive)
        if input_str in search_list:
            return self._app_data[self._names_dict_name][input_str]['id']

        tentative_name, ratio = process.extractOne(input_str, search_list)

        log_output = ' matching from {} to {}.\nType: {}, Locale: {}, Precision ratio: {}'.format(
            input_str,
            tentative_name,
            self._app_data['from_names'][tentative_name]['id_type'],
            self._app_data['from_names'][tentative_name]['locale'],
            ratio
        )

        if ratio >= 90:
            log.debug('\tHigh confidence' + log_output)
        elif 75 <= ratio < 90:
            log.info('\tLow confidence' + log_output)
        elif ratio <= 75:
            if retry:
                self.reload_app_data()
                return self.get_id(input_str, input_type, locale, False)
            else:
                log.warning('\tVery low confidence' + log_output)

        if not return_ratio:
            return self._app_data['from_names'][tentative_name]['id']
        else:
            return self._app_data['from_names'][tentative_name]['id'], ratio

    def get_name(self, input_id: int, locale: str = 'en_US', retry=False):
        """
        Gets you the name for the Riot object with the given ID and locale.

        :param input_id: Riot ID of the object. Required.
        :param locale: Locale you want the name in. default is 'en_US', required.
        :param retry: will try once to reload all the data if it is not finding a match. default is True.

        :return: the matching object name. Raises a KeyError if not found.

        Examples:
            lit.get_name(21)
            lit.get_name(21, 'ko_KR')

        Note:
            Outside of a bug, (id, locale) keys should be uniques and the input type shouldn’t ever be required.
        """
        if locale not in self._app_data[self._locales_list_name]:
            self.add_locale(locale)

        try:
            return self._app_data[self._ids_dict_name][input_id, locale]['name']
        except KeyError:
            if retry:
                self.reload_app_data()
                self.get_name(input_id, locale, False)
            else:
                # Returning None instead of raising an error makes it work much better in PyCharm’s console...
                return None

    def get_translation(self, input_str: str, output_locale: str = 'en_US',
                        input_type: str = None, input_locale: str = None,
                        retry: bool = False, return_ratio=False):
        """
        Tries to get the translation of a given Riot object name matching with the loaded locals.

        :param input_str: name of the object.
        :param output_locale: the output locale. Default is 'en_US'.
        :param input_type: accepts 'champion', 'item', 'rune'. Default is None.
        :param input_locale: accepts any locale and will load it if needed. Default is None.
        :param retry: will try once to reload all the data if it is not finding a good match. Default is True.
        :return: the best translation result through fuzzy matching.
        :param return_ratio: ask for ratio as well as translation

        Examples:
            lit.get_translation('미스 포츈')
            lit.get_translation('Miss Fortune', 'ko_KR')
            lit.get_translation('MF')   # Returns the "clean name" that was fuzzy matched, can be useful too!
        """
        if input_locale is not None and input_locale not in self._app_data[self._locales_list_name]:
            self.add_locale(input_locale)
        if not return_ratio:
            return self.get_name(self.get_id(input_str, input_type, input_locale, retry), output_locale)
        else:
            returned_id, ratio = self.get_id(input_str, input_type, input_locale, retry, return_ratio)
            return self.get_name(returned_id, output_locale), ratio

    def show_available_locales(self):
        """
        Displays available locales from Riot.
        """
        pprint(self._get_json('{}cdn/languages.json'.format(self._dd_url)))

    def show_loaded_locales(self):
        """
        Displays loaded locales.
        """
        pprint(self._app_data[self._locales_list_name])

    def add_locale(self, locale: str):
        """
        Adds a new locale to the package.
        To delete locales, regenerate the data with reload_app_data().

        :param locale: locale to add
        """
        while self.updating:
            time.sleep(.1)
        self.updating = True

        if locale in self._app_data[self._locales_list_name]:
            log.warning('Trying to add an existing locale in {}. Exiting.'.format(locale))
            self.updating = False
            return

        log.info('Adding locale {}'.format(locale))

        # TODO cleanup the nicknames getter as there is code duplication between this and reload_app_data.
        executor = ThreadPoolExecutor(max_workers=1)
        future_nicknames_json = executor.submit(self._get_nicknames_json)

        # self._app_data['latest_version'] will have a value set if we loaded other locales and speeds things up
        try:
            latest_version = self._app_data[self._latest_version_name]
        except (KeyError, AttributeError):
            latest_version = self._get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]

        # We want this to finish before adding nicknames so we’re not starting it in another thread
        self._load_locale_from_server(locale, latest_version)

        self._add_nicknames(future_nicknames_json.result())

        joblib.dump(self._app_data, self._app_data_location)

        self.updating = False

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
        while self.updating:
            time.sleep(.1)
        self.updating = True

        if locales == ():
            locales = self._app_data[self._locales_list_name]

        executor = ThreadPoolExecutor(max_workers=5)

        # We start the nicknames thread directly as it doesn't need to know version number
        future_nicknames_json = executor.submit(self._get_nicknames_json)

        # Then, we reset our app_data dictionary and get the latest version by request
        self._app_data = {self._names_dict_name: {}, self._ids_dict_name: {},
                          self._locales_list_name: [],
                          self._latest_version_name:
                              self._get_json('https://ddragon.leagueoflegends.com/api/versions.json')[0]}

        for locale in locales:
            executor.submit(self._load_locale_from_server(locale, self._app_data[self._latest_version_name]))

        # This forces us to wait until all threads have completed
        executor.shutdown()

        self._add_nicknames(future_nicknames_json.result())

        joblib.dump(self._app_data, self._app_data_location)

        self.updating = False

    def _load_locale_from_server(self, locale, latest_version):
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
                data[request_type] = future.result()

        if not data:
            log.error('\tLocale "{}" not found on Riot’s server.\n'
                      'Use lit.show_available_locales() for a list of available options.'.format(locale))
            raise KeyError

        for champion_tag, champion_dict in data['champion']['data'].items():
            id_information = {
                'id': int(champion_dict['key']),
                'locale': locale,
                'id_type': 'champion',
                'name': champion_dict['name']
            }
            self._update_app_data(id_information)

        for item_id, item_dict in data['item']['data'].items():
            id_information = {
                'id': int(item_id),
                'locale': locale,
                'id_type': 'item',
                'name': item_dict['name']
            }
            self._update_app_data(id_information)

        for rune_tree in data['runesReforged']:
            for slot in rune_tree['slots']:
                for rune in slot['runes']:
                    id_information = {
                        'id': rune['id'],
                        'locale': locale,
                        'id_type': 'rune',
                        'name': rune['name']
                    }
                    self._update_app_data(id_information)

        self._app_data[self._locales_list_name].append(locale)

    def _update_app_data(self, id_info):
        # Adding the name -> ID info mapping
        self._app_data[self._names_dict_name][id_info['name']] = id_info

        # Testing if we have overlapping IDs. Doesn't happen on patch 10.5
        if (id_info['id'], id_info['locale']) in self._app_data[self._ids_dict_name]:
            log.warning('Multiple objects with ID {}'.format(id_info['id']))
            log.warning('\tExisting object: {}'.format(
                self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']]['name'],
                self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']]['id_type']))
            log.warning('\tNew object: {}/{}'.format(id_info['name'], id_info['id_type']))

        # Adding the ID, locale -> ID info mapping
        self._app_data[self._ids_dict_name][id_info['id'], id_info['locale']] = id_info

    # Requires its own function to be easily called as a thread
    def _get_nicknames_json(self):
        return self._get_json(self._nicknames_url)

    # CURRENTLY SPLIT because this requires other fields to be loaded
    # Should be moved in a single function with get nicknames in a clean async function
    def _add_nicknames(self, json):
        for locale in json:
            if locale not in self._app_data[self._locales_list_name]:
                continue
            for nickname, real_name in json[locale].items():
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
