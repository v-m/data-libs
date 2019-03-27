import os
from pathlib import Path
from contextlib import contextmanager
from typing import Dict

from revlibs.dicts import DictLoader

from .connection_model import Connection, DBConnection
from .connectors import *
from .registry import get_connector

log = get_logger()


# from common.utils import load_json_or_file, get_connection_by_name


CONNECTIONS_CONFIG_PATH = os.environ["CONNECTIONS_CONFIG"]

_AVAILABLE_CONNECTIONS_: Dict = {}


def _get_available_connections_(config_path) -> Dict[str, Connection]:
    if config_path not in _AVAILABLE_CONNECTIONS_:
        loader = DictLoader.from_path(Path(config_path))
        connections = loader.group_by_key(transformator=lambda d: Connection(d))
        _AVAILABLE_CONNECTIONS_[config_path] = connections
    else:
        connections = _AVAILABLE_CONNECTIONS_[config_path]
    if not connections:
        raise ValueError("Could not find connections")
    return connections


@contextmanager
def get_connection_by_name(
    connection_name: str, config_path: str = CONNECTIONS_CONFIG_PATH
):
    connection_config = _get_available_connections_(config_path)[connection_name]
    connector = get_connector(connection_config.type)
    connection = connector(connection_config.params)
    yield connection
    connection.close()
