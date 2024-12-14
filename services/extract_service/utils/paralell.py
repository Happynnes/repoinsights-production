from concurrent.futures import ThreadPoolExecutor, as_completed


def run_in_parallel(function, args_list, max_workers=5):
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(function, *args) for args in args_list]
        for future in as_completed(futures):
            results.append(future.result())
    return results
