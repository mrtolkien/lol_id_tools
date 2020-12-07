import os

import lol_id_tools

# Removing any cache we might have
try:
    print("Removing local lol_id_tools cache")
    os.remove(lol_id_tools.getter_functions.lod.data_location)
except FileNotFoundError:
    pass
