import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "test_input,object_id",
    [
        # Testing champions
        ("Miss Fortune", 21),
        ("Annie", 1),
        # Testing items
        ("Blade of the ruined king", 3153),
        ("Trinity Force", 3078),
        ("Kalista's Black Spear", 3600),
        ("Your Cut", 3400),
        # Testing Ornn upgrade
        ("Syzygy", 7001),
        # Testing old jungle items
        ("Stalker's Blade - Warrior", 1400),
        # Testing S10 item
        ("Athene's Unholy Grail ", 3174),
        # Testing S9 item
        ("Ancient Coin", 3301),
        # Testing S8 item
        ("Banner of Command", 3060),
        # Testing S7 item
        ("Abyssal Scepter", 3001),
        # Testing runes
        ("Aftershock", 8439),
        ("Grasp of the undying", 8437),
        # Testing perks
        ("CDRScaling", 5007),
        # Testing tree name
        ("Domination", 8100),
        # Testing summoner spell
        ("Barrier", 21),
    ],
)
def test_english(test_input, object_id):
    assert lol_id_tools.get_id(test_input) == object_id


@pytest.mark.parametrize(
    "test_input,object_id",
    [
        # Testing champions
        ("MF", 21),
        ("J4", 59),
        # Testing items
        ("botrk", 3153),
        ("QSS", 3140),
    ],
)
def test_english_nicknames(test_input, object_id):
    assert lol_id_tools.get_id(test_input) == object_id


# TODO test_korean
