import os
import pickle

save_folder = os.path.join(os.path.expanduser("~"), ".config", "lol_id_tools")
if not os.path.exists(save_folder):
    os.makedirs(save_folder)

data_location = os.path.join(save_folder, "loaded_data.pkl")


class LolIdCache:
    def __init__(self):
        try:
            with open(data_location, "rb") as file:
                self.loaded_data = pickle.load(file)

        except FileNotFoundError:
            self.load_data()
