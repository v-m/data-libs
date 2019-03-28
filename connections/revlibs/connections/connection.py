""" Standard connection interface."""
from contextlib import contextmanager

from revlibs.connections import config


class ConnectExasol:
    pass


class ConnectPostgres:
    def __init__(self, cfg):
        self.name = cfg.name

    def close(self):
        print("success")


_CONNECTORS = {"exasol": ConnectExasol, "postgres": ConnectPostgres}


@contextmanager
def get(name):
    """ Grab a connection."""
    cfg = config.load(name)
    obj = _CONNECTORS[cfg.flavour]
    connector = obj(cfg)
    yield connector
    connector.close()
