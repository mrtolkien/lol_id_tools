import os
import pickle
from collections import defaultdict
from typing import Dict
from lol_id_tools.local_data_parser import load_nickname_data, NameInfo
import asyncio
import logging
import aiohttp
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
    _riot_data = None

    @property
    def riot_data(self):
        if self._riot_data is None:
            self._riot_data = self.unpickle_riot_data()
            self.recalculate_names_to_id()
        return self._riot_data

    # Pickling it to minimise web requests
    def pickle_riot_data(self):
        with open(self.data_location, "wb+") as file:
            pickle.dump(self.riot_data, file)

    def unpickle_riot_data(self) -> Dict[str, Dict[int, Dict[str, str]]]:
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
        for locale in self.riot_data:
            # First we write the info from riot_data
            for id_ in self.riot_data[locale]:
                for object_type in self.riot_data[locale][id_]:
                    name = self.riot_data[locale][id_][object_type]
                    self._names_to_id[name.lower()] = NameInfo(id_, object_type, locale)

            # Then we write the info from nicknames_data if we have loaded the locale
            if locale in self.nickname_data:
                for nickname in self.nickname_data[locale]:
                    clean_name = self.nickname_data[locale][nickname]
                    object_id = None
                    object_type = None
                    for id_ in self.riot_data[locale]:
                        for object_type in self.riot_data[locale][id_]:
                            if self.riot_data[locale][id_][object_type] == clean_name:
                                object_id = id_
                                break

                    self._names_to_id[nickname.lower()] = NameInfo(object_id, object_type, locale)

    # Defining another property for more readable code
    @property
    def loaded_locales(self):
        return [k for k in self.riot_data]

    async def load_locale(self, locale, latest_version=None):
        if not latest_version:
            latest_version = await self.get_latest_version()

        self.riot_data[locale] = defaultdict(dict)

        async with aiohttp.ClientSession() as http_session:
            coroutines = [
                load_riot_objects(self.riot_data, http_session, latest_version, locale, object_type)
                for object_type in ["champion", "runeReforged", "item", "summoner"]
            ]
            coroutines.append(parse_cdragon_runes(self.riot_data, http_session, locale))

            await asyncio.wait([asyncio.create_task(c) for c in coroutines])

        self.recalculate_names_to_id()
        self.pickle_riot_data()

    async def reload_all_locales(self):
        self._names_to_id = {}
        latest_version = await self.get_latest_version()
        await asyncio.wait(
            [asyncio.create_task(self.load_locale(locale, latest_version)) for locale in self.loaded_locales]
        )

    @staticmethod
    async def get_latest_version():
        async with aiohttp.ClientSession() as http_session:
            url = "https://ddragon.leagueoflegends.com/api/versions.json"
            async with http_session.get(url) as response:
                logging.debug(f"Querying {url}")
                data = await response.json()
            return data[0]

    def delete_local_data(self):
        """Mainly used for testing purposes"""
        try:
            os.remove(self.data_location)
        except FileNotFoundError:
            pass
