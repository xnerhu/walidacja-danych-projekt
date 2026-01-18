def as_array(value):
    if isinstance(value, list):
        return value
    return [value]


def index_of(l, value):
    try:
        return l.index(value)
    except ValueError:
        return -1


def last_index_of(l, value):
    try:
        return len(l) - l[::-1].index(value) - 1
    except ValueError:
        return -1


def flatten(l):
    items = []
    for item in l:
        if isinstance(item, list):
            items.extend(flatten(item))
        else:
            items.append(item)
    return items


def unique(l):
    return list(set(l))


def to_chunks(arr: list, chunk_size: int) -> list:
    """Splits a list into chunks of a specified size."""
    return [arr[i : i + chunk_size] for i in range(0, len(arr), chunk_size)]
