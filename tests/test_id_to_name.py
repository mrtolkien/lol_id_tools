import pytest
import lol_id_tools


@pytest.mark.parametrize(
    "english_output,input_id,object_type",
    [
        # Testing champions
        ("Miss Fortune", 21, "CHAMPION"),
        ("Miss Fortune", 21, "champion"),
        # Testing items
        ("Blade of The Ruined King", 3153, "ITEM"),
        ("Trinity Force", 3078, "ITEM"),
        # Testing Ornn upgrade
        ("Syzygy", 7001, "ITEM"),
        # Testing old jungle items
        ("Stalker's Blade - Warrior", 1400, "ITEM"),
        # Testing S10 item
        ("Athene's Unholy Grail ", 3174, "ITEM"),
        # Testing runes
        ("Aftershock", 8439, "RUNE"),
        ("Grasp of the Undying", 8437, "RUNE"),
        # Testing perks
        ("CDRScaling", 5007, "RUNE"),
        # Testing tree name
        ("Domination", 8100, "RUNE"),
        # Testing summoner spell
        ("Barrier", 21, "SUMMONER_SPELL"),
        ("Barrier", 21, "summoner_spell"),
    ],
)
def test_english(english_output, input_id, object_type):
    assert lol_id_tools.get_name(input_id, object_type=object_type) == english_output
