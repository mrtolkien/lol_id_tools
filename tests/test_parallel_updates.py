from concurrent.futures.thread import ThreadPoolExecutor
import lol_id_tools


def test_parallel_updates():
    # Just checking nothing crashes
    # TODO Better testing?
    with ThreadPoolExecutor() as executor:
        for i in range(0, 10):
            executor.submit(lol_id_tools.get_id, "nonsense", 100, retry=True)
