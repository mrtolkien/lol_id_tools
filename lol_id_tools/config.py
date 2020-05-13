import json
import logging
import os

config_folder = os.path.join(os.path.expanduser("~"), '.config', 'lol_id_tools')

if not os.path.exists(config_folder):
    os.mkdir(config_folder)

data_location = os.path.join(config_folder, 'lol_id_tools.db')
config_location = os.path.join(config_folder, 'config.json')

try:
    with open(config_location) as config_file:
        configuration = json.load(config_file)
except FileNotFoundError:
    logging.info(f'Creating default lol_id_tools configuration file at {config_location}')
    configuration = {'nicknames_url': 'https://raw.githubusercontent.com/mrtolkien/'
                                      'lol_id_tools/master/data/nicknames.json',
                     'locales': ['en_US']}
    with open(config_location, 'w+') as config_file:
        json.dump(configuration, config_file, indent=4)
