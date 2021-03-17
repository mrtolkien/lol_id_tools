import os
import requests
import pickle
import logging

from concurrent.futures.thread import ThreadPoolExecutor
from collections import defaultdict
from typing import Dict

from lol_id_tools.local_data_parser import load_nickname_data, NameInfo
from lol_id_tools.data_parser import load_riot_objects, parse_cdragon_runes

save_folder = os.path.join(os.path.expanduser("~"), ".config", "lol_id_tools")
if not os.path.exists(save_folder):
    os.makedirs(save_folder)


class LolObjectData:
    """A class handling data about LoL objects.

    Everything is class-wide to make sure multiple programs on the same machine use the same data.
    """

    data_location = os.path.join(save_folder, "loaded_data.pkl")

    # riot_data represents all the data that we got from Riot and is ghost loaded for module loading efficiency
    # it is used directly for id -> name matching
    # riot_data[locale][id][object_type][NameInfo]
    _loaded_data = None

    @property
    def loaded_data(self):
        if self._loaded_data is None:
            self._loaded_data = self.unpickle_loaded_data()
            self.recalculate_names_to_id()
        return self._loaded_data

    # Pickling it to minimise web requests
    def pickle_loaded_data(self):
        with open(self.data_location, "wb+") as file:
            pickle.dump(self.loaded_data, file)

    def unpickle_loaded_data(self) -> Dict[str, Dict[int, Dict[str, str]]]:
        try:
            with open(self.data_location, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            return {}

    # nicknames_data is a dictionary representation of /locale_data/nicknames.json
    # It is not meant to be used directly as names_to_id is what we use for name -> id
    # nickname_data[locale][nickname][clean_name]
    _nickname_data = None

    @property
    def nickname_data(self):
        if self._nickname_data is None:
            self._nickname_data = load_nickname_data()
        return self._nickname_data

    # names_to_id is a flipped dictionary that holds names from both riot_data and nickname_data
    # names_to_id[name][IdInfo]
    _names_to_id: Dict[str, NameInfo] = {}

    @property
    def names_to_id(self):
        if not self._names_to_id:
            self.recalculate_names_to_id()
        return self._names_to_id

    # get_id() relies a lot on item names, so we also define a reversed dict with lowercase names as property
    def recalculate_names_to_id(self):
        for locale in self.loaded_data:
            # First we write the info from riot_data
            for id_ in self.loaded_data[locale]:
                for object_type in self.loaded_data[locale][id_]:
                    name = self.loaded_data[locale][id_][object_type]
                    self._names_to_id[name.lower()] = NameInfo(id_, object_type, locale)

            # Then we write the info from nicknames_data if we have loaded the locale
            if locale in self.nickname_data:
                for nickname in self.nickname_data[locale]:
                    clean_name = self.nickname_data[locale][nickname]
                    object_id = None
                    object_type = None
                    for id_ in self.loaded_data[locale]:
                        for object_type in self.loaded_data[locale][id_]:
                            if self.loaded_data[locale][id_][object_type] == clean_name:
                                object_id = id_
                                break

                    self._names_to_id[nickname.lower()] = NameInfo(object_id, object_type, locale)

    # Defining another property for more readable code
    @property
    def loaded_locales(self):
        return [k for k in self.loaded_data]

    def load_locale(self, locale, latest_version=None):
        if not latest_version:
            latest_version = self.get_latest_version()

        self.loaded_data[locale] = defaultdict(dict)

        with ThreadPoolExecutor() as executor:
            # TODO Just call different functions?
            for object_type in ["champion", "runesReforged", "item", "summoner"]:
                executor.submit(load_riot_objects, self.loaded_data, latest_version, locale, object_type)

            # Cdragon is different enough that it’s handled by itself
            executor.submit(parse_cdragon_runes, self.loaded_data, locale)

        self.recalculate_names_to_id()
        self.pickle_loaded_data()

    def reload_all_locales(self):
        self._names_to_id = {}
        latest_version = self.get_latest_version()

        with ThreadPoolExecutor() as executor:
            for locale in self.loaded_locales:
                executor.submit(self.load_locale, locale, latest_version)

    @staticmethod
    def get_latest_version():
        """Gets the latest version available on ddragon.
        """
        url = "https://ddragon.leagueoflegends.com/api/versions.json"

        response = requests.get(url)
        logging.debug(f"Querying {url}")

        data = response.json()
        return data[0]

    def delete_local_data(self):
        """Mainly used for testing purposes
        """
        try:
            os.remove(self.data_location)
        except FileNotFoundError:
            pass
