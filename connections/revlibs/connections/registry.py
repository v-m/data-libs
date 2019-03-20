from typing import Any, Dict, Callable, Optional
from .connection_model import DBConnection

_AVAILABLE_CONNECTORS_: Dict[str, Callable[[DBConnection], Any]] = {}


def register_connector(connection_type_name: str):
    """ 
        This is a decorator method for adding a method into registry
    """

    def d(func: Callable[[DBConnection], Any]):
        global _AVAILABLE_CONNECTORS_
        _AVAILABLE_CONNECTORS_[connection_type_name] = func
        return func

    return d


def get_connector(connection_type_name: str) -> Callable[[DBConnection], Any]:
    return _AVAILABLE_CONNECTORS_[connection_type_name]
