from returns.result import Success, Failure

# helper functions, maybe unnecesary
def is_success(result):
    return isinstance(result, Success)

def is_failure(result):
    return isinstance(result, Failure)

def get_failure_from_list(results_list):
    # returns the first failure from a list of results
    for result in results_list:
        if is_failure(result):
            return result
    return None
