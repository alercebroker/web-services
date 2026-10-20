def get_info_message(items_output):
    if len(items_output) <= 0:
        info_message = "We could not find any object with the selected filters"
    else:
        info_message = None

    return info_message
