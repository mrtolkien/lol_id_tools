from concurrent.futures.thread import ThreadPoolExecutor
import lol_id_tools


def test_parallel_updates():
    # TODO Rewrite this test once parallel update is cleaned up
    # Just checking nothing crashes
    with ThreadPoolExecutor() as executor:
        for i in range(0, 5):
            executor.submit(lol_id_tools.get_id, "nonsense", 100, retry=True)
