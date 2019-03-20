from typing import List, Any


def as_list(obj) -> List[Any]:
    if isinstance(obj, list):
        return obj
    return [obj]


def extend(l: List, desired_length: int) -> List:
    return l + [l[-1]] * (desired_length - len(l))
