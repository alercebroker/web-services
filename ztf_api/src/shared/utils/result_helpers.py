from returns.pipeline import is_successful


def get_failure_from_list(results_list):
    # returns the first failure from a list of results
    for result in results_list:
        if not is_successful(result):
            return result
    return None
