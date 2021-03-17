import os
import lol_id_tools

try:
    os.remove(lol_id_tools.lol_id_tools.lod.data_location)
except FileNotFoundError:
    pass
